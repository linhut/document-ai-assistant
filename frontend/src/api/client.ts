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
import axios, { type RawAxiosRequestConfig } from 'axios';

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

/**
 * 底层 axios 实例。
 * 响应拦截器会自动 unwrap response.data，
 * 因此实际返回的是后端 JSON payload，而非 AxiosResponse。
 */
const rawClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
rawClient.interceptors.request.use(
  (config) => {
    // Attach Bearer token from localStorage if present
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 — 返回 response.data（而非完整 AxiosResponse）
rawClient.interceptors.response.use(
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
    } else if (status === 401) {
      message = detail || '认证失败，请检查 Token 配置';
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
 * 类型安全的 API 客户端。
 *
 * 响应拦截器已经 unwraps response.data，所以所有方法
 * 返回的 Promise 解析值就是后端 JSON payload（而非 AxiosResponse）。
 * 这里的泛型 T 用来指定 payload 类型。
 */
export const apiClient = {
  get<T = unknown>(url: string, config?: RawAxiosRequestConfig): Promise<T> {
    return rawClient.get(url, config) as Promise<T>;
  },
  post<T = unknown>(url: string, data?: unknown, config?: RawAxiosRequestConfig): Promise<T> {
    return rawClient.post(url, data, config) as Promise<T>;
  },
  put<T = unknown>(url: string, data?: unknown, config?: RawAxiosRequestConfig): Promise<T> {
    return rawClient.put(url, data, config) as Promise<T>;
  },
  delete<T = unknown>(url: string, config?: RawAxiosRequestConfig): Promise<T> {
    return rawClient.delete(url, config) as Promise<T>;
  },
};

/**
 * 下载文件的辅助函数。
 * 使用 fetch + blob，可捕获 HTTP 错误并给出提示。
 * 内置超时控制（默认 60 秒），防止大文件下载时无限等待。
 */
export async function downloadFile(endpoint: string, filename: string, timeoutMs = 60000): Promise<void> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers: Record<string, string> = {};
  const token = localStorage.getItem('auth_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // 使用 AbortController 实现超时控制
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const resp = await fetch(url, { headers, signal: controller.signal });
    clearTimeout(timeoutId);
    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      let msg = `下载失败 (HTTP ${resp.status})`;
      try { msg = JSON.parse(text).detail || msg; } catch {}
      throw new Error(msg);
    }
    const blob = await resp.blob();
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(blobUrl);
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err?.name === 'AbortError') {
      const msg = '下载超时，请检查网络连接或稍后重试';
      console.error('downloadFile timeout:', url);
      alert(msg);
    } else {
      console.error('downloadFile error:', err);
      alert(err?.message || '下载失败，请重试');
    }
  }
}

export default apiClient;