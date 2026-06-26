/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/**
 * Workspace - 公文智能校审工作台
 *
 * Data-driven dashboard that pulls real data from backend APIs.
 * Sections: greeting bar, stats overview, quick actions, recent documents, status bar.
 */
import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Upload,
  Layers,
  FileText,
  Clock,
  ArrowRight,
  Activity,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Search,
  Cpu,
  BookOpen,
  WifiOff,
  TrendingUp,
  Globe,
  GlobeLock,
} from 'lucide-react';
import apiClient from '@/api/client';
import { detectActiveAI } from '@/lib/ai-status';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface DocumentItem {
  id: number;
  filename: string;
  document_type?: string;
  status: string;
  paragraph_count?: number;
  created_at: string;
}

interface HealthResponse {
  status: string;
  version?: string;
}

interface RulesResponse {
  rules: unknown[];
  total: number;
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

/** Format an ISO date string to a human-friendly relative label */
function formatRelativeDate(iso: string): string {
  const date = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60_000);
  const diffHour = Math.floor(diffMs / 3_600_000);
  const diffDay = Math.floor(diffMs / 86_400_000);

  if (diffMin < 1) return '刚刚';
  if (diffMin < 60) return `${diffMin} 分钟前`;
  if (diffHour < 24) return `${diffHour} 小时前`;
  if (diffDay < 7) return `${diffDay} 天前`;
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
}

/** Current date formatted for the greeting bar */
function todayLabel(): string {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  });
}

/** Map document status to a display label and badge variant */
function statusInfo(status: string): { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' | 'p0' | 'p1' | 'p2'; colorClass: string } {
  switch (status) {
    case 'uploaded':
      return { label: '已上传', variant: 'secondary', colorClass: 'bg-status-info text-white' };
    case 'checked':
      return { label: '已校审', variant: 'p1', colorClass: 'bg-status-warning text-white' };
    case 'optimized':
      return { label: '已优化', variant: 'p2', colorClass: 'bg-status-success text-white' };
    case 'error':
      return { label: '处理失败', variant: 'destructive', colorClass: 'bg-status-error text-white' };
    default:
      return { label: status, variant: 'outline', colorClass: '' };
  }
}

/* ------------------------------------------------------------------ */
/*  Stat Card Sub-component                                            */
/* ------------------------------------------------------------------ */

interface StatCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon: React.ElementType;
  iconColorClass: string;
}

