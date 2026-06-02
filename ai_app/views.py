import os
import threading
from datetime import datetime, timezone

from asgiref.sync import async_to_sync
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from google.antigravity import Agent, GenerationConfig, LocalAgentConfig

# Importar componentes modulares
from .tools import TOOL_REGISTRY
from .system_prompt import SYSTEM_INSTRUCTIONS
from .usage_tracker import MODEL_LIMITS, _load_usage, _usage_lock, record_usage

# Directorio persistente para sesiones de IA
SESSIONS_DIR = os.path.join(settings.BASE_DIR, "ai_sessions")

class AntigravityChatView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        prompt = request.data.get("prompt")
        model_name = request.data.get("model", "gemini-2.5-flash-preview-05-20")
        history = request.data.get("history", [])

        if not prompt:
            return Response(
                {"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST
            )
            
        api_key = os.environ.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return Response(
                {"error": "GEMINI_API_KEY not configured in environment"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ── Construir contexto de conversación ────────────────────────────────
        # Inyectamos el historial directamente en el prompt como texto plano.
        MAX_HISTORY_TURNS = 6  # últimos 6 intercambios
        prompt_con_contexto = prompt

        if history:
            turns_recientes = history[-(MAX_HISTORY_TURNS * 2):]
            lineas = []
            for msg in turns_recientes:
                role = msg.get("role", "")
                content = (msg.get("content") or "").strip()
                if not content:
                    continue
                if role == "user":
                    lineas.append(f"USUARIO: {content}")
                elif role == "bot":
                    # Truncar respuestas del bot para optimizar tokens
                    preview = content[:800] + "…" if len(content) > 800 else content
                    lineas.append(f"ASISTENTE: {preview}")

            if lineas:
                contexto_str = "\n".join(lineas)
                prompt_con_contexto = (
                    f"[HISTORIAL DE CONVERSACIÓN RECIENTE]\n"
                    f"{contexto_str}\n\n"
                    f"[NUEVA PREGUNTA DEL USUARIO]\n"
                    f"{prompt}"
                )

        def get_antigravity_response():
            gen_config = GenerationConfig(max_output_tokens=8192, temperature=0.1)
            config = LocalAgentConfig(
                model=model_name,
                generation=gen_config,
                save_dir=SESSIONS_DIR,
                tools=TOOL_REGISTRY,
                system_instructions=SYSTEM_INSTRUCTIONS,
            )

            async def run_agent():
                async with Agent(config) as agent:
                    response_obj = await agent.chat(prompt_con_contexto)
                    text = await response_obj.text()
                    usage = response_obj.usage_metadata
                    return text, usage

            return async_to_sync(run_agent)()

        try:
            text, usage = get_antigravity_response()
            # Guardar estadísticas de uso en background
            threading.Thread(
                target=record_usage, args=(model_name, usage), daemon=True
            ).start()

            # Serializar usage_metadata para el frontend
            usage_data = None
            if usage:
                usage_data = {
                    "prompt_tokens": usage.prompt_token_count or 0,
                    "output_tokens": usage.candidates_token_count or 0,
                    "thought_tokens": usage.thoughts_token_count or 0,
                    "total_tokens": usage.total_token_count or 0,
                }

            return Response({"response": text, "usage": usage_data})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AIUsageStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Retorna las estadísticas de uso de la API key de Gemini.
        """
        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")
        current_hour = now.strftime("%Y-%m-%dT%H")

        with _usage_lock:
            data = _load_usage()

        result = {
            "timestamp": now.isoformat(),
            "models": {},
            "summary": {
                "total_requests_today": 0,
                "total_tokens_today": 0,
                "models_used_today": [],
            },
        }

        for model, model_data in data.items():
            limits = MODEL_LIMITS.get(model, {"rpd": None, "rpm": None, "tpm": None, "label": model})
            daily = model_data.get("daily", {})
            hourly = model_data.get("hourly", {})

            # Stats de hoy
            today_stats = daily.get(today, {
                "requests": 0, "prompt_tokens": 0,
                "output_tokens": 0, "thought_tokens": 0, "total_tokens": 0,
            })

            # Stats de la hora actual
            hour_stats = hourly.get(current_hour, {"requests": 0, "total_tokens": 0})

            # Historial de los últimos 7 días
            last_7_days = []
            for i in range(6, -1, -1):
                from datetime import timedelta
                day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
                day_data = daily.get(day, {"requests": 0, "total_tokens": 0})
                last_7_days.append({
                    "date": day,
                    "requests": day_data.get("requests", 0),
                    "total_tokens": day_data.get("total_tokens", 0),
                })

            # Últimas 24 horas
            last_24h = []
            for i in range(23, -1, -1):
                from datetime import timedelta
                h = (now - timedelta(hours=i)).strftime("%Y-%m-%dT%H")
                h_data = hourly.get(h, {"requests": 0, "total_tokens": 0})
                last_24h.append({
                    "hour": h,
                    "requests": h_data.get("requests", 0),
                    "total_tokens": h_data.get("total_tokens", 0),
                })

            # Porcentajes de uso del día
            rpd_used = today_stats.get("requests", 0)
            tpd_used = today_stats.get("total_tokens", 0)
            rpd_limit = limits.get("rpd")
            tpm_limit = limits.get("tpm")

            rpd_pct = round((rpd_used / rpd_limit) * 100, 1) if rpd_limit else None
            tpd_limit_approx = tpm_limit * 1440 if tpm_limit else None
            tpd_pct = round((tpd_used / tpd_limit_approx) * 100, 2) if tpd_limit_approx else None

            result["models"][model] = {
                "label": limits["label"],
                "limits": {
                    "rpd": limits.get("rpd"),
                    "rpm": limits.get("rpm"),
                    "tpm": limits.get("tpm"),
                },
                "today": {
                    **today_stats,
                    "rpd_used": rpd_used,
                    "rpd_pct": rpd_pct,
                    "tpd_pct": tpd_pct,
                },
                "current_hour": hour_stats,
                "last_7_days": last_7_days,
                "last_24h": last_24h,
            }

            if today_stats.get("requests", 0) > 0:
                result["summary"]["models_used_today"].append(model)
                result["summary"]["total_requests_today"] += today_stats.get("requests", 0)
                result["summary"]["total_tokens_today"] += today_stats.get("total_tokens", 0)

        return Response(result)
