/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/**
 * Electron Main Process
 *
 * 负责：
 * - 启动 Python 后端
 * - 创建 BrowserWindow
 * - 管理应用生命周期（含系统托盘）
 * - 处理 IPC 通信
 */
import { app, BrowserWindow, shell, ipcMain, dialog, Menu, Tray, nativeImage } from 'electron';
import { spawn, ChildProcess, execSync } from 'child_process';
import * as path from 'path';
import * as url from 'url';
import * as http from 'http';
import * as fs from 'fs';

const isDev = !app.isPackaged;
const BACKEND_PORT = 8765;
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;

let mainWindow: BrowserWindow | null = null;
let tray: Tray | null = null;
let backendProcess: ChildProcess | null = null;
let backendStartedByUs = false;
let isQuitting = false;

// ---------------------------------------------------------------------------
//  Single instance lock — 防止多开
// ---------------------------------------------------------------------------

const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    // 第二个实例启动时，聚焦到已有窗口
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

// ---------------------------------------------------------------------------
//  Logging
// ---------------------------------------------------------------------------

function getLogPath(): string {
  const logDir = path.join(app.getPath('userData'), 'logs');
  if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
  return path.join(logDir, 'electron.log');
}

function log(level: string, msg: string): void {
  const line = `[${new Date().toISOString()}] [${level}] ${msg}\n`;
  console.log(line.trim());
  try { fs.appendFileSync(getLogPath(), line); } catch {}
}

// ---------------------------------------------------------------------------
//  Icon helper — 统一图标路径，Windows 使用 .ico
// ---------------------------------------------------------------------------

function getIconPath(): string {
  if (isDev) {
    // 开发模式：优先 .ico，回退 .png
    const icoPath = path.join(__dirname, '..', '..', 'build', 'icon.ico');
    if (fs.existsSync(icoPath)) return icoPath;
    return path.join(__dirname, '..', '..', 'build', 'icon.png');
  }
  // 生产模式：resources 目录下
  const icoPath = path.join(process.resourcesPath, 'icon.ico');
  if (fs.existsSync(icoPath)) return icoPath;
  return path.join(process.resourcesPath, 'icon.png');
}

// ---------------------------------------------------------------------------
//  Backend lifecycle
// ---------------------------------------------------------------------------

function getBackendCommand(): { cmd: string; args: string[] } {
  if (isDev) {
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const script = path.join(__dirname, '..', '..', '..', 'backend', 'main.py');
    return { cmd: pythonCmd, args: [script, '--force'] };
  }
  // 生产模式：直接启动 PyInstaller 打包的 exe，--force 自动释放残留端口
  const backendExe = path.join(process.resourcesPath, 'backend_server', 'backend_server.exe');
  return { cmd: backendExe, args: ['--force'] };
}

function startBackend(): void {
  const { cmd, args } = getBackendCommand();

  log('INFO', `Starting backend: ${cmd} ${args.join(' ')}`);

  if (!fs.existsSync(cmd)) {
    log('ERROR', `Backend executable not found: ${cmd}`);
    dialog.showErrorBox('启动错误', `找不到后端程序：\n${cmd}`);
    return;
  }

  const spawnOptions: Record<string, unknown> = {
    stdio: ['pipe', 'pipe', 'pipe'],
    windowsHide: true,
  };

  // 所有模式都需要 UTF-8 和无缓冲输出
  spawnOptions.env = {
    ...process.env,
    PYTHONIOENCODING: 'utf-8',
    PYTHONUNBUFFERED: '1',
  };

  if (isDev) {
    // 开发模式：cwd 设为 backend 目录
    spawnOptions.cwd = path.dirname(cmd);
  } else {
    // 生产模式：传递 APP_DATA_DIR 给后端，使运行时数据写入用户目录
    // 而非 Program Files 安装目录
    (spawnOptions.env as Record<string, string>)['APP_DATA_DIR'] = app.getPath('userData');
  }

  backendProcess = spawn(cmd, args, spawnOptions);

  backendStartedByUs = true;

  backendProcess.stdout?.on('data', (data: Buffer) => {
    log('BACKEND', data.toString().trim());
  });

  backendProcess.stderr?.on('data', (data: Buffer) => {
    log('BACKEND-ERR', data.toString().trim());
  });

  backendProcess.on('exit', (code: number | null) => {
    log('INFO', `Backend exited with code ${code}`);
    backendProcess = null;
    if (code !== 0 && code !== null && !isQuitting) {
      dialog.showErrorBox(
        '后端服务异常',
        `后端服务已退出（错误码 ${code}）。\n日志：${getLogPath()}`
      );
    }
  });

  backendProcess.on('error', (err: Error) => {
    log('ERROR', `Failed to start backend: ${err.message}`);
  });
}

