/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/**
 * API Client - Axios 实例配置
 *
 * 支持三种运行环境：
 * 1. 开发模式（Vite dev server）：通过 proxy 转发 /api → localhost:8765
 * 2. 生产模式（Electron）：直接调用 http://127.0.0.1:8765
 * 3. 自定义：通过 VITE_API_BASE_URL 环境变量覆盖
 *
 * 所有 API 调用必须通过此 client，禁止直接 fetch。
 */
import axios from 'axios';

/**
 * 获取 API 基础地址。
 * 优先级：Electron IPC > 环境变量 > 默认值
 */
function getBaseUrl(): string {
  // Electron 环境：通过 IPC 获取后端地址
  if (typeof window !== 'undefined' && (window as any).electronAPI?.getBackendStatus) {
    // 同步返回已知地址（Electron main 进程已确认后端可用）
    return 'http://127.0.0.1:8765';
  }
  // Vite 环境变量
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  // 开发模式下 Vite proxy 会处理 /api，所以用空字符串
  if (import.meta.env.DEV) {
    return '';
  }
  // 生产默认
  return 'http://127.0.0.1:8765';
}

const API_BASE_URL = getBaseUrl();

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
}) as any;

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // 统一错误处理 — 分类化错误信息
    const status = error.response?.status;
    const detail = error.response?.data?.detail;

    let message: string;
    if (!error.response) {
      message = '无法连接到后端服务，请确认服务已启动';
    } else if (status === 404) {
      message = detail || '请求的资源不存在';
    } else if (status === 400) {
      message = detail || '请求参数错误';
    } else if (status === 500) {
      message = detail || '后端处理异常';
    } else {
      message = detail || error.message || '请求失败';
    }

    console.error(`API Error [${status}]:`, message);
    return Promise.reject(error);
  }
);

/**
 * 下载文件的辅助函数。
 * 统一处理文件下载，避免页面直接拼接 URL。
 */
export function downloadFile(endpoint: string, filename: string): void {
  const url = `${API_BASE_URL}${endpoint}`;
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

export default apiClient;