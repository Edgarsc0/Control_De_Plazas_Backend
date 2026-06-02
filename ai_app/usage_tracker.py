# ai_app/usage_tracker.py

import os
import json
import threading
from datetime import datetime, timezone
from django.conf import settings

# Archivo JSON para almacenar estadísticas de uso de la API key
USAGE_FILE = os.path.join(settings.BASE_DIR, "ai_usage_stats.json")
_usage_lock = threading.Lock()

# Límites conocidos por modelo (basados en la documentación de Google AI Studio)
MODEL_LIMITS = {
    "gemini-3.1-flash-lite":  {"rpd": 500,  "rpm": 30,  "tpm": 250_000,  "label": "3.1 Flash Lite"},
    "gemini-3.5-flash":       {"rpd": 20,   "rpm": 10,  "tpm": 250_000,  "label": "3.5 Flash"},
    "gemini-2.5-flash":       {"rpd": 20,   "rpm": 10,  "tpm": 250_000,  "label": "2.5 Flash"},
    "gemma-4-31b":            {"rpd": 1500, "rpm": 30,  "tpm": 15_000,   "label": "Gemma 4 31B"},
    "gemini-2.5-flash-preview-05-20": {"rpd": 50, "rpm": 10, "tpm": 250_000, "label": "2.5 Flash Preview"},
}

def _load_usage() -> dict:
    """Carga el archivo de estadísticas de uso. Thread-safe."""
    if not os.path.exists(USAGE_FILE):
        return {}
    try:
        with open(USAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def _save_usage(data: dict) -> None:
    """Guarda el archivo de estadísticas de uso. Thread-safe."""
    os.makedirs(os.path.dirname(USAGE_FILE), exist_ok=True)
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def record_usage(model: str, usage_metadata) -> None:
    """
    Registra el uso de tokens y requests para un modelo dado.
    Almacena estadísticas por día y por hora (ventana de 1h).
    """
    now = datetime.now(timezone.utc)
    day_key = now.strftime("%Y-%m-%d")       # ej: "2026-05-29"
    hour_key = now.strftime("%Y-%m-%dT%H")  # ej: "2026-05-29T14"

    prompt_tokens = (usage_metadata.prompt_token_count or 0) if usage_metadata else 0
    output_tokens = (usage_metadata.candidates_token_count or 0) if usage_metadata else 0
    thought_tokens = (usage_metadata.thoughts_token_count or 0) if usage_metadata else 0
    total_tokens = (usage_metadata.total_token_count or 0) if usage_metadata else 0

    with _usage_lock:
        data = _load_usage()

        # Inicializar estructura si no existe
        if model not in data:
            data[model] = {"daily": {}, "hourly": {}}

        # ── Estadísticas diarias ──
        if day_key not in data[model]["daily"]:
            data[model]["daily"][day_key] = {
                "requests": 0, "prompt_tokens": 0,
                "output_tokens": 0, "thought_tokens": 0, "total_tokens": 0,
            }
        d = data[model]["daily"][day_key]
        d["requests"] += 1
        d["prompt_tokens"] += prompt_tokens
        d["output_tokens"] += output_tokens
        d["thought_tokens"] += thought_tokens
        d["total_tokens"] += total_tokens

        # ── Estadísticas por hora ──
        if hour_key not in data[model]["hourly"]:
            data[model]["hourly"][hour_key] = {
                "requests": 0, "total_tokens": 0,
            }
        h = data[model]["hourly"][hour_key]
        h["requests"] += 1
        h["total_tokens"] += total_tokens

        # Mantener solo los últimos 30 días y 48 horas para no crecer indefinidamente
        all_days = sorted(data[model]["daily"].keys())
        if len(all_days) > 30:
            for old_day in all_days[:-30]:
                del data[model]["daily"][old_day]

        all_hours = sorted(data[model]["hourly"].keys())
        if len(all_hours) > 48:
            for old_hour in all_hours[:-48]:
                del data[model]["hourly"][old_hour]

        _save_usage(data)
