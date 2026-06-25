/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
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