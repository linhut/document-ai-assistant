/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/**
 * AI 配置状态工具
 * 供 Sidebar、RightPanel、CheckCenter 等多处共用
 * 自动检测哪个服务商已配置并激活，不硬编码 provider
 */
import apiClient from '@/api/client';

export interface AIStatus {
  provider: string;
  model: string;
  active: boolean;
  exists: boolean;
}

/** AI 配置变更全局事件名 */
export const AI_CONFIG_CHANGED = 'ai-config-changed';

/**
 * 通知其他组件 AI 配置已变更
 * AISettings 保存后调用，触发 Sidebar/RightPanel 等重新检测
 */
export function notifyAIConfigChanged(): void {
  window.dispatchEvent(new Event(AI_CONFIG_CHANGED));
}

/**
 * 检测当前已激活的 AI 配置
 *
 * 调用后端 /api/ai/active 端点（查询首个 is_active=True 的配置），
 * 无活跃配置时返回 null（不 fallback 到已禁用的 provider）。
 */
interface ActiveAIResponse {
  exists: boolean;
  active: boolean;
  provider: string;
  model: string;
}

interface AIConfigResponse {
  exists: boolean;
  is_active: boolean;
  provider: string;
  model: string;
}

export async function detectActiveAI(signal?: AbortSignal): Promise<AIStatus | null> {
  try {
    const data = await apiClient.get<ActiveAIResponse>('/api/ai/active', { signal });
    if (data?.exists && data?.active) {
      return {
        provider: data.provider || '',
        model: data.model || '-',
        active: true,
        exists: true,
      };
    }
    return null;
  } catch {
    return _fallbackDetect(signal);
  }
}

/**
 * 降级检测：逐个查询已知 provider key，仅返回 is_active=True 的。
 * 兼容旧格式（custom）和新格式（custom:xxx）。
 */
async function _fallbackDetect(signal?: AbortSignal): Promise<AIStatus | null> {
  const legacyKeys = ['custom', 'openai', 'deepseek', 'claude', 'ollama'];
  for (const provider of legacyKeys) {
    try {
      const data = await apiClient.get<AIConfigResponse>(`/api/ai/config/${provider}`, { signal });
      if (data?.exists && data?.is_active) {
        return {
          provider: data.provider || provider,
          model: data.model || '-',
          active: true,
          exists: true,
        };
      }
    } catch {
      // 该 provider 未配置，继续
    }
  }
  return null;
}
