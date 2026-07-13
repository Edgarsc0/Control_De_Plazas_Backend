# Guía de instalación — Celery en Windows

Setup para correr `importar_zafiro` (Celery Worker + Beat) en Windows.
MySQL remoto (`168.231.73.222:3306`), Redis local a esta PC.

**Antes que nada**: confirma con el equipo que no haya ya un `celery beat`
corriendo en el servidor Linux apuntando a producción. El lock distribuido
de la tarea vive en Redis, y aquí el Redis es local — no coordina con el de
Linux. Dos `beat` activos = doble ejecución de la tarea. Solo uno a la vez
en todo el sistema.

## 1. Prerrequisitos

- Python 3.12+ (`python --version`), en PATH.
- Node.js LTS (`node --version`). `index.js` usa `selenium-webdriver` +
  `edgedriver` → necesita Microsoft Edge instalado.
- Redis en `127.0.0.1:6379` (paso 2).

## 2. Redis local

Redis no tiene build oficial Windows. Elige uno:

| Opción | Comando/instalación | Notas |
|---|---|---|
| **Memurai** (recomendado) | Instalador MSI desde memurai.com | Corre como servicio Windows, Redis-compatible |
| WSL2 | `wsl --install`, luego `sudo apt install redis-server` dentro de WSL | WSL2 forwardea `127.0.0.1:6379` al host automáticamente |
| Docker Desktop | `docker run -d -p 6379:6379 redis:7` | Requiere Docker Desktop con backend WSL2/Hyper-V |

Verifica:
```
redis-cli ping
```
→ debe responder `PONG`. Si `redis-cli` no está en PATH, prueba
`docker exec -it <container> redis-cli ping` o el cliente que traiga tu
opción elegida.

## 3. Clonar/copiar esta carpeta

Copia `eje_central_back_copia` completa a la PC Windows. Ruta sin espacios
recomendada, ej. `C:\ANAM\eje_central_back_copia`.

## 4. Instalar dependencias

```bat
install.bat
```

Crea `venv\`, instala `requirements-windows.txt`. No pisa `.env` si ya
existe (esta copia trae uno real prellenado).

Si `mysqlclient` falla al compilar (sin wheel para tu Python): ver
`README.md` → "mysqlclient no compila" (fallback a PyMySQL, 2 líneas).

## 5. Revisar `.env`

Ya viene prellenado (`SECRET_KEY`, credenciales MySQL, `control_gestion`,
`CELERY_BROKER_URL=redis://127.0.0.1:6379/0`). Solo confirma:

```
ZAFIRO_SCRIPT_PATH=C:\ruta\real\a\eje_central_back_copia\scripts\zafiro\index.js
```

que coincida con dónde quedó esta carpeta. `ZAFIRO_DOWNLOAD_DIR` ya apunta a
`C:\ZafiroDescargas` (se crea sola si no existe).

## 6. Scripts ZAFIRO

`scripts\zafiro\` ya trae `index.js`, `consultas.js`, `descargarExcel.js`,
`corregir_heuristico.exe`, `package.json`/`package-lock.json`, `patrones\`.
Falta `node_modules` (no se copió — es Linux-specific, `edgedriver` baja
binarios por plataforma):

```bat
cd scripts\zafiro
npm install
```

## 7. Arrancar

```bat
start_worker.bat
```
Confirma en consola:
```
[tasks]
  . plantilla.tasks.importar_zafiro
celery@HOST ready.
```

Beat (solo si confirmaste el punto del encabezado — un solo beat en todo
el sistema):
```bat
start_beat.bat
```

O ambos en una:
```bat
start_all.bat
```

Primer plano, `--pool=solo` (Windows no soporta `prefork`/`os.fork`).
Cerrar la ventana mata el proceso — no hay modo servicio en este setup.

## 8. Verificación

- Beat dispara `importar_zafiro` cada 30 min (`crontab(minute="*/30")` en
  `settings.py`), o dispárala a mano desde el sistema si ya hay un endpoint
  para eso.
- Log del worker debe mostrar las 4 descargas (Posiciones, Empleados
  Completos, Bajas, Historial), el swap Blue-Green y los stored procedures
  de post-proceso.
- Progreso también queda en `ZafiroBitacora` (tabla) — visible desde el
  admin/frontend si necesitas debug sin mirar la consola.

## Troubleshooting

| Síntoma | Causa | Fix |
|---|---|---|
| `ConnectionRefusedError` a Redis | Redis local no está corriendo | Repite paso 2, `redis-cli ping` |
| Timeout/`Access denied` a MySQL | Firewall del servidor no permite esta IP saliente, o credenciales | Confirma con el admin del servidor que `168.231.73.222:3306` acepte tu IP |
| `node`/`npm` no reconocido | PATH no actualizado tras instalar Node | Abre terminal nueva |
| Tarea corre duplicada | Dos `beat` activos (Linux + Windows) | Apaga uno de los dos, ver encabezado |
| `mysqlclient` no compila | Sin wheel para tu versión de Python | `README.md` → fallback PyMySQL |
