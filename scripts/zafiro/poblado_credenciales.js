/**
 * Descarga la consulta "Poblado para credenciales" (Recursos Humanos >
 * Planeación RRHH > Procesos Especiales > Poblado para credenciales).
 *
 * Script AISLADO de index.js a propósito: así importar_zafiro (que corre
 * cada 30 min) nunca se ve afectado si este flujo cambia, falla, o se
 * reescribe. Reutiliza los mismos helpers probados en index.js/
 * descargarExcel.js/consultas.js (login, búsqueda de elemento cruzando
 * iframes, espera de descarga).
 *
 * Navegación (selectores capturados en vivo del portal, 2026-08-03):
 *   1. Abrir el menú principal (pthnavbca_PORTAL_ROOT_OBJECT) y click en
 *      "Recursos Humanos" (#crefli_SAT_TABLERO_WKC > a) — mismo patrón que
 *      "#crefli_SAT_EO_WKCN > a" en index.js/descargarExcel.js/consultas.js,
 *      solo que aquí navega directo a un Tablero (SAT_TABLERO_WKC.GBL).
 *   2. En el Tablero, click en la pestaña "Planeación RRHH" (pagelet tab,
 *      onSwitchPageletGroup) — por texto, vía clickLinkByText.
 *   3. Click en el link hijo "Poblado para credenciales"
 *      (.EOPP_SCCHILDCONTENTLINK, target="TargetContent") — por texto,
 *      igual que arriba.
 *   4. El componente POBLADO.POBLADO_CRED.GBL carga, por analogía directa
 *      con descargarExcel.js/consultas.js, dentro del frame "ptifrmtgtframe"
 *      (mismo frame donde vive el work record ZAFIRO_WRK en index.js).
 *   5. Checkbox "Poblado SQL" = POBLADO_WRK_FLAG (la consulta, preferida sobre
 *      "Poblado Excel" = POBLADO_WRK_FLAG2 porque cada INSERT trae el nombre
 *      de columna junto al valor — no depende de encoding/orden de columnas
 *      como el CSV). "Poblado Excel" viene marcada por defecto, así que se
 *      desmarca explícitamente y se marca solo "Poblado SQL". Botón
 *      "Ejecutar" = POBLADO_WRK_EXECUTE_PB.
 *   6. Confirmado por el usuario: al ejecutar con "Poblado SQL" NO se dispara
 *      una descarga a disco — se abre una pestaña/ventana nueva navegando a
 *      una URL tipo ".../tmpdb/POBLADO_CRED.TXT" con el SQL (DELETE +
 *      INSERTs en sintaxis T-SQL/SQL Server) como texto plano. El script
 *      cambia al handle de esa ventana nueva, lee el texto del body, lo
 *      guarda como poblado_credenciales.sql, cierra esa ventana y regresa a
 *      la principal.
 *
 * Si algún paso no calza exactamente con el portal real (ej. el frame no es
 * "ptifrmtgtframe"), el catch de abajo deja un screenshot
 * (error_screenshot_poblado_credenciales.png) + URL/título actuales para
 * depurar rápido cuál paso fue.
 *
 * Uso: node poblado_credenciales.js <download_dir> [headless=1]
 */
const { Builder, By, until } = require("selenium-webdriver");
const edge = require("selenium-webdriver/edge");
require("edgedriver");
const fs = require("fs");
const path = require("path");
const os = require("os");

const DOWNLOAD_DIR =
  process.argv[2] || path.join(os.homedir(), "Downloads", "ZafiroDescargas");
const HEADLESS = process.argv[3] !== "0";

if (!fs.existsSync(DOWNLOAD_DIR))
  fs.mkdirSync(DOWNLOAD_DIR, { recursive: true });

try {
  fs.readdirSync(DOWNLOAD_DIR).forEach((f) => {
    if (f.endsWith(".crdownload") || f.endsWith(".tmp")) {
      fs.unlinkSync(path.join(DOWNLOAD_DIR, f));
    }
  });
} catch (e) {}

// ---------------------------------------------------------------------------
// Helpers (copiados tal cual de index.js / descargarExcel.js / consultas.js)
// ---------------------------------------------------------------------------

function snapshotArchivos(dir) {
  if (!fs.existsSync(dir)) return new Set();
  return new Set(fs.readdirSync(dir));
}

async function waitForNewDownload(dir, previos, timeoutMs = 900000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const actuales = fs.readdirSync(dir);
    const enProgreso = actuales.some(
      (f) => f.endsWith(".crdownload") || f.endsWith(".tmp"),
    );
    const nuevosCompletos = actuales.filter(
      (f) => !previos.has(f) && !f.endsWith(".crdownload") && !f.endsWith(".tmp"),
    );
    if (nuevosCompletos.length > 0 && !enProgreso) return nuevosCompletos[0];
    await new Promise((r) => setTimeout(r, 1000));
  }
  throw new Error(`Timeout: descarga no completó en ${timeoutMs / 1000}s`);
}

