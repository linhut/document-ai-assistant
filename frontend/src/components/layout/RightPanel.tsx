/**
 * RightPanel - 右侧辅助面板（280px，静态渲染）
 * 由 AppLayout 控制是否渲染（≥1440px 时渲染）
 * 不含自身 visibility 逻辑，渲染即可见
 */
import { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';
import {
  Activity, Cpu, Shield, Type, Info, BookOpen, Sparkles,
  Upload, Lightbulb, ChevronRight, BarChart3, LayoutTemplate,
  Compass, CheckCircle2, FileText, Settings, Home,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { detectActiveAI, type AIStatus } from '@/lib/ai-status';
import apiClient from '@/api/client';

/* ------------------------------------------------------------------ */
/*  通用辅助组件                                                        */
/* ------------------------------------------------------------------ */

function StatusDot({ active }: { active: boolean }) {
  return <span className={cn('inline-block h-2 w-2 rounded-full', active ? 'bg-status-success' : 'bg-primary-300')} />;
}

function InfoRow({ icon: Icon, label, value }: { icon: React.ComponentType<{ className?: string }>; label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2.5 py-1.5">
      <Icon className="h-3.5 w-3.5 text-primary-400 flex-shrink-0" />
      <span className="text-xs text-muted-foreground flex-1">{label}</span>
      <span className="text-xs font-medium text-foreground">{value}</span>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  页面专属内容                                                        */
/* ------------------------------------------------------------------ */

/** 工作台：系统状态 */
function SystemStatus() {
  const [ai, setAi] = useState<AIStatus | null>(null);
  const [rules, setRules] = useState<number>(0);
  const [fonts, setFonts] = useState<number>(0);

  useEffect(() => {
    let ok = true;
    Promise.allSettled([
      detectActiveAI(),
      apiClient.get('/api/rules/?source=all'),
      apiClient.get('/api/settings/fonts'),
    ]).then(([aiR, ruleR, fontR]) => {
      if (!ok) return;
      if (aiR.status === 'fulfilled') setAi(aiR.value);
      if (ruleR.status === 'fulfilled') {
        const d = ruleR.value as any;
        setRules(Array.isArray(d) ? d.length : d?.total ?? 0);
      }
      if (fontR.status === 'fulfilled') {
        const d = fontR.value as any;
        setFonts(Array.isArray(d) ? d.length : d?.total ?? 0);
      }
    });
    return () => { ok = false; };
  }, []);

  return (
    <div className="space-y-4">
      <div className="rounded-lg bg-primary-50 p-3 space-y-1.5">
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-accent" />
          <span className="text-xs font-medium">AI 模型</span>
          {ai !== null && <StatusDot active={ai.active} />}
        </div>
        <p className="text-xs text-muted-foreground">{ai ? `${ai.provider} · ${ai.model}` : '未配置'}</p>
      </div>
      <InfoRow icon={Shield} label="规则引擎" value={`${rules} 条`} />
      <InfoRow icon={Type} label="字体库" value={`${fonts} 个`} />
      <InfoRow icon={Info} label="版本" value={`v${__APP_VERSION__}`} />
    </div>
  );
}

/** 文档处理：助手提示 */
function DocAssistant() {
  const [templates, setTemplates] = useState<{ id: string; name: string }[]>([]);
  useEffect(() => {
    apiClient.get('/api/templates/list')
      .then(r => setTemplates((Array.isArray(r) ? r : (r as any)?.templates || []).slice(0, 3)))
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center gap-2 mb-2">
          <BookOpen className="h-3.5 w-3.5 text-accent" />
          <span className="text-xs font-medium">推荐模板</span>
        </div>
        {templates.length > 0 ? templates.map((t, i) => (
          <Link key={t.id || i} to="/templates"
            className="flex items-center gap-2 px-2.5 py-2 rounded-lg bg-primary-50 hover:bg-primary-100 text-xs text-muted-foreground mb-1.5 transition-colors">
            <FileText className="h-3.5 w-3.5 text-primary-400 flex-shrink-0" />
            <span className="truncate flex-1">{t.name}</span>
            <ChevronRight className="h-3 w-3 text-primary-300" />
          </Link>
        )) : <p className="text-xs text-muted-foreground">暂无模板</p>}
      </div>
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="h-3.5 w-3.5 text-accent" />
          <span className="text-xs font-medium">AI 能力</span>
        </div>
        <ul className="text-xs text-muted-foreground space-y-1.5">
          <li>· 智能识别公文格式问题</li>
          <li>· 自动匹配 GB/T 9704 标准</li>
          <li>· 一键修正全部格式错误</li>
        </ul>
      </div>
    </div>
  );
}

/** 校审中心：统计 */
function CheckStats() {
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.split('?')[1] || '');
    const docId = params.get('docId');
    if (!docId) return;
    apiClient.get(`/api/check/${docId}/results`).then(r => {
      const items: any[] = Array.isArray(r) ? r : [];
      const c: Record<string, number> = {};
      items.forEach(i => { const s = i.severity || '?'; c[s] = (c[s] || 0) + 1; });
      setCounts(c);
      setTotal(items.length);
    }).catch(() => {});
  }, []);

  const sevs = [
    { k: 'P0', label: 'P0 严重', color: 'bg-severity-p0' },
    { k: 'P1', label: 'P1 瑕疵', color: 'bg-severity-p1' },
    { k: 'P2', label: 'P2 建议', color: 'bg-severity-p2' },
  ];

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-1">
        <BarChart3 className="h-3.5 w-3.5 text-accent" />
        <span className="text-xs font-medium">问题分布</span>
        <span className="ml-auto text-sm font-bold text-foreground">{total}</span>
      </div>
      {sevs.map(s => (
        <div key={s.k} className="flex items-center gap-2">
          <span className={cn('h-2.5 w-2.5 rounded-sm', s.color)} />
          <span className="text-xs text-muted-foreground flex-1">{s.label}</span>
          <span className="text-xs font-semibold">{counts[s.k] || 0}</span>
        </div>
      ))}
    </div>
  );
}

/** 模板中心：分类统计 */
function TemplateStats() {
  const [total, setTotal] = useState(0);
  const [cats, setCats] = useState<Record<string, number>>({});

  useEffect(() => {
    apiClient.get('/api/templates/list').then(r => {
      const items: any[] = Array.isArray(r) ? r : (r as any)?.templates || [];
      setTotal(items.length);
      const c: Record<string, number> = {};
      items.forEach(t => { const cat = t.category || '未分类'; c[cat] = (c[cat] || 0) + 1; });
      setCats(c);
    }).catch(() => {});
  }, []);

  return (
    <div className="space-y-3">
      <div className="rounded-lg bg-primary-50 p-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <LayoutTemplate className="h-4 w-4 text-accent" />
          <span className="text-xs font-medium">模板总数</span>
        </div>
        <span className="text-lg font-bold">{total}</span>
      </div>
      {Object.entries(cats).map(([cat, count]) => (
        <div key={cat} className="flex items-center justify-between px-2 py-1.5 rounded bg-primary-50">
          <span className="text-xs text-muted-foreground">{cat}</span>
          <span className="text-xs font-semibold">{count}</span>
        </div>
      ))}
    </div>
  );
}

/** 默认：快速导航 */
function QuickNav() {
  const loc = useLocation();
  const links = [
    { icon: Home, label: '工作台', path: '/workspace' },
    { icon: FileText, label: '文档处理', path: '/document/process' },
    { icon: CheckCircle2, label: '校审中心', path: '/document/check' },
    { icon: LayoutTemplate, label: '模板中心', path: '/templates' },
    { icon: Settings, label: 'AI 设置', path: '/settings/ai' },
  ];
  return (
    <div className="space-y-1">
      {links.map(({ icon: Icon, label, path }) => {
        const active = loc.pathname === path;
        return (
          <Link key={path} to={path}
            className={cn('flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs transition-colors',
              active ? 'bg-accent text-white' : 'text-muted-foreground hover:bg-primary-50')}>
            <Icon className="h-4 w-4 flex-shrink-0" />
            <span className="flex-1">{label}</span>
            {!active && <ChevronRight className="h-3 w-3 text-primary-300" />}
          </Link>
        );
      })}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  路由 → 内容映射                                                    */
/* ------------------------------------------------------------------ */

function usePanelConfig() {
  const path = useLocation().pathname;
  if (path === '/' || path === '/workspace') return { title: '系统状态', icon: Activity, Content: SystemStatus };
  if (path === '/document/process') return { title: '文档助手', icon: Sparkles, Content: DocAssistant };
  if (path === '/document/check') return { title: '校审统计', icon: BarChart3, Content: CheckStats };
  if (path === '/templates') return { title: '模板信息', icon: LayoutTemplate, Content: TemplateStats };
  return { title: '快速导航', icon: Compass, Content: QuickNav };
}

/* ------------------------------------------------------------------ */
/*  主组件：纯静态面板，无visibility逻辑                                  */
/* ------------------------------------------------------------------ */

export default function RightPanel() {
  const { title, icon: PageIcon, Content } = usePanelConfig();

  return (
    <aside className="w-[280px] h-full bg-white border-l border-primary-200 flex-shrink-0 overflow-y-auto">
      <div className="p-4 space-y-4">
        {/* 面板标题 */}
        <div className="flex items-center gap-2 pb-2 border-b border-primary-100">
          <PageIcon className="h-4 w-4 text-accent" />
          <h3 className="text-sm font-semibold">{title}</h3>
        </div>
        {/* 面板内容 */}
        <Content />
      </div>
    </aside>
  );
}
