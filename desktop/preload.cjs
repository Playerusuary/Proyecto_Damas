/**
 * desktop/preload.cjs
 *
 * Preload script: expone una API minima al renderer via contextBridge.
 * Esto permite detectar si la app esta corriendo en modo desktop (Electron)
 * sin habilitar nodeIntegration en el renderer.
 */

const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("desktop", {
  isDesktop: true,
});
