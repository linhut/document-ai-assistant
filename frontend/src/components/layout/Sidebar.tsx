/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/**
 * Sidebar - 侧边导航栏
 * 自适应：宽屏展开，窄屏可折叠
 *
 * 导航分组：
 *   核心: 工作台, 文档处理
 *   辅助: 校审中心, 模板中心 (expandable)
 *   系统: AI 设置, 关于
 *
 * 底部显示 AI 状态指示器和版本信息。
 */
import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  FileText,
  CheckCircle2,
  Settings,
  Info,
  ChevronDown,
  ChevronRight,
  Layout,
  X,
} from 'lucide-react';
import { detectActiveAI, type AIStatus } from '../../lib/ai-status';

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

/** 导航项类型 */
interface NavItemBase {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  path: string;
}

interface NavItemSimple extends NavItemBase {
  expandable?: false;
}

interface NavItemExpandable extends NavItemBase {
  expandable: true;
  children: Array<{ label: string; path: string }>;
}

type NavItem = NavItemSimple | NavItemExpandable;

/** 导航分组定义 */
interface NavGroup {
  label: string;
  items: NavItem[];
}

export default function Sidebar({ collapsed = false, onToggle }: SidebarProps) {
  const location = useLocation();
  const [templatesExpanded, setTemplatesExpanded] = useState(true);
  const [isMobile, setIsMobile] = useState(false);
  const [aiReady, setAiReady] = useState<boolean | null>(null);
  const [aiInfo, setAiInfo] = useState<AIStatus | null>(null);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Fetch AI configuration status — 检测所有 provider，不硬编码
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const status = await detectActiveAI();
      if (!cancelled) {
        setAiReady(status?.active ?? false);
        setAiInfo(status);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const isActive = (path: string) => location.pathname === path;

  // 检查expandable项是否激活（当前路径匹配自身或任意子路由）
  const isExpandableActive = (item: NavItemExpandable) => {
    if (location.pathname === item.path) return true;
    return item.children?.some(child => location.pathname === child.path) ?? false;
  };

  // 导航分组：核心 → 辅助 → 系统
  const navGroups: NavGroup[] = [
    {
      label: '核心',
      items: [
        { icon: Home, label: '工作台', path: '/workspace' },
        { icon: FileText, label: '文档处理', path: '/document/process' },
      ],
    },
    {
      label: '辅助',
      items: [
        { icon: CheckCircle2, label: '校审中心', path: '/document/check' },
        {
          icon: Layout,
          label: '模板中心',
          path: '/templates',
          expandable: true,
          children: [
            { label: '查看所有模板', path: '/templates' },
            { label: '导入模板', path: '/templates/import' },
            { label: '规则管理', path: '/rules' },
          ],
        },
      ],
    },
    {
      label: '系统',
      items: [
        { icon: Settings, label: 'AI 设置', path: '/settings/ai' },
        { icon: Info, label: '关于', path: '/about' },
      ],
    },
  ];

  const isCollapsed = collapsed || isMobile;

  return (
    <>
      {/* Mobile overlay */}
      {isMobile && !collapsed && (
        <div
          className="fixed inset-0 bg-black/40 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          ${isCollapsed ? 'w-16' : 'w-60'}
          bg-white border-r border-primary-200 flex flex-col h-full
          transition-all duration-200 ease-in-out
          ${isMobile ? 'fixed z-50' : 'relative'}
          ${isMobile && collapsed ? '-translate-x-full' : ''}
        `}
      >
        {/* Logo 区域 */}
        <div className={`${isCollapsed ? 'p-3' : 'p-6'} border-b border-primary-200 flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'}`}>
          {!isCollapsed && (
            <Link to="/" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-accent rounded-lg flex items-center justify-center">
                <FileText className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="font-bold text-lg">公文助手</h1>
                <p className="text-xs text-primary-500">AI 智能优化</p>
              </div>
            </Link>
          )}
          {isCollapsed && (
            <Link to="/" className="w-10 h-10 bg-accent rounded-lg flex items-center justify-center">
              <FileText className="h-6 w-6 text-white" />
            </Link>
          )}
          {isMobile && (
            <button onClick={onToggle} className="p-1 hover:bg-primary-100 rounded">
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* 导航菜单 — 按分组渲染，组间分隔线 */}
        <nav className={`flex-1 ${isCollapsed ? 'p-2' : 'p-4'} overflow-y-auto`}>
          {navGroups.map((group, groupIdx) => (
            <div key={group.label}>
              {/* 分组分隔线：第一组之前不需要 */}
              {groupIdx > 0 && (
                <div className={`${isCollapsed ? 'my-2 mx-2' : 'my-3'}`}>
                  <div className={`border-t border-primary-200 ${isCollapsed ? '' : ''}`} />
                </div>
              )}

              {/* 分组标题（仅展开模式显示） */}
              {!isCollapsed && (
                <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider px-4 mb-1">
                  {group.label}
                </p>
              )}

              <div className="space-y-1">
                {group.items.map((item) => (
                  <div key={item.path}>
                    {'expandable' in item && item.expandable ? (
                      <>
                        {/* 折叠态：图标直接导航到默认子路由 */}
                        {isCollapsed ? (
                          <Link
                            to={item.children?.[0]?.path || item.path}
                            className={`
                              flex items-center gap-3
                              px-2 py-3 justify-center
                              rounded-lg transition-colors
                              ${isExpandableActive(item)
                                ? 'bg-accent text-white'
                                : 'text-primary-700 hover:bg-primary-100'}
                            `}
                            title={item.label}
                          >
                            <item.icon className="h-5 w-5 flex-shrink-0" />
                          </Link>
                        ) : (
                          /* 展开态：点击图标导航，点击箭头展开/折叠 */
                          <div className="flex items-center w-full">
                            <Link
                              to={item.children?.[0]?.path || item.path}
                              className={`
                                flex-1 flex items-center gap-3 px-4 py-3
                                rounded-lg transition-colors
                                ${isExpandableActive(item)
                                  ? 'bg-accent text-white'
                                  : 'text-primary-700 hover:bg-primary-100'}
                              `}
                            >
                              <item.icon className="h-5 w-5 flex-shrink-0" />
                              <span className="flex-1 text-left">{item.label}</span>
                            </Link>
                            <button
                              onClick={() => setTemplatesExpanded(!templatesExpanded)}
                              className="p-1 rounded hover:bg-primary-100 transition-colors"
                              aria-label={templatesExpanded ? '折叠' : '展开'}
                            >
                              {templatesExpanded ? (
                                <ChevronDown className="h-4 w-4 text-primary-500" />
                              ) : (
                                <ChevronRight className="h-4 w-4 text-primary-500" />
                              )}
                            </button>
                          </div>
                        )}
                        {!isCollapsed && templatesExpanded && item.children && (
                          <div className="ml-8 mt-1 space-y-1">
                            {item.children.map((child) => (
                              <Link
                                key={child.path}
                                to={child.path}
                                className={`block px-4 py-2 rounded-lg text-sm transition-colors ${
                                  isActive(child.path)
                                    ? 'bg-accent-light text-accent font-medium'
                                    : 'text-primary-600 hover:bg-primary-50'
                                }`}
                              >
                                {child.label}
                              </Link>
                            ))}
                          </div>
                        )}
                      </>
                    ) : (
                      <Link
                        to={item.path}
                        className={`
                          flex items-center gap-3
                          ${isCollapsed ? 'px-2 py-3 justify-center' : 'px-4 py-3'}
                          rounded-lg transition-colors
                          ${isActive(item.path)
                            ? 'bg-accent text-white'
                            : 'text-primary-700 hover:bg-primary-100'}
                        `}
                        title={isCollapsed ? item.label : undefined}
                      >
                        <item.icon className="h-5 w-5 flex-shrink-0" />
                        {!isCollapsed && <span>{item.label}</span>}
                      </Link>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </nav>

        {/* 底部：AI 状态指示器 + 版本信息 */}
        <div className={`border-t border-primary-200 ${isCollapsed ? 'p-2' : 'p-4'} space-y-2`}>
          {/* AI 状态指示器 */}
          {aiReady !== null && (
            <div
              className={`flex items-center gap-2 ${isCollapsed ? 'justify-center' : ''}`}
              title={isCollapsed ? (aiReady ? `AI 就绪: ${aiInfo?.provider}` : 'AI 未配置') : undefined}
            >
              <span
                className={`inline-block h-2 w-2 rounded-full flex-shrink-0 ${
                  aiReady ? 'bg-status-success' : 'bg-primary-300'
                }`}
              />
              {!isCollapsed && (
                <span className="text-xs text-muted-foreground truncate">
                  {aiReady ? `${aiInfo?.provider || 'AI'} 就绪` : 'AI 未配置'}
                </span>
              )}
            </div>
          )}

          {/* 版本信息 */}
          {!isCollapsed && (
            <p className="text-xs text-primary-500 text-center">
              版本 v{__APP_VERSION__}
            </p>
          )}
        </div>
      </aside>
    </>
  );
}