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
 *   5. Checkbox "Poblado Excel" = POBLADO_WRK_FLAG2 (ya viene marcado por
 *      defecto en el portal; el script lo deja idempotente). Botón
 *      "Ejecutar" = POBLADO_WRK_EXECUTE_PB.
 *   6. Confirmado por el usuario: al ejecutar aparece un loader arriba a la
 *      derecha (~30s o menos) y al terminar el navegador dispara la
 *      descarga automáticamente — NO hay pantalla de Process Monitor que
 *      sondear (a diferencia de descargarExcel.js/consultas.js). Mismo
 *      patrón de espera que index.js (waitForNewDownload).
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

    // ---- Checkbox "Poblado Excel" — idempotente, ya viene marcado por
    // defecto en el portal, pero lo forzamos por si alguna vez no lo está ----
    await driver.wait(until.elementLocated(By.id("POBLADO_WRK_FLAG2")), 10000);
    const yaMarcado = await driver.executeScript(
      "var cb = document.getElementById('POBLADO_WRK_FLAG2'); return cb ? cb.checked : false;",
    );
    if (!yaMarcado) {
      await driver.executeScript(
        "document.getElementById('POBLADO_WRK_FLAG2').click();",
      );
      await driver.sleep(500);
    }

    // ---- Ejecutar y esperar la descarga automática del navegador --------
    // Confirmado en el portal real: aparece un loader (~30s o menos) y al
    // terminar el navegador dispara la descarga solo — sin pantalla de
    // Process Monitor que sondear (a diferencia de descargarExcel.js).
    const previos = snapshotArchivos(DOWNLOAD_DIR);
    const btn = await driver.findElement(By.id("POBLADO_WRK_EXECUTE_PB"));
    await driver.executeScript("arguments[0].scrollIntoView(true);", btn);
    await driver.sleep(500);
    await btn.click();

    const archivoDescargado = await waitForNewDownload(DOWNLOAD_DIR, previos, 120000);
    const ext = path.extname(archivoDescargado) || ".csv";
    const nombreFinal = `poblado_credenciales${ext}`;
    fs.renameSync(
      path.join(DOWNLOAD_DIR, archivoDescargado),
      path.join(DOWNLOAD_DIR, nombreFinal),
    );
    console.log(`Archivo guardado: ${nombreFinal}`);
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
