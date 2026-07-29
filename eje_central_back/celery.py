import logging
import os

from celery import Celery
from celery.signals import worker_ready

# Apunta al módulo de settings de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eje_central_back.settings")

app = Celery("eje_central_back")

# Lee la configuración de Django usando el namespace CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Descubre automáticamente tasks.py en cada app de INSTALLED_APPS
app.autodiscover_tasks()

logger = logging.getLogger(__name__)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


@worker_ready.connect
def recuperar_zafiro_pendiente(sender, **kwargs):
    """
    Al arrancar este Worker, revisa si quedó alguna bitácora de ZAFIRO en
    estado RUNNING de una corrida anterior que murió a medias (crash del
    worker, corte de luz/red, etc.). Como el lock distribuido en Redis
    garantiza que solo corre una instancia de `importar_zafiro` a la vez,
    cualquier bitácora en RUNNING en este punto es necesariamente huérfana
    de una corrida que ya no existe.

    Marca esas bitácoras como ERROR, libera el lock (por si quedó tomado) y
    relanza `importar_zafiro` de inmediato para recuperar la sincronización
    sin esperar al siguiente slot de 30 minutos.
    """
    import redis as redis_lib
    from django.conf import settings as dj_settings

    from plantilla.models import ZafiroBitacora
    from plantilla.tasks import importar_zafiro

    pendientes = ZafiroBitacora.objects.filter(status="RUNNING")
    total = pendientes.count()

    r = redis_lib.Redis.from_url(dj_settings.CELERY_BROKER_URL)
    lock_previo = r.delete("lock:importar_zafiro")

    if total == 0:
        if lock_previo:
            logger.warning(
                "Lock de importar_zafiro liberado al arrancar el Worker "
                "(no había bitácora RUNNING pendiente, pero el lock seguía tomado)."
            )
        return

    pendientes.update(
        status="ERROR",
        error_message="Interrumpida: el Worker se reinició antes de que la tarea terminara.",
    )

    logger.warning(
        "Recuperación al arrancar: %s bitácora(s) de ZAFIRO quedaron en RUNNING "
        "de una corrida anterior. Marcadas como ERROR, lock liberado, "
        "relanzando importar_zafiro.",
        total,
    )
    importar_zafiro.delay()
