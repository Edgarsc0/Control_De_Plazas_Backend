@echo off
REM =============================================================================
REM Arranca el Celery Worker en Windows (primer plano).
REM Deja esta ventana abierta mientras quieras que el worker corra.
REM
REM NOTA WINDOWS: el pool "prefork" (default de Celery) usa os.fork(), que no
REM existe en Windows. Por eso usamos --pool=solo (un solo hilo, sin
REM concurrencia). No es un problema aqui: importar_zafiro usa un lock
REM distribuido en Redis que ya garantiza una sola ejecucion a la vez.
REM =============================================================================
setlocal

set "ROOT=%~dp0"

call "%ROOT%venv\Scripts\activate.bat"
cd /d "%ROOT%"

celery -A eje_central_back worker --pool=solo --loglevel=info

endlocal
