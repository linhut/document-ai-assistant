/**
 * Electron Preload Script
 *
 * 通过 contextBridge 暴露安全的 IPC 接口给渲染进程。
 */
import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getAppInfo: () => ipcRenderer.invoke('get-app-info'),
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),

  // Platform helpers
  platform: process.platform,
  isElectron: true,
});