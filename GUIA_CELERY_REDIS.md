# Cómo funcionan Celery y Redis en este proyecto

## 1. Las piezas y para qué sirve cada una

| Pieza | Rol | Dónde vive |
|---|---|---|
| **Django** | La app web (API REST). Define modelos, vistas, settings. | `eje_central_back/`, `plantilla/`, etc. |
| **Redis** | Un servidor de mensajería/caché en memoria. Aquí cumple 3 roles a la vez (ver abajo). | Local en Windows, puerto `6379` |
| **Celery Worker** | Un proceso separado que ejecuta tareas pesadas/lentas *fuera* del ciclo request-response de Django. | `start_worker.bat` |
| **Celery Beat** | Un "reloj": dispara tareas programadas a horarios fijos (como un cron). No ejecuta nada él mismo, solo *encola* la tarea para que el Worker la tome. | `start_beat.bat` |

Django, Worker y Beat son **3 procesos independientes** que se comunican entre sí a través de Redis. Por eso `start_all.bat` abre 2 ventanas de terminal (Worker y Beat) además de que Django corre aparte (`runserver` o similar).

## 2. Los 3 roles de Redis aquí

Configurado en `eje_central_back/settings.py`:

1. **Broker de Celery** (`CELERY_BROKER_URL`): la "cola de pendientes". Cuando Beat decide que es hora de correr una tarea, mete un mensaje en Redis. El Worker está escuchando esa cola y lo recoge.
2. **Result backend** (`CELERY_RESULT_BACKEND`): donde Celery guarda el resultado/estado de cada tarea ejecutada.
3. **Cache de Django** (`CACHES`, línea ~265 de `settings.py`): Django reutiliza el mismo Redis para cachear cosas como el dashboard, evitando recalcular cada vez que la tarea de ZAFIRO termina.

Además, `plantilla/tasks.py` usa Redis directamente (sin pasar por Celery) para:
- Un **lock distribuido** (`lock:importar_zafiro`) que garantiza que solo una instancia de la tarea corra a la vez, aunque haya varios workers o se dispare dos veces.
- Publicar eventos en el canal `zafiro_updates` para notificar al frontend en tiempo real (SSE) cuando termina una importación.

## 3. La tarea real: `importar_zafiro`

Está definida en `plantilla/tasks.py` (`@shared_task(name="plantilla.tasks.importar_zafiro")`) y programada en `CELERY_BEAT_SCHEDULE` (settings.py) para correr **cada 30 minutos**.

Qué hace, en resumen:
1. Toma el lock en Redis (si ya hay una corriendo, se descarta).
2. Por cada uno de 4 reportes (Posiciones, Empleados Completos, Empleados Bajas, Historial Posición):
   - Ejecuta un script **Node.js** (`scripts/zafiro/index.js`) que hace scraping/descarga del sistema ZAFIRO y genera un CSV.
   - Corrige el CSV con un binario externo heurístico (si existe).
   - Trunca la tabla `*_STAGING` correspondiente e inserta los datos con `bulk_create`.
3. Cuando los 4 reportes están cargados en staging, hace un **swap atómico** (`RENAME TABLE`, patrón Blue-Green) entre las tablas de producción y las de staging — así los datos nuevos quedan en producción de forma instantánea, sin downtime.
4. Corre varios *stored procedures* de post-proceso (llenar nombres de puesto, corregir SMB/SMN, calcular vacancias, etc.).
5. Publica el evento en Redis para que el frontend se refresque, e invalida cachés.

Todo el progreso queda registrado en vivo en el modelo `ZafiroBitacora` (columna `logs_en_vivo`), visible también en la ventana de la terminal del Worker.

## 4. Cómo se arranca todo

```
install.bat      → crea el venv e instala dependencias (una sola vez, o cuando cambie requirements-windows.txt)
start_all.bat    → abre 2 ventanas: start_worker.bat y start_beat.bat
```

- `start_worker.bat`: activa el venv y corre `celery -A eje_central_back worker --pool=solo`. En Windows se usa `--pool=solo` porque el pool por defecto de Celery (`prefork`) depende de `os.fork()`, que no existe en Windows.
- `start_beat.bat`: activa el venv y corre `celery -A eje_central_back beat --scheduler django_celery_beat.schedulers:DatabaseScheduler`. El scheduler de base de datos permite ver/editar el horario desde el admin de Django (tabla `django_celery_beat`).

Django (el servidor web en sí) se arranca aparte, normalmente con `python manage.py runserver`.

## 5. Problemas que se corrigieron en esta sesión

1. **`requirements-windows.txt`** pedía `google-antigravity==0.1.0`, versión que no existe en PyPI (mínima disponible: `0.1.2`). Esto abortaba el `pip install -r` completo, dejando el venv sin Celery ni ninguna otra dependencia instalada. → Se fijó a `google-antigravity==0.1.2`.
2. **`.env`**: la línea `EJE CENTRAL BACKEND ENV: DB_NAME = EjeCentral` no era un comentario válido (no empieza con `#`), así que `DB_NAME` nunca se leía y Django se conectaba a MySQL sin seleccionar base de datos (`OperationalError 1046`). → Se corrigió a `# EJE CENTRAL BACKEND ENV` + `DB_NAME = EjeCentral`.
3. **Redis/Celery**: el paquete `redis` (cliente Python) se instaló en su versión más reciente (8.0.1), que por defecto negocia protocolo RESP3 enviando el comando `HELLO`. El Redis-server que corre en esta PC Windows es la versión 5.0.14.1 (muy antigua, de un puerto no oficial) y no reconoce `HELLO` → `unknown command 'HELLO'`. → Se fijó `redis==5.2.1` en `requirements-windows.txt`, versión que usa RESP2 por defecto y sí es compatible.

## 6. Pendiente detectado (no corregido aún)

En la última corrida, el Worker recibió la tarea `importar_zafiro` pero el script Node.js falló:

```
Error: Cannot find module 'selenium-webdriver'
```

Esto es un problema de **dependencias de Node.js**, no de Python/Celery: falta correr `npm install` dentro de `scripts/zafiro/` (o la carpeta que contenga el `package.json` de ese script) para instalar `selenium-webdriver` y demás paquetes que use `index.js`. La infraestructura de Celery/Redis en sí ya quedó funcionando correctamente (Beat programa, Worker recibe, hace retry a los 5 minutos según `default_retry_delay=300`).
