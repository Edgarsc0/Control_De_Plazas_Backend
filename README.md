# Backend Eje Central - Guía de Instalación para Windows 11

Esta es la guía oficial para configurar y ejecutar el backend del sistema "Eje Central" en un entorno Windows 11.

## 1. Requisitos Previos
Asegúrate de tener instalados los siguientes programas en tu computadora:
- **Python 3.10 o superior**: Al instalarlo, asegúrate de marcar la casilla "Add Python to PATH" durante el instalador.
- **Node.js**: Necesario para ejecutar los scripts de scraping de Zafiro.
- **Redis Server para Windows**: Celery requiere Redis para funcionar. Puedes instalarlo descargando [Memurai](https://www.memurai.com/) (un clon de Redis para Windows) o usando WSL (Windows Subsystem for Linux).
- **MySQL**: (Opcional si tu base de datos ya está en la nube o en otro servidor como el `168.231.73.222`).

## 2. Preparar el entorno

1. Abre tu terminal (`cmd` o `PowerShell`) y navega hasta esta carpeta:
   ```cmd
   cd C:\Ruta\A\Tu\Carpeta\copia_back
   ```

2. Crea un entorno virtual de Python:
   ```cmd
   python -m venv venv
   ```

3. Activa el entorno virtual:
   ```cmd
   .\venv\Scripts\activate
   ```
   *(Si PowerShell te da un error de ejecución de scripts, abre PowerShell como administrador y ejecuta: `Set-ExecutionPolicy Unrestricted`)*

4. Instala las dependencias del proyecto:
   ```cmd
   pip install -r requirements.txt
   ```
   *Nota: Hemos añadido `gevent` a las dependencias porque Celery en Windows no soporta el modelo por defecto (prefork).*

## 3. Configuración (.env)

Abre el archivo `.env` que se encuentra en la raíz de esta carpeta y ajusta las rutas para que coincidan con tu sistema de Windows:
- **ZAFIRO_SCRIPT_PATH**: Debe apuntar al archivo `index.js` de tus scripts de Node. Ejemplo:
  `ZAFIRO_SCRIPT_PATH = C:\Users\TuUsuario\Documents\SIORH-Back\automatizacion\scripts\index.js`

*Nota: La ruta de descarga (`ZAFIRO_DOWNLOAD_DIR`) se autoconfigura por defecto a tu carpeta de Descargas en Windows (ej. `C:\Users\TuUsuario\Downloads\ZafiroDescargas`).*

## 4. Iniciar el Servidor Django

Asegúrate de que tu entorno virtual sigue activado, entra a la carpeta principal del código y ejecuta las migraciones (si aplica) y luego el servidor:

```cmd
cd eje_central_back
python manage.py migrate
python manage.py runserver
```
El servidor ahora correrá en `http://127.0.0.1:8000/`.

## 5. Iniciar Celery (Para tareas en segundo plano)

Abre **otra ventana nueva** de terminal (`cmd` o `PowerShell`), navega a la misma ruta y **activa el entorno virtual de nuevo**:

```cmd
cd C:\Ruta\A\Tu\Carpeta\copia_back
.\venv\Scripts\activate
cd eje_central_back
```

A diferencia de Linux o Mac, **Celery en Windows requiere ejecutarse usando el pool `gevent`**. Ejecuta el siguiente comando para iniciar el *Worker*:

```cmd
celery -A eje_central_back worker -l info -P gevent
```

¡Listo! Con esto tendrás tu entorno corriendo de manera estable en Windows 11.
