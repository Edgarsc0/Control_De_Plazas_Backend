# Scripts ZAFIRO (Windows)

Esta carpeta está vacía a propósito. Copia aquí estos archivos:

- `index.js` — el script Node.js que descarga los CSV de ZAFIRO.
- Todo lo que `index.js` necesite para correr (`package.json`,
  `node_modules`, etc. — corre `npm install` aquí si hace falta).
- `corregir_heuristico.exe` — el binario corrector heurístico (debe
  llamarse exactamente así; `plantilla/tasks.py` lo busca por ese nombre
  + `.exe` en Windows, en la MISMA carpeta que `index.js`).

Luego, en el `.env` de la raíz de esta copia (ver `README.md` principal),
apunta:

```
ZAFIRO_SCRIPT_PATH=C:\ruta\completa\a\eje_central_back_copia\scripts\zafiro\index.js
```

También necesitas **Node.js instalado en Windows**
(https://nodejs.org, LTS) y disponible en el PATH (`node --version` debe
funcionar en una terminal nueva).
