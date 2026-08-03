@echo off
REM =============================================================================
REM Corre UNICAMENTE poblado_credenciales.js en modo visible (no headless), para
REM probarlo a mano y ver en pantalla exactamente donde se atora si se atora.
REM No toca Celery/Django ni importar_zafiro para nada -- es solo el script de
REM scraping, aislado.
REM
REM Uso:
REM   probar_poblado_credenciales.bat
REM   probar_poblado_credenciales.bat "D:\otra\carpeta\de\descargas"
REM
REM Si no se pasa carpeta, usa la misma que ZAFIRO_DOWNLOAD_DIR en el .env
REM (C:\ZafiroDescargas) -- no hay conflicto con los CSV de ZAFIRO porque el
REM archivo resultante se renombra a poblado_credenciales.<ext>.
REM =============================================================================
setlocal

set "SCRIPT_DIR=%~dp0"
set "DOWNLOAD_DIR=%~1"
if "%DOWNLOAD_DIR%"=="" set "DOWNLOAD_DIR=C:\ZafiroDescargas"

cd /d "%SCRIPT_DIR%"

if not exist "node_modules" (
    echo [poblado_credenciales] No existe node_modules en esta carpeta, instalando dependencias...
    call npm install
    if errorlevel 1 (
        echo [poblado_credenciales] npm install fallo. Revisa que Node.js este instalado y en el PATH.
        pause
        exit /b 1
    )
)

echo [poblado_credenciales] Carpeta de descarga: %DOWNLOAD_DIR%
echo [poblado_credenciales] Modo: VISIBLE (headless=0) -- se abrira una ventana de Edge.
echo.

node poblado_credenciales.js "%DOWNLOAD_DIR%" 0

echo.
echo [poblado_credenciales] Proceso terminado (codigo de salida: %errorlevel%).
if not "%errorlevel%"=="0" (
    echo [poblado_credenciales] Revisa error_screenshot_poblado_credenciales.png en esta carpeta.
)
pause

endlocal