/**
 * Espera a que se abra una ventana/pestaña nueva (comparado contra los
 * handles que ya existían antes de disparar la acción) y regresa su handle.
 * "Poblado SQL" navega a la URL del .TXT en una pestaña nueva en vez de
 * descargar un archivo, así que esto reemplaza a waitForNewDownload para
 * ese flujo específico (waitForNewDownload se deja arriba por si se vuelve
 * a necesitar el flujo de "Poblado Excel").
 */
async function esperarVentanaNueva(driver, handlesPrevios, timeoutMs = 60000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const handlesActuales = await driver.getAllWindowHandles();
    const nueva = handlesActuales.find((h) => !handlesPrevios.includes(h));
    if (nueva) return nueva;
    await driver.sleep(500);
  }
  throw new Error(`Timeout: no se abrió una ventana/pestaña nueva en ${timeoutMs / 1000}s`);
}

async function clickLinkByText(driver, text, timeoutMs = 15000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    await driver.switchTo().defaultContent();
    try {
      const link = await driver.findElement(By.xpath(`//a[contains(., '${text}')]`));
      await driver.executeScript("arguments[0].scrollIntoView(true);", link);
      await driver.sleep(300);
      await link.click();
      return;
    } catch (_) {}
    for (const iframe of await driver.findElements(By.css("iframe"))) {
      try {
        await driver.switchTo().frame(iframe);
        const link = await driver.findElement(By.xpath(`//a[contains(., '${text}')]`));
        await driver.executeScript("arguments[0].scrollIntoView(true);", link);
        await driver.sleep(300);
        await link.click();
        await driver.switchTo().defaultContent();
        return;
      } catch (_) {
        await driver.switchTo().defaultContent();
      }
    }
    await driver.sleep(1000);
  }
  throw new Error(`No se encontró el enlace "${text}" en ${timeoutMs}ms`);
}

async function waitAndClick(driver, selector, timeoutMs = 15000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    await driver.switchTo().defaultContent();
    try {
      await driver.wait(until.elementLocated(By.css(selector)), 2000);
      const el = await driver.findElement(By.css(selector));
      await driver.executeScript("arguments[0].scrollIntoView(true);", el);
      await driver.sleep(200);
      await el.click();
      return;
    } catch (_) {}
    for (const iframe of await driver.findElements(By.css("iframe"))) {
      try {
        await driver.switchTo().frame(iframe);
        const el = await driver.findElement(By.css(selector));
        await driver.executeScript("arguments[0].scrollIntoView(true);", el);
        await driver.sleep(200);
        await el.click();
        await driver.switchTo().defaultContent();
        return;
      } catch (_) {
        await driver.switchTo().defaultContent();
      }
    }
    await driver.sleep(1000);
  }
  throw new Error(`No se encontró el selector "${selector}" en ${timeoutMs}ms`);
}

async function switchToWorkFrame(driver, frameId, timeoutMs = 15000) {
  await driver.switchTo().defaultContent();
  await driver.wait(until.elementLocated(By.id(frameId)), timeoutMs);
  await driver.switchTo().frame(await driver.findElement(By.id(frameId)));
}

// ---------------------------------------------------------------------------

