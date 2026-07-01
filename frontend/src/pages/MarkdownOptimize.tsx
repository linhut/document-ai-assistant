/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/*
 * MarkdownOptimize — Markdown 公文优化页面（Module A）
 *
 * 左侧（360px）：Markdown 编辑器 + 文种选择
 * 右侧：A4 实时预览（只读）
 *
 * 核心定位：内容创作。格式精修通过「发送到 A4 编排」完成。
 */
import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import {
  Eye, Download, ZoomIn, ZoomOut, Loader2, Wand2, Pen,
  Settings2, ChevronLeft, Send,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/api/client';
import { downloadFromPost, buildPreviewPayload } from '@/lib/download';
import A4PageRenderer from '@/components/A4PageRenderer';
import {
  useLightConfig, DEFAULT_CONFIG,
} from '@/hooks/useDocumentConfig';
import type { DocParagraph, DocTable } from '@/lib/types';

/* ------------------------------------------------------------------ */
/*  模块级预览缓存 — 比 sessionStorage 更可靠                          */
/*  EnhancedA4Preview 通过 URL 参数 cache=<key> 读取                   */
/*  最大缓存 100 条，每条 5 分钟 TTL 自动过期                           */
/* ------------------------------------------------------------------ */

interface CacheEntry {
  paragraphs: DocParagraph[];
  tables: DocTable[];
  page_setup: Record<string, number>;
  doc_type?: string;
  template_name?: string;
  expiresAt: number;
}

const PREVIEW_CACHE_MAX = 100;
const PREVIEW_CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

const previewCache = new Map<string, CacheEntry>();

function cacheSet(key: string, value: Omit<CacheEntry, 'expiresAt'>): void {
  // Evict expired entries first
  const now = Date.now();
  for (const [k, v] of previewCache) {
    if (v.expiresAt <= now) previewCache.delete(k);
  }
  // Evict oldest if over capacity
  while (previewCache.size >= PREVIEW_CACHE_MAX) {
    const firstKey = previewCache.keys().next().value;
    if (firstKey !== undefined) previewCache.delete(firstKey);
    else break;
  }
  previewCache.set(key, { ...value, expiresAt: now + PREVIEW_CACHE_TTL_MS });
}

export function getCachedPreview(key: string) {
  const entry = previewCache.get(key);
  previewCache.delete(key);  // 一次性读取，读后清除
  if (!entry) return undefined;
  if (Date.now() > entry.expiresAt) return undefined;
  return {
    paragraphs: entry.paragraphs,
    tables: entry.tables,
    page_setup: entry.page_setup,
    doc_type: entry.doc_type,
    template_name: entry.template_name,
  };
}

/* ------------------------------------------------------------------ */
/*  主页面包装器                                                        */
/* ------------------------------------------------------------------ */

export default function MarkdownOptimize() {
  const navigate = useNavigate();
  const { config, patch } = useLightConfig();

  const [paragraphs, setParagraphs] = useState<DocParagraph[]>([]);
  const [tables, setTables] = useState<DocTable[]>([]);
  const [error, setError] = useState('');
  const [zoom, setZoom] = useState(85);
  const [panelOpen, setPanelOpen] = useState(true);

  // Markdown 输入状态
  const [markdownText, setMarkdownText] = useState('');
  const [markdownDocType, setMarkdownDocType] = useState('notice');
  const [generating, setGenerating] = useState(false);
  const [polishing, setPolishing] = useState(false);
  const [showSyntaxHelp, setShowSyntaxHelp] = useState(false);
  const [textareaHeight, setTextareaHeight] = useState(280);

  // 拖拽调整编辑区高度
  const dragRef = useRef<{ startY: number; startH: number } | null>(null);
  const handleDragStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    dragRef.current = { startY: e.clientY, startH: textareaHeight };
    const handleMove = (ev: MouseEvent) => {
      if (!dragRef.current) return;
      const delta = ev.clientY - dragRef.current.startY;
      setTextareaHeight(Math.min(Math.max(dragRef.current.startH + delta, 120), window.innerHeight * 0.5));
    };
    const handleUp = () => { dragRef.current = null; document.removeEventListener('mousemove', handleMove); document.removeEventListener('mouseup', handleUp); };
    document.addEventListener('mousemove', handleMove);
    document.addEventListener('mouseup', handleUp);
  }, [textareaHeight]);

  // 文种列表
  const [docTypes, setDocTypes] = useState<Array<{ id: string; name: string }>>([]);
  useEffect(() => {
    apiClient.get<{ templates?: Array<{ id: string; name: string; enabled?: boolean }> }>('/api/templates/list').then(resp => {
      const templates = resp?.templates || [];
      const types = templates
        .filter((t: any) => t.enabled !== false)
        .map((t: any) => ({ id: t.id, name: t.name || t.id }));
      if (types.length > 0) setDocTypes(types);
    }).catch((err) => {
      console.error('Failed to load document types:', err);
      setDocTypes([
        { id: 'notice', name: '通知' }, { id: 'request', name: '请示' },
        { id: 'report', name: '报告' }, { id: 'letter', name: '函' },
        { id: 'decision', name: '决定' }, { id: 'announcement', name: '通告' },
        { id: 'notice_public', name: '公告' }, { id: 'meeting', name: '会议纪要' },
      ]);
    });
  }, []);

  const patchRef = useRef(patch);
  patchRef.current = patch;

  // 文种名称（用于下载文件名）
  const docTypeName = useMemo(() => {
    const found = docTypes.find(dt => dt.id === markdownDocType);
    return found?.name || '公文';
  }, [docTypes, markdownDocType]);

  // 生成预览
  const handleGenerate = useCallback(async () => {
    if (!markdownText.trim()) return;
    setGenerating(true);
    setError('');
    try {
      const resp = await apiClient.post<{
        success: boolean;
        paragraphs?: DocParagraph[];
        tables?: DocTable[];
        page_setup?: Record<string, number>;
      }>('/api/optimize/markdown-to-preview', {
        markdown_text: markdownText,
        doc_type: markdownDocType,
      }, { timeout: 30000 });
      if (resp.success && resp.paragraphs) {
        setParagraphs(resp.paragraphs);
        setTables(resp.tables || []);
        if (resp.page_setup) {
          const ps = resp.page_setup;
          const mt = ps.margin_top_mm / 10;
          const mb = ps.margin_bottom_mm / 10;
          const ml = ps.margin_left_mm / 10;
          const mr = ps.margin_right_mm / 10;
          patchRef.current({
            margins: {
              top: (mt > 0 && !isNaN(mt)) ? mt : DEFAULT_CONFIG.margins.top,
              bottom: (mb > 0 && !isNaN(mb)) ? mb : DEFAULT_CONFIG.margins.bottom,
              left: (ml > 0 && !isNaN(ml)) ? ml : DEFAULT_CONFIG.margins.left,
              right: (mr > 0 && !isNaN(mr)) ? mr : DEFAULT_CONFIG.margins.right,
            },
          });
        }
      }
    } catch (err: any) {
      setError(err?.message || '生成失败');
    } finally {
      setGenerating(false);
    }
  }, [markdownText, markdownDocType]);

  // AI 润色
  const handleAIPolish = useCallback(async () => {
    if (!markdownText.trim()) return;
    setPolishing(true);
    setError('');
    try {
      const resp = await apiClient.post<{ success: boolean; text?: string; message?: string }>('/api/optimize/ai-polish', {
        text: markdownText,
        doc_type: markdownDocType,
      }, { timeout: 120000 });
      if (resp.success && resp.text) {
        setMarkdownText(resp.text);
      } else if (resp.message) {
        setError(resp.message);
      }
    } catch (err: any) {
      setError(err?.message || 'AI 润色失败，请检查 AI 配置');
    } finally {
      setPolishing(false);
    }
  }, [markdownText, markdownDocType]);

  // 发送到 A4 编排 — 使用模块级缓存 + URL 参数
  const handleSendToA4 = useCallback(() => {
    if (paragraphs.length === 0) {
      console.warn('No paragraphs to send. Please generate preview first.');
      return;
    }
    const cacheKey = `md-${Date.now()}`;
    const data = {
      paragraphs,
      tables,
      doc_type: docTypeName,
      template_name: docTypeName,
      page_setup: {
        margin_top_mm: config.margins.top * 10,
        margin_bottom_mm: config.margins.bottom * 10,
        margin_left_mm: config.margins.left * 10,
        margin_right_mm: config.margins.right * 10,
      },
    };
    // 1. 写入模块级缓存（最快路径）
    cacheSet(cacheKey, data);
    // 2. 写入 sessionStorage（兼容）
    try {
      sessionStorage.setItem('markdown_preview_data', JSON.stringify(data));
    } catch { /* ignore quota */ }
    // 3. 写入 localStorage（防刷新丢失）
    try {
      localStorage.setItem('markdown_preview_data', JSON.stringify(data));
    } catch { /* ignore quota */ }
    navigate(`/document/enhanced-preview?cache=${cacheKey}`);
  }, [paragraphs, tables, config.margins, docTypeName, navigate]);

  // 下载 docx（注入用户配置，确保与预览一致）
  const handleDownload = useCallback(async () => {
    if (!paragraphs.length) return;
    try {
      const payload = buildPreviewPayload(paragraphs, tables, config);
      await downloadFromPost('/api/optimize/preview-download', payload, `${docTypeName}（Markdown）.docx`);
    } catch (e) {
      console.error('Download failed:', e);
    }
  }, [paragraphs, tables, config, docTypeName]);

  return (
    <div className="h-screen flex flex-col bg-primary-50 overflow-hidden">
      {/* 顶部工具栏 */}
      <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-primary-200 shrink-0">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => setPanelOpen(!panelOpen)}>
            {panelOpen ? <ChevronLeft className="h-4 w-4" /> : <Settings2 className="h-4 w-4" />}
          </Button>
          <Pen className="h-5 w-5 text-accent" />
          <span className="font-semibold text-primary-900">Markdown 公文优化</span>
          {paragraphs.length > 0 && <Badge variant="outline">{paragraphs.length} 段落</Badge>}
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={() => setZoom(z => Math.max(50, z - 10))}><ZoomOut className="h-4 w-4" /></Button>
          <span className="text-xs text-muted-foreground w-10 text-center">{zoom}%</span>
          <Button variant="ghost" size="sm" onClick={() => setZoom(z => Math.min(150, z + 10))}><ZoomIn className="h-4 w-4" /></Button>
          {paragraphs.length > 0 && (
            <>
              <Button variant="ghost" size="sm" onClick={handleDownload} title="下载 .docx">
                <Download className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={handleSendToA4} title="发送到 A4 编排精修">
                <Send className="h-4 w-4" />
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* 左侧面板（360px）— Markdown 编辑器 */}
        {panelOpen && (
          <div className="w-[360px] border-r border-primary-200 bg-white flex flex-col shrink-0 overflow-hidden">
            {/* P0: 文种选择器（固定） */}
            <div className="p-3 pb-2 shrink-0">
              <label className="text-xs text-primary-600 block mb-1">选择文种</label>
              <select value={markdownDocType} onChange={e => setMarkdownDocType(e.target.value)}
                className="w-full border border-primary-200 rounded px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-accent">
                {docTypes.map(dt => <option key={dt.id} value={dt.id}>{dt.name}</option>)}
              </select>
            </div>

            {/* P0: Markdown 编辑区（flex-1 自适应，可拖拽调高） */}
            <div className="px-3 pb-0 shrink-0">
              <label className="text-xs text-primary-600 block mb-1">粘贴 Markdown 内容</label>
            </div>
            <div className="px-3 pb-0 shrink-0" style={{ height: textareaHeight }}>
              <textarea
                value={markdownText} onChange={e => setMarkdownText(e.target.value)}
                placeholder={"# 关于印发XX实施方案的通知\n\n各有关单位：\n\n为贯彻落实...，现将《XX实施方案》印发给你们，请认真执行。\n\n| 序号 | 任务 | 责任单位 |\n|------|------|----------|\n| 1 | 任务一 | XX局 |\n| 2 | 任务二 | XX办 |"}
                className="w-full h-full border border-primary-200 rounded p-2 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-accent resize-none"
              />
            </div>
            {/* 拖拽条 */}
            <div
              onMouseDown={handleDragStart}
              className="h-2 cursor-row-resize flex items-center justify-center hover:bg-primary-50 transition-colors shrink-0"
            >
              <div className="w-8 h-0.5 bg-primary-300 rounded-full" />
            </div>

            {/* P0: 按钮区（固定） */}
            <div className="p-3 space-y-2 shrink-0">
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="flex-1"
                  onClick={handleAIPolish} disabled={polishing || !markdownText.trim()}>
                  {polishing ? (
                    <><Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" /> 润色中...</>
                  ) : (
                    <><Wand2 className="h-3.5 w-3.5 mr-1" /> AI 润色</>
                  )}
                </Button>
                <Button variant="default" size="sm" className="flex-1"
                  onClick={handleGenerate} disabled={generating || !markdownText.trim()}>
                  {generating ? (
                    <><Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" /> 生成中...</>
                  ) : (
                    <><Eye className="h-3.5 w-3.5 mr-1" /> 生成预览</>
                  )}
                </Button>
              </div>
              {paragraphs.length > 0 && (
                <Button variant="outline" size="sm" className="w-full" onClick={handleSendToA4}>
                  <Send className="h-3.5 w-3.5 mr-1" /> 发送到 A4 编排精修
                </Button>
              )}
              {error && (
                <div className="p-2 bg-red-50 border border-red-200 rounded text-xs text-red-600">{error}</div>
              )}
            </div>

            {/* P2: 语法帮助（折叠，独立滚动区） */}
            <div className="flex-1 overflow-y-auto border-t border-primary-100">
              <button
                onClick={() => setShowSyntaxHelp(!showSyntaxHelp)}
                className="w-full flex items-center justify-between px-3 py-2 text-xs font-medium text-primary-500 hover:bg-primary-50 transition-colors"
              >
                <span>💡 语法说明</span>
                <span className={`transform transition-transform text-[10px] ${showSyntaxHelp ? 'rotate-180' : ''}`}>▼</span>
              </button>
              {showSyntaxHelp && (
                <div className="px-3 pb-3 space-y-1 text-xs text-primary-500">
                  <p><code className="bg-primary-100 px-1 rounded"># 标题</code> → 公文标题（二号 22pt）</p>
                  <p><code className="bg-primary-100 px-1 rounded">## 一、</code> → 一级标题（三号 16pt）</p>
                  <p><code className="bg-primary-100 px-1 rounded">**加粗**</code> → 加粗文字</p>
                  <p><code className="bg-primary-100 px-1 rounded">| 列 | 表 |</code> → 自动转为表格</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 右侧 A4 预览 */}
        <div className="flex-1 overflow-auto bg-gray-200 p-6">
          {paragraphs.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-primary-400">
                <Pen className="h-16 w-16 mx-auto mb-4 opacity-30" />
                <p className="text-lg font-medium">在左侧粘贴 Markdown 内容</p>
                <p className="text-sm mt-1">选择文种后点击「生成预览」</p>
              </div>
            </div>
          ) : (
            <A4PageRenderer
              paragraphs={paragraphs}
              tables={tables}
              margins={config.margins}
              bodyFontSize={config.body.fontSize}
              bodyLineSpacing={config.body.lineSpacing}
              titleFontFamily={config.title.fontFamily}
              titleFontSize={config.title.fontSize}
              titleBold={config.title.bold}
              titleAlign={config.title.align}
              heading1FontFamily={config.heading1.fontFamily}
              heading1FontSize={config.heading1.fontSize}
              heading2FontFamily={config.heading2.fontFamily}
              heading2FontSize={config.heading2.fontSize}
              heading3FontFamily={config.heading3.fontFamily}
              heading3FontSize={config.heading3.fontSize}
              heading3Bold={config.special.heading3Bold}
              pageNumberShow={config.pageNumber.show}
              pageNumberPosition={config.pageNumber.position}
              pageNumberFont={config.pageNumber.font}
              firstParaBold={config.special.firstParaBold}
              stamp={config.special.stamp}
              stampImage={config.special.stampImage}
              stampPage={config.special.stampPage}
              zoom={zoom}
              headerConfig={config.header}
              footerNoteConfig={config.footerNote}
            />
          )}
        </div>
      </div>
    </div>
  );
}
