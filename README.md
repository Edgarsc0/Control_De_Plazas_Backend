# eje_central_back_copia — Celery en Windows

Copia standalone de `eje_central_back` para correr **Celery Worker + Beat**
(`importar_zafiro`) en Windows. MySQL sigue siendo remoto (servidor
compartido); **Redis corre local** en esta misma PC Windows.

No es una app Django/DRF nueva: `plantilla/tasks.py` depende del ORM,
modelos y stored procedures del proyecto — el worker necesita el contexto
Django completo, solo que sin servidor web.

> Copia estática, no sincronizada con `eje_central_back`. Cambios en
> `tasks.py`/`models.py`/etc. en el original hay que replicarlos aquí a mano.

## Topología

- MySQL: remoto, `168.231.73.222:3306` (compartido con el backend Linux).
- Redis: **local**, `127.0.0.1:6379` — broker + result backend + lock
  distribuido + cache, todo aislado de cualquier Redis que use el backend
  Linux.
- Consecuencia: el lock `lock:importar_zafiro` (ver `tasks.py`) solo
  deduplica ejecuciones dentro de ESTE Redis. Si el backend Linux también
  corre `celery beat` apuntando a su propio Redis, **nada evita que ambos
  disparen `importar_zafiro` al mismo tiempo** — el lock no cruza brokers.
  Antes de arrancar `beat` aquí, confirma que esté apagado en Linux (o
  viceversa). Solo un `beat` activo en todo el sistema.

## Requisitos

- Python 3.12+ en PATH.
- Node.js LTS (usa Selenium + Edge vía `edgedriver`; instala Microsoft Edge
  si no está).
- Redis para Windows corriendo en `127.0.0.1:6379` (ver abajo).
- Acceso de red saliente a `168.231.73.222:3306` (MySQL).
- `index.js` + `corregir_heuristico.exe` en `scripts\zafiro\` (ya
  incluidos en esta copia).

## Redis local en Windows

Redis no tiene build oficial para Windows. Opciones, de más a menos simple:

1. **Memurai** (https://www.memurai.com) — Redis-compatible, build nativo
   Windows, instalador MSI, corre como servicio. Recomendado para producción.
2. **WSL2** + Redis nativo de Linux dentro (`sudo apt install redis-server`),
   expuesto en `127.0.0.1:6379` al host Windows (WSL2 hace port-forward
   automático a localhost).
3. **Docker Desktop**: `docker run -d -p 6379:6379 redis:7`.
4. Puerto de Microsoft/tporadowski (`redis-windows` en GitHub) — no
   mantenido oficialmente, solo para dev/pruebas rápidas.

Verifica con `redis-cli ping` → `PONG` antes de arrancar Celery.

## Instalación

```bat
install.bat
```

Crea `venv\`, instala `requirements-windows.txt`, y copia `.env.example` a
`.env` si no existe (esta copia ya trae un `.env` real, no lo pisa).

`.env` ya viene con `SECRET_KEY`, MySQL y `control_gestion` prellenados.
`CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` ya apuntan a
`redis://127.0.0.1:6379/0`. Solo confirma `ZAFIRO_SCRIPT_PATH` con la ruta
real donde quedó esta carpeta.

## Arranque

```bat
start_worker.bat   REM worker solo
start_beat.bat     REM beat solo — revisar topología arriba antes de correr
start_all.bat      REM ambos, cada uno en su ventana
```

Modo primer plano (no servicio) — cerrar la ventana mata el proceso.

## Adaptación Windows: `--pool=solo`

`prefork` (default de Celery) usa `os.fork()`, no disponible en Windows.
Los scripts usan `--pool=solo` (single-thread). No hay pérdida real de
concurrencia: `importar_zafiro` ya serializa vía lock distribuido y corre
una tarea larga (~hasta 30 min) a la vez.

## `mysqlclient` no compila

Sin wheel precompilado para tu versión de Python. Fallback sin compilar:

```python
# eje_central_back/__init__.py (el paquete Django, junto a celery.py)
import pymysql
pymysql.install_as_MySQLdb()
```

(`PyMySQL` ya está en `requirements-windows.txt`.)

## Qué NO hace falta

- `python manage.py migrate` — esquema ya existe en la BD compartida.
- App Django/DRF nueva — se reutiliza `plantilla`, `authentication`, etc.
- MySQL local — es remoto.
