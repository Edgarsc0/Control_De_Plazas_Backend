@echo off
REM Arranca worker y beat, cada uno en su propia ventana.
REM Si el beat ya corre en el servidor Linux, usa unicamente start_worker.bat aqui.
set "ROOT=%~dp0"

start "Celery Worker" cmd /k "%ROOT%start_worker.bat"
start "Celery Beat" cmd /k "%ROOT%start_beat.bat"
