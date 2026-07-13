@echo off
REM =============================================================================
REM Arranca el Celery Beat en Windows (primer plano) — el "reloj" que dispara
REM importar_zafiro cada 30 minutos segun CELERY_BEAT_SCHEDULE.
REM Deja esta ventana abierta mientras quieras que el beat corra.
REM
REM Solo debe haber UNA instancia de beat corriendo en todo el sistema (Linux
REM o Windows, no ambos a la vez) para no duplicar el schedule.
REM =============================================================================
setlocal

set "ROOT=%~dp0"

call "%ROOT%venv\Scripts\activate.bat"
cd /d "%ROOT%"

celery -A eje_central_back beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler

endlocal
