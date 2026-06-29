/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */

/**
 * A4PreviewModal - A4 预览弹窗
 * 支持两种模式：
 *   1. 文档预览：传入 docId，从 /api/documents/{id}/preview 加载
 *   2. 模板预览：传入 templateId，从 /api/templates/{id}/preview 加载
 *
 * 使用统一的 A4PageRenderer 组件渲染，通过 remapParagraphRoles
 * 兼容旧数据中缺少 header_org/header_number 角色的段落。
 */
import { useState, useEffect, useMemo } from 'react';
import { X, ZoomIn, ZoomOut, RefreshCw, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { apiClient, downloadFile } from '@/api/client';
import { downloadFromPost } from '@/lib/download';
import { remapParagraphRoles } from '@/lib/role-remap';
import A4PageRenderer from '@/components/A4PageRenderer';
import type { DocParagraph, DocTable } from '@/lib/types';

/* ------------------------------------------------------------------ */
/*  Props                                                              */
/* ------------------------------------------------------------------ */

interface A4PreviewModalProps {
  docId?: number;
  templateId?: string;
  templateName?: string;
  refreshKey?: number;
  canDownload?: boolean;
  onClose: () => void;
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */

export default function A4PreviewModal({
  docId, templateId, templateName, refreshKey, canDownload, onClose,
}: A4PreviewModalProps) {
  const [paragraphs, setParagraphs] = useState<DocParagraph[]>([]);
  const [tables, setTables] = useState<DocTable[]>([]);
  const [pageSetup, setPageSetup] = useState({
    margin_top_mm: 37, margin_bottom_mm: 35, margin_left_mm: 28, margin_right_mm: 26,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [zoom, setZoom] = useState(80);

  const isTemplateMode = !!templateId;
  const titleText = isTemplateMode ? `模板预览 — ${templateName || templateId}` : 'A4 预览';
  const subtitleText = isTemplateMode ? '模板排版效果预览' : 'GB/T 9704 标准排版';

  /* ---- 数据加载 ---- */

  const loadData = async (signal?: AbortSignal) => {
    try {
      setLoading(true);
      setError('');

      let resp: any;
      if (isTemplateMode) {
        resp = await apiClient.post(`/api/templates/${templateId}/preview`, {}, { timeout: 30000, signal });
      } else if (docId) {
        resp = await apiClient.get(`/api/documents/${docId}/preview`, { signal });
      } else {
        setError('未指定预览目标');
        return;
      }

      if (!signal?.aborted) {
        setParagraphs(resp.paragraphs || []);
        setTables(resp.tables || []);
        setPageSetup(resp.page_setup || pageSetup);
      }
    } catch (err: any) {
      if (err?.name === 'CanceledError' || err?.code === 'ERR_CANCELED') return;
      const msg = err?.response?.data?.detail || err?.message || '预览加载失败';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    loadData(controller.signal);
    return () => controller.abort();
  }, [docId, templateId, refreshKey]);

  /* ---- 角色映射：兼容旧数据（缺少 header_org/header_number） ---- */

  const remappedParagraphs = useMemo(
    () => remapParagraphRoles(paragraphs),
    [paragraphs],
  );

  /* ---- 页边距转换：mm → cm ---- */

  const margins = useMemo(() => ({
    top: pageSetup.margin_top_mm / 10,
    bottom: pageSetup.margin_bottom_mm / 10,
    left: pageSetup.margin_left_mm / 10,
    right: pageSetup.margin_right_mm / 10,
  }), [pageSetup]);

  /* ---- 下载处理 ---- */

  const handleTemplateDownload = async () => {
    try {
      await downloadFromPost('/api/optimize/preview-download', {
        paragraphs: paragraphs.map(p => ({
          text: p.text, role: p.role, is_heading: p.is_heading,
          heading_level: p.heading_level, format: p.format,
        })),
        tables: tables.length > 0 ? tables : undefined,
        page_setup: pageSetup,
      }, `${templateName || templateId || '模板'}（预览）.docx`);
    } catch (e) {
      console.error('Template download failed:', e);
    }
  };

  /* ---- 渲染 ---- */

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div
        className="bg-white rounded-xl shadow-2xl flex flex-col max-h-[95vh] overflow-hidden"
        style={{ width: '90vw', maxWidth: '900px' }}
        onClick={e => e.stopPropagation()}
      >
        {/* 标题栏 */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-primary-100 bg-primary-50">
          <div className="flex items-center gap-2">
            <span className="font-medium text-primary-900">{titleText}</span>
            <span className="text-xs text-primary-500">{subtitleText}</span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={() => loadData()} title="刷新">
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setZoom(z => Math.max(50, z - 10))}>
              <ZoomOut className="h-4 w-4" />
            </Button>
            <span className="text-xs text-muted-foreground w-10 text-center">{zoom}%</span>
            <Button variant="ghost" size="sm" onClick={() => setZoom(z => Math.min(150, z + 10))}>
              <ZoomIn className="h-4 w-4" />
            </Button>
            {/* 模板模式：从预览数据下载 */}
            {isTemplateMode && paragraphs.length > 0 && (
              <Button variant="ghost" size="sm" onClick={handleTemplateDownload} title="下载模板文档">
                <Download className="h-4 w-4" />
              </Button>
            )}
            {/* 文档模式：从后端下载优化文件（需已优化） */}
            {!isTemplateMode && docId && canDownload && (
              <Button variant="ghost" size="sm" onClick={() => downloadFile(`/api/optimize/${docId}/download`, `optimized_${docId}.docx`)} title="下载">
                <Download className="h-4 w-4" />
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* A4 内容区 */}
        <div className="flex-1 overflow-auto bg-gray-200 p-6">
          {loading ? (
            <div className="text-center py-20 text-muted-foreground">加载中...</div>
          ) : error ? (
            <div className="text-center py-20">
              <p className="text-red-500 mb-3">{error}</p>
              <Button variant="outline" size="sm" onClick={() => loadData()}>重试</Button>
            </div>
          ) : paragraphs.length === 0 ? (
            <div className="text-center py-20 text-muted-foreground">
              <p>暂无预览内容</p>
            </div>
          ) : (
            <A4PageRenderer
              paragraphs={remappedParagraphs}
              tables={tables}
              margins={margins}
              zoom={zoom}
            />
          )}
        </div>
      </div>
    </div>
  );
}