const main = async () => {
  const options = new edge.Options();
  options.addArguments("--disable-blink-features=AutomationControlled");
  options.addArguments("--start-maximized");
  options.addArguments("--window-size=1920,1080");
  options.addArguments("--no-sandbox");
  options.addArguments("--disable-dev-shm-usage");
  options.addArguments("--disable-gpu");
  options.addArguments("--disable-software-rasterizer");
  options.addArguments("--disable-extensions");
  options.addArguments("--mute-audio");
  if (HEADLESS) options.addArguments("--headless=new");
  options.setUserPreferences({
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": false,
    "download.directory_upgrade": true,
    "safebrowsing.enabled": true,
  });

  const driver = await new Builder()
    .forBrowser("MicrosoftEdge")
    .setEdgeOptions(options)
    .build();

  try {
    console.log("Iniciando descarga de Poblado para credenciales...");

    // ---- Login (idéntico a index.js/descargarExcel.js/consultas.js) ----
    await driver.get("https://peanam.mat.sat.gob.mx/psp/anamhum/EMPLOYEE/HRMS/");

    await driver.wait(until.elementLocated(By.id("userid")), 10000);
    await driver.findElement(By.id("userid")).sendKeys("GOFC79CN");
    await driver.wait(until.elementLocated(By.id("pwd")), 10000);
    await driver.findElement(By.id("pwd")).sendKeys("Carlos_N8");
    await driver.sleep(2000);
    await driver.executeScript(
      "document.querySelector('body > table > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td > table > tbody > tr > td > table:nth-child(3) > tbody > tr:nth-child(4) > td:nth-child(3) > input').click();",
    );
    await driver.sleep(2500);

    await driver.wait(until.elementLocated(By.id("pthnavbca_PORTAL_ROOT_OBJECT")), 10000);
    await driver.findElement(By.id("pthnavbca_PORTAL_ROOT_OBJECT")).click();
    await driver.sleep(1500);

    // ---- Recursos Humanos (mismo patrón que crefli_SAT_EO_WKCN) --------
    await waitAndClick(driver, "#crefli_SAT_TABLERO_WKC > a", 10000);
    await driver.sleep(2500);

    // ---- Pestaña "Planeación RRHH" (pagelet tab) ------------------------
    await clickLinkByText(driver, "Planeación RRHH", 15000);
    await driver.sleep(2000);

    // ---- Link hijo "Poblado para credenciales" (.EOPP_SCCHILDCONTENTLINK) ----
    await clickLinkByText(driver, "Poblado para credenciales", 15000);
    await driver.sleep(2500);

    // ---- El componente carga en ptifrmtgtframe (igual que ZAFIRO_WRK) ----
    await switchToWorkFrame(driver, "ptifrmtgtframe", 15000);

    // ---- Checkbox "Poblado SQL" (POBLADO_WRK_FLAG) — queremos SOLO esta
    // marcada. "Poblado Excel" (POBLADO_WRK_FLAG2) viene marcada por
    // defecto, así que se desmarca explícitamente primero. ----
    await driver.wait(until.elementLocated(By.id("POBLADO_WRK_FLAG")), 10000);

    await driver.executeScript(
      "var excel = document.getElementById('POBLADO_WRK_FLAG2'); if (excel && excel.checked) { excel.click(); }",
    );
    await driver.sleep(300);

    await driver.executeScript(
      "var sql = document.getElementById('POBLADO_WRK_FLAG'); if (sql && !sql.checked) { sql.click(); }",
    );
    await driver.sleep(300);

    // ---- Ejecutar. A diferencia de "Poblado Excel", esto NO descarga un
    // archivo: abre una pestaña/ventana nueva navegando a una URL .TXT con
    // el SQL (DELETE + INSERTs) como texto plano. Cambiamos a esa ventana,
    // leemos el texto, lo guardamos, y cerramos esa ventana. ----
    const ventanasAntes = await driver.getAllWindowHandles();

    const btn = await driver.findElement(By.id("POBLADO_WRK_EXECUTE_PB"));
    await driver.executeScript("arguments[0].scrollIntoView(true);", btn);
    await driver.sleep(500);
    await btn.click();

    const ventanaNueva = await esperarVentanaNueva(driver, ventanasAntes, 120000);
    await driver.switchTo().window(ventanaNueva);
    await driver.wait(until.elementLocated(By.css("body")), 15000);

    const contenidoSql = await driver.findElement(By.css("body")).getText();

    if (!contenidoSql || !contenidoSql.toLowerCase().includes("insert into")) {
      throw new Error(
        "La ventana nueva no contiene el SQL esperado (¿cambió el formato del portal?).",
      );
    }

    const nombreFinal = "poblado_credenciales.sql";
    fs.writeFileSync(path.join(DOWNLOAD_DIR, nombreFinal), contenidoSql, "utf-8");
    console.log(`Archivo guardado: ${nombreFinal} (${contenidoSql.length} caracteres)`);

    // Cerrar la ventana del texto y regresar a la principal antes de salir.
    await driver.close();
    await driver.switchTo().window(ventanasAntes[0]);

    console.log("Proceso terminado: Poblado para credenciales");
  } catch (error) {
    console.error("Error:", error.message);
    process.exitCode = 1;
    try {
      console.log("URL actual:", await driver.getCurrentUrl());
      console.log("Título actual:", await driver.getTitle());
      const screenshot = await driver.takeScreenshot();
      fs.writeFileSync(
        path.join(__dirname, "error_screenshot_poblado_credenciales.png"),
        screenshot,
        "base64",
      );
      console.log("Screenshot guardado en error_screenshot_poblado_credenciales.png");
    } catch (err) {
      console.error("No se pudo tomar captura o URL:", err.message);
    }
  } finally {
    await driver.quit();
  }
};

main();