/**
 * 强制终止后端进程树（Windows 下 kill 子进程）
 */
function stopBackend(): void {
  if (!backendProcess) return;

  const pid = backendProcess.pid;
  log('INFO', `Stopping backend (pid=${pid})...`);

  // 先尝试优雅关闭
  backendProcess.kill('SIGTERM');

  // Windows：3秒后用 taskkill 强制终止整个进程树
  setTimeout(() => {
    if (backendProcess) {
      log('WARN', `Force killing backend process tree (pid=${pid})`);
      try {
        if (process.platform === 'win32' && pid) {
          execSync(`taskkill /F /T /PID ${pid}`, { stdio: 'ignore' });
        } else {
          backendProcess.kill('SIGKILL');
        }
      } catch (e) {
        log('ERROR', `Failed to kill backend: ${e}`);
      }
      backendProcess = null;
    }
  }, 3000);
}

async function isBackendRunning(): Promise<boolean> {
  return new Promise((resolve) => {
    const req = http.get(`${BACKEND_URL}/api/health`, (res) => {
      res.resume();
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(2000);
    req.end();
  });
}

function waitForBackend(maxWaitMs: number = 20000): Promise<boolean> {
  return new Promise((resolve) => {
    const startTime = Date.now();
    const check = () => {
      const req = http.get(`${BACKEND_URL}/api/health`, (res) => {
        res.resume();
        if (res.statusCode === 200) {
          log('INFO', 'Backend is ready');
          resolve(true);
        } else {
          retry();
        }
      });
      req.on('error', retry);
      req.setTimeout(1000);
      req.end();
    };
    const retry = () => {
      if (Date.now() - startTime > maxWaitMs) {
        log('ERROR', `Backend did not start within ${maxWaitMs}ms`);
        resolve(false);
      } else {
        setTimeout(check, 500);
      }
    };
    check();
  });
}

// ---------------------------------------------------------------------------
//  Frontend URL
// ---------------------------------------------------------------------------

function getFrontendUrl(): string {
  if (isDev) {
    return 'http://localhost:5173';
  }
  const appPath = app.getAppPath();
  const indexPath = path.join(appPath, 'dist', 'index.html');

  log('INFO', `appPath: ${appPath}`);
  log('INFO', `indexPath: ${indexPath} exists=${fs.existsSync(indexPath)}`);

  return url.format({
    pathname: indexPath,
    protocol: 'file:',
    slashes: true,
  });
}

// ---------------------------------------------------------------------------
//  System Tray
// ---------------------------------------------------------------------------

function createTray(): void {
  const iconPath = getIconPath();
  let trayIcon: Electron.NativeImage;

  if (fs.existsSync(iconPath)) {
    trayIcon = nativeImage.createFromPath(iconPath).resize({ width: 16, height: 16 });
  } else {
    // fallback: 蓝色方块
    const iconSize = 16;
    const canvas = Buffer.alloc(iconSize * iconSize * 4);
    for (let i = 0; i < iconSize * iconSize; i++) {
      canvas[i * 4] = 0;
      canvas[i * 4 + 1] = 120;
      canvas[i * 4 + 2] = 215;
      canvas[i * 4 + 3] = 255;
    }
    trayIcon = nativeImage.createFromBuffer(canvas, { width: iconSize, height: iconSize });
  }

  tray = new Tray(trayIcon);
  tray.setToolTip('AI 公文智能优化助手');

  const contextMenu = Menu.buildFromTemplate([
    {
      label: '显示主窗口',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      },
    },
    { type: 'separator' },
    {
      label: '退出',
      click: () => {
        quitApp();
      },
    },
  ]);

  tray.setContextMenu(contextMenu);

  tray.on('double-click', () => {
    if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

// ---------------------------------------------------------------------------
//  完全退出程序
// ---------------------------------------------------------------------------

function quitApp(): void {
  isQuitting = true;
  log('INFO', 'User requested quit');
  stopBackend();
  app.quit();
}

// ---------------------------------------------------------------------------
//  Window
// ---------------------------------------------------------------------------

async function createWindow(): Promise<void> {
  const iconPath = getIconPath();

  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    title: 'AI 公文智能优化助手',
    icon: fs.existsSync(iconPath) ? iconPath : undefined,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
    show: false,
  });

  // 外部链接用默认浏览器打开
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // 加载前端
  const frontendUrl = getFrontendUrl();
  log('INFO', `Loading frontend: ${frontendUrl}`);
  await mainWindow.loadURL(frontendUrl);

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
    log('INFO', 'Window shown');
  });

  // 关闭时询问：最小化到托盘 or 退出程序
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      const choice = dialog.showMessageBoxSync(mainWindow!, {
        type: 'question',
        buttons: ['最小化到托盘', '退出程序'],
        defaultId: 0,
        cancelId: 0,
        title: '关闭确认',
        message: '请选择操作',
      });
      if (choice === 1) {
        quitApp();
      } else {
        mainWindow?.hide();
        log('INFO', 'Window minimized to tray');
      }
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// ---------------------------------------------------------------------------
//  IPC handlers
// ---------------------------------------------------------------------------

ipcMain.handle('get-app-info', () => ({
  version: app.getVersion(),
  platform: process.platform,
  isDev,
  backendPort: BACKEND_PORT,
  backendUrl: BACKEND_URL,
  logPath: getLogPath(),
}));

ipcMain.handle('get-backend-status', async () => {
  const running = await isBackendRunning();
  return {
    status: running ? 'running' : 'stopped',
    startedByUs: backendStartedByUs,
    url: BACKEND_URL,
  };
});

ipcMain.handle('get-api-base-url', () => BACKEND_URL);

// ---------------------------------------------------------------------------
//  App lifecycle
// ---------------------------------------------------------------------------

app.on('ready', async () => {
  log('INFO', `App ready. isDev=${isDev}, platform=${process.platform}, resourcesPath=${process.resourcesPath}`);
  log('INFO', `Icon path: ${getIconPath()} exists=${fs.existsSync(getIconPath())}`);

  // 移除默认英文菜单栏（File/Edit/View/Window/Help）
  Menu.setApplicationMenu(null);

  // 创建系统托盘
  createTray();

  // 检查后端是否已在运行
  const alreadyRunning = await isBackendRunning();

  if (alreadyRunning) {
    log('INFO', 'Backend already running');
  } else {
    startBackend();
    const ready = await waitForBackend();
    if (!ready) {
      log('ERROR', 'Backend failed to start');
      const choice = dialog.showMessageBoxSync({
        type: 'error',
        title: '启动失败',
        message: 'Python 后端服务启动超时。',
        detail: `日志：${getLogPath()}\n\n可能原因：\n1. Python 未安装\n2. 端口 8765 被占用\n3. 依赖包缺失`,
        buttons: ['重试', '退出'],
        defaultId: 0,
      });
      if (choice === 0) {
        startBackend();
        const ready2 = await waitForBackend();
        if (!ready2) {
          app.quit();
          return;
        }
      } else {
        app.quit();
        return;
      }
    }
  }

  await createWindow();
});

app.on('window-all-closed', () => {
  // 所有窗口关闭时直接退出
  log('INFO', 'All windows closed, quitting');
  quitApp();
});

app.on('activate', async () => {
  if (mainWindow === null) {
    await createWindow();
  } else {
    mainWindow.show();
  }
});

app.on('before-quit', () => {
  isQuitting = true;
  stopBackend();
});
