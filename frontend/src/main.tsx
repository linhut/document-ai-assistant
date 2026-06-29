/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ToastProvider } from './components/ui/toast.tsx'

// ---------------------------------------------------------------------------
//  全局错误处理 — 防止未捕获异常导致白屏
// ---------------------------------------------------------------------------
window.addEventListener('unhandledrejection', (event) => {
  console.error('[Unhandled Promise Rejection]', event.reason);
  // 阻止默认的控制台报错（避免 Electron 白屏）
  event.preventDefault();
});

window.addEventListener('error', (event) => {
  console.error('[Global Error]', event.error || event.message, event.filename, event.lineno);
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ToastProvider>
      <App />
    </ToastProvider>
  </StrictMode>,
)
