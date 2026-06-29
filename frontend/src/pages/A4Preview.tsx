/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */

/**
 * A4Preview - A4 分页预览页面
 * 从优化后的文档渲染实时 A4 预览
 *
 * 使用统一的 A4PageRenderer 组件渲染，通过 remapParagraphRoles
 * 兼容旧数据中缺少 header_org/header_number 角色的段落。
 */
import { useState, useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Loader2, FileText, Download, ZoomIn, ZoomOut } from 'lucide-react';
import PageHeader from '@/components/layout/PageHeader';
import { Button } from '@/components/ui/button';
import { apiClient, downloadFile } from '@/api/client';
import { remapParagraphRoles } from '@/lib/role-remap';
import A4PageRenderer from '@/components/A4PageRenderer';
import type { DocParagraph, DocTable } from '@/lib/types';

export default function A4Preview() {
  const [searchParams] = useSearchParams();
  const docId = searchParams.get('docId');
  const [paragraphs, setParagraphs] = useState<DocParagraph[]>([]);
  const [tables, setTables] = useState<DocTable[]>([]);
  const [pageSetup, setPageSetup] = useState({
    margin_top_mm: 37, margin_bottom_mm: 35, margin_left_mm: 28, margin_right_mm: 26,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [zoom, setZoom] = useState(100);

  useEffect(() => {
    if (docId) loadDocument(parseInt(docId));
  }, [docId]);

  const loadDocument = async (id: number) => {
    try {
      setLoading(true);
      const resp = await apiClient.get<{ paragraphs?: DocParagraph[]; tables?: DocTable[]; page_setup?: typeof pageSetup }>(`/api/documents/${id}/preview`);
      setParagraphs(resp.paragraphs || []);
      setTables(resp.tables || []);
      setPageSetup(resp.page_setup || pageSetup);
    } catch {
      setError('无法加载文档预览');
    } finally {
      setLoading(false);
    }
  };

  /* ---- 角色映射 ---- */
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

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-primary-50">
        <Loader2 className="h-8 w-8 animate-spin text-accent" />
      </div>
    );
  }

  if (error || (!paragraphs.length && !loading)) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-primary-50">
        <div className="text-center">
          <FileText className="h-12 w-12 text-primary-300 mx-auto mb-3" />
          <p className="text-muted-foreground">{error || '文档无段落内容'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full bg-primary-50 min-h-screen">
      <PageHeader
        title="A4 预览"
        description="GB/T 9704 标准排版预览"
        actions={
          <div className="flex gap-2 items-center">
            <Button variant="outline" size="sm" onClick={() => setZoom(z => Math.max(50, z - 10))}>
              <ZoomOut className="h-4 w-4" />
            </Button>
            <span className="text-sm text-muted-foreground w-12 text-center">{zoom}%</span>
            <Button variant="outline" size="sm" onClick={() => setZoom(z => Math.min(150, z + 10))}>
              <ZoomIn className="h-4 w-4" />
            </Button>
            {docId && (
              <Button variant="outline" size="sm" onClick={() => downloadFile(`/api/optimize/${docId}/download`, `preview_${docId}.docx`)}>
                <Download className="h-4 w-4 mr-1" />下载
              </Button>
            )}
          </div>
        }
      />

      <div className="p-8">
        <A4PageRenderer
          paragraphs={remappedParagraphs}
          tables={tables}
          margins={margins}
          zoom={zoom}
        />
      </div>
    </div>
  );
}
