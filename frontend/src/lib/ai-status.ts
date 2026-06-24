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

/**
 * 检测当前已激活的 AI 配置
 * 按优先级检查: custom → openai → deepseek → claude → ollama
 * 返回第一个 exists && is_active 的配置，或最后一个检查到的配置
 */
export async function detectActiveAI(): Promise<AIStatus | null> {
  const providers = ['custom', 'openai', 'deepseek', 'claude', 'ollama'];

  let lastFound: AIStatus | null = null;

  for (const provider of providers) {
    try {
      const data = await apiClient.get(`/api/ai/config/${provider}`);
      if (data?.exists) {
        const status: AIStatus = {
          provider: data.provider || provider,
          model: data.model || '-',
          active: !!data.is_active,
          exists: true,
        };
        lastFound = status;
        // 找到激活的立即返回
        if (status.active) return status;
      }
    } catch {
      // 该 provider 未配置，继续检查下一个
    }
  }

  return lastFound;
}
