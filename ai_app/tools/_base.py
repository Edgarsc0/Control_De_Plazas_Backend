import logging
import time
import functools
from django.core.cache import cache
from django.db import connection
from django.db.models import Q
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.db.utils import OperationalError, ProgrammingError

logger = logging.getLogger("ai_app.tools")

MAX_RESULTS_DEFAULT = 10
MAX_RESULTS_ABSOLUTE = 50

def tool_handler(max_output_chars: int = 6000):
    """
    Decorator that wraps tool functions to provide:
    - Robust error handling returning clean error messages to the LLM (no stack traces)
    - Execution timing and status logging
    - Automatic output truncation if limits are exceeded
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            tool_name = func.__name__
            logger.info(f"Running tool {tool_name} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                logger.info(f"Tool {tool_name} completed in {duration:.2f}ms")
                
                if not isinstance(result, str):
                    result = str(result)
                
                if len(result) > max_output_chars:
                    trunc_msg = f"\n\n⚠️... [Output truncado. Mostrando {max_output_chars} de {len(result)} caracteres. Añada más filtros para reducir la búsqueda] ..."
                    result = result[:max_output_chars] + trunc_msg
                
                return result
            except ObjectDoesNotExist as e:
                logger.error(f"Error in tool {tool_name}: ObjectDoesNotExist - {str(e)}")
                return f"❌ Error: El registro solicitado no existe. Detalles: {str(e)}"
            except FieldError as e:
                logger.error(f"Error in tool {tool_name}: FieldError - {str(e)}")
                return f"❌ Error de Filtro: Uno de los campos especificados no existe en el modelo. Detalles: {str(e)}"
            except (OperationalError, ProgrammingError) as e:
                logger.error(f"Error in tool {tool_name}: DatabaseError - {str(e)}")
                return f"❌ Error de Base de Datos: Ocurrió un problema al ejecutar la consulta. Detalles: {str(e)}"
            except Exception as e:
                logger.error(f"Unexpected error in tool {tool_name}: {str(e)}", exc_info=True)
                return f"❌ Error inesperado al ejecutar {tool_name}: {str(e)}"
        return wrapper
    return decorator

def _aplicar_filtros_avanzados(queryset, filtros: list[dict]):
    """
    Aplica filtros dinámicos combinados (AND) a un queryset de Django.
    Valida campos contra el modelo real y normaliza operadores comunes del LLM.
    """
    if not filtros or not isinstance(filtros, list):
        return queryset

    q_objects = Q()
    filtros_aplicados = []
    
    for f in filtros:
        if not isinstance(f, dict):
            continue
            
        field = f.get("field")
        op = f.get("op") or f.get("operator") or "exact"
        val = f.get("value")
        
        if not field or val is None:
            continue
            
        # Validar si el campo existe en el modelo
        model = queryset.model
        clean_field = field.split('__')[0] # Manejar posibles relaciones de Django si se dan
        if not hasattr(model, clean_field):
            # Intentar verificar si es un campo de base de datos directamente o buscar en campos de meta
            meta_fields = [field.name for field in model._meta.get_fields()]
            if clean_field not in meta_fields:
                logger.warning(f"Campo {clean_field} no existe en el modelo {model.__name__}. Se intentará aplicar de todos modos.")
                # No descartamos inmediatamente, por si es un campo dinámico o anotado.

        # Normalizar operadores
        op = op.lower()
        if op in ("eq", "=", "equal"):
            op = "exact"
        elif op in ("ne", "!=", "neq", "exclude"):
            # Exclude requiere un tratamiento especial, lo simularemos negando la Q() o usaremos exclude
            op = "exact"
            # Manejamos != como negación
            lookup = f"{field}__{op}" if op != "exact" else field
            q_objects &= ~Q(**{lookup: val})
            filtros_aplicados.append(f"NOT {field}={val}")
            continue
        elif op == "like":
            if isinstance(val, str) and val.endswith("%") and not val.startswith("%"):
                op = "startswith"
                val = val.rstrip("%")
            elif isinstance(val, str) and val.startswith("%") and not val.endswith("%"):
                op = "endswith"
                val = val.lstrip("%")
            else:
                op = "icontains"
                if isinstance(val, str):
                    val = val.strip("%")
        elif op in ("contains", "contain"):
            op = "icontains"
        elif op in ("greater than", "greater_than"):
            op = "gt"
        elif op in ("less than", "less_than"):
            op = "lt"
        elif op in ("greater or equal", "gteq"):
            op = "gte"
        elif op in ("less or equal", "lteq"):
            op = "lte"

        lookup = f"{field}__{op}" if op != "exact" else field
        q_objects &= Q(**{lookup: val})
        filtros_aplicados.append(f"{lookup}={val}")

    if filtros_aplicados:
        logger.info(f"Filtros aplicados en {queryset.model.__name__}: {', '.join(filtros_aplicados)}")

    return queryset.filter(q_objects)

def _get_latest_mov_pos_ids() -> list[int]:
    """
    Retorna los IDs del registro más reciente de cada plaza en MOV_POS.
    Almacena el resultado en caché por 2 minutos (120s) para evitar consultas pesadas.
    """
    cache_key = "latest_mov_pos_ids"
    cached_ids = cache.get(cache_key)
    if cached_ids is not None:
        return cached_ids

    query = """
        SELECT id FROM (
            SELECT id, ROW_NUMBER() OVER (
                PARTITION BY `Nº Pos Actual`
                ORDER BY `F Efva` DESC, `Fecha Captura` DESC, `F/H Últ Actz` DESC, id DESC
            ) as rn
            FROM MOV_POS
        ) ranked WHERE rn = 1
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        ids = [row[0] for row in cursor.fetchall()]
        
    cache.set(cache_key, ids, 120)
    return ids

def _format_record(data_dict: dict, campos_prioritarios: list[str] = None) -> str:
    """
    Formatea un registro individual convirtiendo un diccionario a texto legible,
    poniendo primero los campos prioritarios si se especifican, y omitiendo vacíos.
    """
    lines = []
    keys = list(data_dict.keys())
    
    if campos_prioritarios:
        # Filtrar campos prioritarios que existen en el diccionario
        for cp in campos_prioritarios:
            if cp in data_dict:
                val = data_dict[cp]
                if val not in (None, "", "nan", "NaN"):
                    lines.append(f"  - {cp.replace('_', ' ').title()}: {val}")
                if cp in keys:
                    keys.remove(cp)

    # Resto de los campos
    for k in keys:
        val = data_dict[k]
        if val not in (None, "", "nan", "NaN"):
            lines.append(f"  - {k.replace('_', ' ').title()}: {val}")

    return "\n".join(lines)

def _build_interop_header(emoji: str, label: str, total: int, showing: int, keys_found: dict = None) -> str:
    """
    Genera un header estandarizado para interconectividad y Chain-of-Thought (CoT).
    """
    header = f"{emoji} {label} — Total: {total} | Mostrando: {showing}\n"
    if keys_found:
        for k, v in keys_found.items():
            if v:
                # Si es lista de valores, los unimos por coma. Máximo 10 para no saturar el header.
                val_list = [str(x) for x in v]
                joined = ", ".join(val_list[:15])
                if len(val_list) > 15:
                    joined += ", ..."
                header += f"🔑 {k}: {joined}\n"
    header += "════════════════════════════════════\n"
    return header