function StatCard({ title, value, subtitle, icon: Icon, iconColorClass }: StatCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow border-primary-200">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-primary-600">{title}</p>
            <p className="text-3xl font-bold text-primary-900">{value}</p>
            <p className="text-xs text-primary-500 mt-1">
              {subtitle ?? ' '}
            </p>
          </div>
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${iconColorClass}`}>
            <Icon className="h-5 w-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/* ------------------------------------------------------------------ */
/*  Workspace Component                                                */
/* ------------------------------------------------------------------ */

export default function Workspace() {
  const navigate = useNavigate();

  // Data states
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [healthOk, setHealthOk] = useState<boolean | null>(null);
  const [backendVersion, setBackendVersion] = useState<string>('');
  const [ruleCount, setRuleCount] = useState<number>(0);
  const [aiModel, setAiModel] = useState<string>('');
  const [loading, setLoading] = useState(true);

  // Network access state
  const [webAccess, setWebAccess] = useState(true);
  const [lanUrl, setLanUrl] = useState<string>('');
  const [togglingWeb, setTogglingWeb] = useState(false);

  // Stable refs so the fetch function doesn't change identity on every render
  const stateRef = useRef({ setDocuments, setHealthOk, setBackendVersion, setRuleCount, setAiModel, setLoading });

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      try {
        const [docRes, healthRes, ruleRes, aiRes, netRes] = await Promise.allSettled([
          apiClient.get('/api/documents/?skip=0&limit=50'),
          apiClient.get('/api/health'),
          apiClient.get('/api/rules/?source=all'),
          detectActiveAI(),
          apiClient.get('/api/settings/network'),
        ]);

        if (cancelled) return;

        // Documents
        if (docRes.status === 'fulfilled') {
          const data = docRes.value as DocumentItem[] | { documents?: DocumentItem[] };
          const list = Array.isArray(data)
            ? data
            : ((data as Record<string, unknown>).documents as DocumentItem[] | undefined) ?? [];
          stateRef.current.setDocuments(list);
        }

        // Health
        if (healthRes.status === 'fulfilled') {
          const h = healthRes.value as HealthResponse;
          stateRef.current.setHealthOk(h.status === 'ok');
          stateRef.current.setBackendVersion(h.version ?? '');
        } else {
          stateRef.current.setHealthOk(false);
        }

        // Rules
        if (ruleRes.status === 'fulfilled') {
          const r = ruleRes.value as RulesResponse;
          stateRef.current.setRuleCount(r.total ?? 0);
        }

        // AI config — 自动检测已启用的服务商
        if (aiRes.status === 'fulfilled') {
          const a = aiRes.value;
          stateRef.current.setAiModel(
            a && a.exists && a.active ? `${a.provider ?? 'AI'} / ${a.model ?? '默认'}` : ''
          );
        }

        // Network access status
        if (netRes.status === 'fulfilled') {
          const n = netRes.value as any;
          setWebAccess(n?.web_access_enabled ?? false);
          setLanUrl(n?.lan_url ?? '');
        }

        stateRef.current.setLoading(false);
      } catch {
        if (!cancelled) {
          stateRef.current.setLoading(false);
        }
      }
    }

    void loadDashboard();
    return () => { cancelled = true; };
  }, []);

  /* ---- Toggle web access ---- */
  const handleToggleWebAccess = async () => {
    setTogglingWeb(true);
    try {
      const resp = await apiClient.post('/api/settings/network', { enabled: !webAccess });
      setWebAccess(resp.web_access_enabled);
      setLanUrl(resp.lan_url || '');
    } catch (err) {
      console.error('Toggle web access failed:', err);
    } finally {
      setTogglingWeb(false);
    }
  };

  /* ---- Derived stats ---- */
  const totalDocs = documents.length;
  const reviewedCount = documents.filter(
    (d) => d.status === 'checked' || d.status === 'optimized'
  ).length;
  const optimizedCount = documents.filter((d) => d.status === 'optimized').length;
  // Client-side estimate: each checked/optimized doc has paragraph_count issues on average
  const issuesEstimate = documents.reduce((sum, d) => sum + (d.paragraph_count ?? 0), 0);

  /* ---- Empty state flag ---- */
  const hasDocuments = totalDocs > 0;

  return (
    <div className="w-full bg-background">
      {/* ================================================================ */}
      {/*  Top Greeting Bar                                                 */}
      {/* ================================================================ */}
      <div className="px-4 md:px-6 lg:px-8 pt-6 pb-2">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-primary-900">
              公文智能校审工作台
            </h1>
            <p className="text-sm text-primary-600 mt-1 flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5" />
              {todayLabel()}
            </p>
          </div>
          <div className="flex items-center gap-2 text-sm">
            {healthOk === null ? (
              <span className="flex items-center gap-1.5 text-primary-500">
                <Activity className="h-3.5 w-3.5 animate-pulse" />
                检测中...
              </span>
            ) : healthOk ? (
              <span className="flex items-center gap-1.5 text-status-success">
                <span className="inline-block w-2 h-2 rounded-full bg-status-success animate-pulse" />
                系统运行正常
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-status-error">
                <WifiOff className="h-3.5 w-3.5" />
                后端未连接
              </span>
            )}
          </div>
        </div>
      </div>

      {/* ================================================================ */}
      {/*  Main Content                                                     */}
      {/* ================================================================ */}
      <div className="px-4 md:px-6 lg:px-8 py-6 space-y-8">

        {/* -------------------------------------------------------------- */}
        {/*  Stats Overview                                                  */}
        {/* -------------------------------------------------------------- */}
        <section>
          <h2 className="text-lg font-semibold text-primary-900 mb-4">
            数据概览
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="文档总数"
              value={totalDocs}
              subtitle={totalDocs === 0 ? '上传文档开始使用' : `累计处理 ${totalDocs} 份文档`}
              icon={FileText}
              iconColorClass="bg-primary-100 text-primary-700"
            />
            <StatCard
              title="校审次数"
              value={reviewedCount}
              subtitle={reviewedCount === 0 ? '尚未校审文档' : `${reviewedCount} 份文档已校审`}
              icon={Search}
              iconColorClass="bg-accent-light text-accent"
            />
            <StatCard
              title="发现问题"
              value={issuesEstimate}
              subtitle={issuesEstimate === 0 ? '暂无问题记录' : '段落数估算 (详见校审详情)'}
              icon={AlertTriangle}
              iconColorClass="bg-severity-p1-bg text-severity-p1"
            />
            <StatCard
              title="优化完成"
              value={optimizedCount}
              subtitle={optimizedCount === 0 ? '暂无优化记录' : `${optimizedCount} 份文档已优化`}
              icon={CheckCircle2}
              iconColorClass="bg-status-success/15 text-status-success"
            />
          </div>
        </section>

        {/* -------------------------------------------------------------- */}
        {/*  Quick Actions                                                   */}
        {/* -------------------------------------------------------------- */}
        <section>
          <h2 className="text-lg font-semibold text-primary-900 mb-4">
            快速操作
          </h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Upload */}
            <Link to="/document/process">
              <Card className="hover:shadow-md transition-all cursor-pointer border-primary-200 h-full">
                <CardContent className="pt-6">
                  <div className="w-12 h-12 rounded-lg bg-accent text-white flex items-center justify-center mb-4">
                    <Upload className="h-6 w-6" />
                  </div>
                  <h3 className="font-semibold text-primary-900">上传公文</h3>
                  <p className="text-sm text-primary-600 mt-1">
                    上传 .docx / .doc / .wps 文件开始格式校审
                  </p>
                </CardContent>
              </Card>
            </Link>

            {/* Templates */}
            <Link to="/templates">
              <Card className="hover:shadow-md transition-all cursor-pointer border-primary-200 h-full">
                <CardContent className="pt-6">
                  <div className="w-12 h-12 rounded-lg bg-primary-200 text-primary-800 flex items-center justify-center mb-4">
                    <Layers className="h-6 w-6" />
                  </div>
                  <h3 className="font-semibold text-primary-900">选择模板</h3>
                  <p className="text-sm text-primary-600 mt-1">
                    浏览公文模板，一键套用格式
                  </p>
                </CardContent>
              </Card>
            </Link>

            {/* AI Config */}
            <Link to="/settings/ai">
              <Card className="hover:shadow-md transition-all cursor-pointer border-primary-200 h-full">
                <CardContent className="pt-6">
                  <div className="w-12 h-12 rounded-lg bg-primary-200 text-primary-800 flex items-center justify-center mb-4">
                    <Cpu className="h-6 w-6" />
                  </div>
                  <h3 className="font-semibold text-primary-900">AI 配置</h3>
                  <p className="text-sm text-primary-600 mt-1">
                    配置 AI 模型，启用智能润色
                  </p>
                </CardContent>
              </Card>
            </Link>

            {/* Web Access Toggle */}
            <Card
              className={`hover:shadow-md transition-all cursor-pointer border-primary-200 h-full ${webAccess ? 'ring-2 ring-status-success/30' : ''}`}
              onClick={handleToggleWebAccess}
            >
              <CardContent className="pt-6">
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${webAccess ? 'bg-status-success/15 text-status-success' : 'bg-primary-200 text-primary-600'}`}>
                  {webAccess ? <Globe className="h-6 w-6" /> : <GlobeLock className="h-6 w-6" />}
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-primary-900">网页访问</h3>
                    <p className="text-sm text-primary-600 mt-1">
                      {webAccess ? '其他用户可访问' : '仅本机可访问'}
                    </p>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${webAccess ? 'bg-status-success/15 text-status-success' : 'bg-primary-100 text-primary-500'}`}>
                    {togglingWeb ? '...' : webAccess ? '已开启' : '已关闭'}
                  </div>
                </div>
                {webAccess && (
                  <p className="text-xs text-status-success mt-2 font-mono">
                    http://localhost:5173
                  </p>
                )}
                <p className="text-xs text-primary-400 mt-2">
                  {webAccess ? '点击关闭网页访问' : '点击开启，其他用户可通过浏览器访问'}
                </p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* -------------------------------------------------------------- */}
        {/*  Recent Documents                                                */}
        {/* -------------------------------------------------------------- */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-primary-900">
              最近文档
            </h2>
            {hasDocuments && (
              <Link
                to="/document/process"
                className="text-sm text-accent hover:text-accent-hover flex items-center gap-1 transition-colors"
              >
                查看全部
                <ArrowRight className="h-4 w-4" />
              </Link>
            )}
          </div>

          {loading ? (
            <Card className="border-primary-200">
              <CardContent className="py-12 flex flex-col items-center justify-center text-center">
                <Activity className="h-8 w-8 text-primary-400 animate-spin mb-3" />
                <p className="text-sm text-primary-500">加载文档数据...</p>
              </CardContent>
            </Card>
          ) : !hasDocuments ? (
            /* Empty state */
            <Card className="border-primary-200 border-dashed">
              <CardContent className="py-16 flex flex-col items-center justify-center text-center">
                <div className="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center mb-4">
                  <BookOpen className="h-8 w-8 text-primary-400" />
                </div>
                <h3 className="text-base font-semibold text-primary-800 mb-1">
                  暂无文档
                </h3>
                <p className="text-sm text-primary-500 mb-6 max-w-xs">
                  上传您的第一份公文，系统将自动检测格式问题并提供优化建议
                </p>
                <Link to="/document/process">
                  <Button>
                    <Upload className="h-4 w-4 mr-2" />
                    上传公文
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ) : (
            <Card className="border-primary-200">
              <CardContent className="p-0">
                {documents.slice(0, 8).map((doc, index) => {
                  const si = statusInfo(doc.status);
                  return (
                    <div
                      key={doc.id}
                      onClick={() =>
                        navigate(`/document/check?docId=${doc.id}`)
                      }
                      className={`flex items-center gap-3 md:gap-4 px-4 md:px-6 py-4 hover:bg-primary-50 transition-colors cursor-pointer ${
                        index !== Math.min(documents.length, 8) - 1
                          ? 'border-b border-primary-100'
                          : ''
                      }`}
                    >
                      <FileText className="h-8 w-8 md:h-10 md:w-10 text-accent flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-primary-900 truncate">
                          {doc.filename}
                        </h3>
                        <div className="flex items-center gap-2 md:gap-3 mt-1 flex-wrap">
                          <Badge className={`text-xs ${si.colorClass}`}>
                            {si.label}
                          </Badge>
                          {doc.document_type && (
                            <span className="text-xs text-primary-500">
                              {doc.document_type}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-primary-500 flex-shrink-0">
                        <Clock className="h-4 w-4 hidden sm:block" />
                        <span>{formatRelativeDate(doc.created_at)}</span>
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          )}
        </section>
      </div>

      {/* ================================================================ */}
      {/*  Bottom Status Bar                                                */}
      {/* ================================================================ */}
      <div className="px-4 md:px-6 lg:px-8 pb-6">
        <div className="flex flex-wrap items-center justify-between gap-4 text-xs text-primary-500 border-t border-primary-200 pt-4">
          <div className="flex items-center gap-4 flex-wrap">
            <span className="flex items-center gap-1.5">
              <Cpu className="h-3.5 w-3.5" />
              AI 模型: {aiModel || '未配置'}
            </span>
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="h-3.5 w-3.5" />
              校审规则: {ruleCount} 条
            </span>
          </div>
          <span className="flex items-center gap-1.5">
            <TrendingUp className="h-3.5 w-3.5" />
            系统版本: v{__APP_VERSION__}
            {backendVersion && ` / 后端 ${backendVersion}`}
          </span>
        </div>
      </div>
    </div>
  );
}
