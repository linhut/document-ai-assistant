// (c) 2026 Jose AI (https://www.linhut.cn)
// https://github.com/linhut/document-ai-assistant
// Licensed under the MIT License. See the LICENSE file for details.

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
import fs from 'fs'

// 从 package.json 读取版本号，作为全局常量注入
const pkg = JSON.parse(fs.readFileSync(path.resolve(__dirname, 'package.json'), 'utf-8'))

export default defineConfig({
  base: './',  // Electron打包后使用file://协议，必须用相对路径
  plugins: [react(), tailwindcss()],
  define: {
    __APP_VERSION__: JSON.stringify(pkg.version),
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    // 主 chunk 超 500KB 时告警线放宽到 800KB（58xKB 产物现处于告警之下）
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        // Vite 8：manualChunks 仅支持函数形式 —— 框架层独立分包，
        // 依赖升级只重下对应 chunk，首屏解析更快
        manualChunks(id) {
          if (!id.includes('node_modules')) return undefined
          if (id.includes('/react/') || id.includes('/react-dom/') || id.includes('react-router')) {
            return 'react'
          }
          if (
            id.includes('@radix-ui') || id.includes('lucide-react') ||
            id.includes('class-variance-authority')
          ) {
            return 'ui'
          }
          if (id.includes('axios') || id.includes('zustand')) {
            return 'vendor'
          }
          return 'vendor-other'
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8765',
        changeOrigin: true,
      },
    },
  },
})
