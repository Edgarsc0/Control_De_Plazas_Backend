@echo off
REM =============================================================================
REM Instala el entorno virtual y dependencias para correr Celery en Windows.
REM Ejecutar UNA vez (o de nuevo si cambia requirements-windows.txt).
REM =============================================================================
setlocal

set "ROOT=%~dp0"

echo ============================================
echo  1. Verificando Python...
echo ============================================
python --version
if errorlevel 1 (
    echo ERROR: No se encontro "python" en PATH. Instala Python 3.12+ desde
    echo https://www.python.org/downloads/ marcando "Add python.exe to PATH".
    exit /b 1
)

echo ============================================
echo  2. Creando entorno virtual en venv ...
echo ============================================
if not exist "%ROOT%venv" (
    python -m venv "%ROOT%venv"
)

call "%ROOT%venv\Scripts\activate.bat"

echo ============================================
echo  3. Instalando dependencias ...
echo ============================================
python -m pip install --upgrade pip
pip install -r "%ROOT%requirements-windows.txt"
if errorlevel 1 (
    echo.
    echo ============================================
    echo  AVISO: si "mysqlclient" fallo al compilar, ve
    echo  README.md, seccion "Problemas con mysqlclient".
    echo ============================================
)

echo ============================================
echo  4. Preparando archivo .env ...
echo ============================================
if not exist "%ROOT%.env" (
    copy "%ROOT%.env.example" "%ROOT%.env"
    echo Se creo "%ROOT%.env" a partir de .env.example.
    echo IMPORTANTE: editalo y llena los valores reales antes de arrancar Celery.
) else (
    echo Ya existe "%ROOT%.env", no se sobrescribe.
)

echo.
echo Listo. Revisa "%ROOT%.env" y luego corre start_all.bat
endlocal
