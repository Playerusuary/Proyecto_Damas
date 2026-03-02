const { app, BrowserWindow } = require("electron");
const path = require("node:path");
const fs = require("node:fs");
const { spawn } = require("node:child_process");
const http = require("node:http");

let backendProcess = null;
let mainWindow = null;

const BACKEND_HOST = "127.0.0.1";
const BACKEND_PORT = 8000;
const BACKEND_BASE_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}`;

function requestBackendHealth() {
  return new Promise((resolve) => {
    const req = http.get(`${BACKEND_BASE_URL}/`, { timeout: 1200 }, (res) => {
      resolve(res.statusCode >= 200 && res.statusCode < 500);
      res.resume();
    });

    req.on("error", () => resolve(false));
    req.on("timeout", () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function waitForBackend(maxMs = 20000) {
  const start = Date.now();
  while (Date.now() - start < maxMs) {
    const ok = await requestBackendHealth();
    if (ok) return true;
    await new Promise((r) => setTimeout(r, 450));
  }
  return false;
}

function getPackagedBackendConfig() {
  const exePath = path.join(process.resourcesPath, "backend", "damas-backend.exe");
  const modelPath = path.join(process.resourcesPath, "backend", "checkers_model.keras");
  return {
    command: exePath,
    args: [],
    env: {
      ...process.env,
      DAMAS_MODEL_PATH: modelPath,
    },
    cwd: path.dirname(exePath),
  };
}

function getDevBackendConfig() {
  const backendCandidates = [
    path.join(__dirname, "..", "backend"),
    path.join(__dirname, "..", "..", "backend"),
  ];
  const backendRoot =
    backendCandidates.find((p) => fs.existsSync(path.join(p, "run_backend.py"))) ||
    backendCandidates[0];

  const venvPython = path.join(backendRoot, "venv", "Scripts", "python.exe");
  const systemPython = "python";

  const command = fs.existsSync(venvPython) ? venvPython : systemPython;

  return {
    command,
    args: [path.join(backendRoot, "run_backend.py")],
    env: { ...process.env },
    cwd: backendRoot,
  };
}

function startBackendProcess() {
  const cfg = app.isPackaged ? getPackagedBackendConfig() : getDevBackendConfig();

  backendProcess = spawn(cfg.command, cfg.args, {
    cwd: cfg.cwd,
    env: cfg.env,
    stdio: "ignore",
    windowsHide: true,
    detached: false,
  });

  backendProcess.on("error", (err) => {
    console.error("No se pudo iniciar backend:", err.message);
  });
}

function stopBackendProcess() {
  if (!backendProcess || backendProcess.killed) return;

  try {
    if (process.platform === "win32") {
      spawn("taskkill", ["/PID", String(backendProcess.pid), "/T", "/F"], {
        windowsHide: true,
        stdio: "ignore",
      });
    } else {
      backendProcess.kill("SIGTERM");
    }
  } catch (err) {
    console.error("No se pudo cerrar backend:", err.message);
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 900,
    minWidth: 900,
    minHeight: 700,
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  const devUrl = process.env.ELECTRON_START_URL;
  if (devUrl) {
    mainWindow.loadURL(devUrl);
    return;
  }

  if (app.isPackaged) {
    mainWindow.loadFile(path.join(__dirname, "..", "dist", "index.html"));
    return;
  }

  const devIndexCandidates = [
    path.join(__dirname, "..", "dist", "index.html"),
    path.join(__dirname, "..", "frontend", "dist", "index.html"),
  ];
  const devIndex = devIndexCandidates.find((p) => fs.existsSync(p)) || devIndexCandidates[0];
  mainWindow.loadFile(devIndex);
}

app.whenReady().then(async () => {
  startBackendProcess();
  await waitForBackend();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("before-quit", () => {
  stopBackendProcess();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
