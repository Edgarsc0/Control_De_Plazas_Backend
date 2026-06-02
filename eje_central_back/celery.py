import os

from celery import Celery

# Apunta al módulo de settings de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eje_central_back.settings")

app = Celery("eje_central_back")

# Lee la configuración de Django usando el namespace CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Descubre automáticamente tasks.py en cada app de INSTALLED_APPS
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
