// (c) 2026 Jose AI (https://www.linhut.cn)
// https://github.com/linhut/document-ai-assistant
// Licensed under the MIT License. See the LICENSE file for details.

/**
 * 全局应用状态（zustand）
 *
 * 统一管理跨页面共享状态，当前覆盖 AI 配置状态：
 *   - 各页面通过 useAppStore 读取 aiStatus / 触发 refreshAIStatus，
 *     不再各自 detectActiveAI + 监听 window 事件
 *   - AISettings 保存/切换/删除后调用 notifyAIConfigChanged()（window 事件），
 *     store 在模块层监听该事件并自动刷新，所有订阅组件同步更新
 */
import { create } from 'zustand';
import { AI_CONFIG_CHANGED, detectActiveAI, type AIStatus } from '@/lib/ai-status';

interface AppState {
  /** 当前激活的 AI 配置（未激活为 null） */
  aiStatus: AIStatus | null;
  /** AI 状态检测中 */
  aiLoading: boolean;
  setAIStatus: (status: AIStatus | null) => void;
  /** 重新检测激活的 AI 配置并写入 store */
  refreshAIStatus: () => Promise<AIStatus | null>;
}

export const useAppStore = create<AppState>((set) => ({
  aiStatus: null,
  aiLoading: false,
  setAIStatus: (status) => set({ aiStatus: status, aiLoading: false }),
  refreshAIStatus: async () => {
    set({ aiLoading: true });
    try {
      const status = await detectActiveAI();
      set({ aiStatus: status, aiLoading: false });
      return status;
    } catch {
      set({ aiStatus: null, aiLoading: false });
      return null;
    }
  },
}));

// 模块级监听：AI 配置变更事件 → 自动刷新 store（兼容既有 notifyAIConfigChanged 调用方）
if (typeof window !== 'undefined') {
  window.addEventListener(AI_CONFIG_CHANGED, () => {
    void useAppStore.getState().refreshAIStatus();
  });
}

/** 便捷 hook：返回 AI 状态与刷新函数 */
export function useAIStatus(): { aiStatus: AIStatus | null; aiLoading: boolean; refreshAIStatus: () => Promise<AIStatus | null> } {
  const aiStatus = useAppStore((s) => s.aiStatus);
  const aiLoading = useAppStore((s) => s.aiLoading);
  const refreshAIStatus = useAppStore((s) => s.refreshAIStatus);
  return { aiStatus, aiLoading, refreshAIStatus };
}
