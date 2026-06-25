/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/**
 * AppLayout - 应用主布局（v4 修正版）
 *
 * 结构：侧边栏(240/64px) | 主内容(flex-1) | 右面板(280px, ≥1440px)
 * - 三层均为同一flex容器的子元素，flex自动分配空间
 * - page-content: max-width:1600px，仅在内容超宽时约束，不影响正常填充
 * - 右面板由AppLayout条件渲染，不含自身visibility逻辑
 */
import { useState, useEffect } from 'react';
import { ReactNode } from 'react';
import Sidebar from './Sidebar';
import RightPanel from './RightPanel';
import { Menu } from 'lucide-react';

interface AppLayoutProps {
  children: ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [showRightPanel, setShowRightPanel] = useState(false);

  useEffect(() => {
    const mqMobile = window.matchMedia('(max-width: 767px)');
    const mqWide = window.matchMedia('(min-width: 1440px)');

    const check = () => {
      const mobile = mqMobile.matches;
      setIsMobile(mobile);
      if (mobile) setSidebarCollapsed(true);
      setShowRightPanel(mqWide.matches);
    };

    check();
    mqMobile.addEventListener('change', check);
    mqWide.addEventListener('change', check);
    return () => {
      mqMobile.removeEventListener('change', check);
      mqWide.removeEventListener('change', check);
    };
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-primary-50 text-primary-900">
      {/* === 侧边栏：固定宽度 240/64px === */}
      <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />

      {/* === 主内容区：flex-1 自动占满剩余空间 === */}
      <main className="flex-1 min-w-0 flex flex-col overflow-hidden">
        {/* Mobile hamburger */}
        {isMobile && sidebarCollapsed && (
          <button
            onClick={() => setSidebarCollapsed(false)}
            className="fixed top-4 left-4 z-30 p-2 bg-white rounded-lg shadow-md border border-primary-200"
          >
            <Menu className="h-5 w-5" />
          </button>
        )}

        {/* 内容滚动区 */}
        <div className="flex-1 overflow-y-auto">
          {/* page-content: 内容超1600px时约束宽度并居中，否则100%填充 */}
          <div className="page-content">
            {children}
          </div>
        </div>
      </main>

      {/* === 右面板：固定280px，≥1440px时由AppLayout渲染 === */}
      {showRightPanel && <RightPanel />}
    </div>
  );
}
