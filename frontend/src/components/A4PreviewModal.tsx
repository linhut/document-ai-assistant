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
 */
import { useState, useEffect } from 'react';
import { X, ZoomIn, ZoomOut, RefreshCw, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { apiClient, downloadFile } from '@/api/client';

interface DocParagraph {
  text: string;
  role?: string;
  is_heading: boolean;
  heading_level?: number;
  format: {
    alignment?: string;
    first_line_indent_pt?: number;
    font_name?: string;
    font_size_pt?: number;
    line_spacing_pt?: number;
    bold?: boolean;
    color?: string;
  };
  runs?: { text: string; bold?: boolean; font_name?: string }[];
}

interface DocTableCellPara {
  text: string;
  format: { alignment?: string; font_name?: string; font_size_pt?: number; bold?: boolean };
}

interface DocTableCell {
  row: number;
  col: number;
  text: string;
  paragraphs: DocTableCellPara[];
}

interface DocTable {
  index: number;
  rows: number;
  cols: number;
  cells: DocTableCell[];
  insert_after_index?: number;
}

interface A4PreviewModalProps {
  docId?: number;
  templateId?: string;
  templateName?: string;
  refreshKey?: number;
  onClose: () => void;
}

const FONT_MAP: Record<string, string> = {
  '方正小标宋简体': '"方正小标宋简体", "FZXiaoBiaoSong-B05S", serif',
  '方正小标宋_GBK': '"方正小标宋简体", "FZXiaoBiaoSong-B05S", serif',
  '黑体': '"黑体", "SimHei", sans-serif',
  '楷体_GB2312': '"楷体_GB2312", "KaiTi", serif',
  '楷体': '"楷体", "KaiTi", serif',
  '仿宋_GB2312': '"仿宋_GB2312", "FangSong", serif',
  '仿宋': '"仿宋", "FangSong", serif',
  '宋体': '"宋体", "SimSun", serif',
  'Times New Roman': '"Times New Roman", serif',
};

function getFontFamily(name?: string): string {
  if (!name) return '"仿宋_GB2312", "FangSong", serif';
  return FONT_MAP[name] || `"${name}", serif`;
}

export default function A4PreviewModal({ docId, templateId, templateName, refreshKey, onClose }: A4PreviewModalProps) {
  const [paragraphs, setParagraphs] = useState<DocParagraph[]>([]);
  const [tables, setTables] = useState<DocTable[]>([]);
  const [pageSetup, setPageSetup] = useState({ margin_top_mm: 37, margin_bottom_mm: 35, margin_left_mm: 28, margin_right_mm: 26 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [zoom, setZoom] = useState(80);

  const isTemplateMode = !!templateId;
  const titleText = isTemplateMode ? `模板预览 — ${templateName || templateId}` : 'A4 预览';
  const subtitleText = isTemplateMode ? '模板排版效果预览' : 'GB/T 9704 标准排版';

  useEffect(() => {
    loadData();
  }, [docId, templateId, refreshKey]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');

      let resp: any;
      if (isTemplateMode) {
        resp = await apiClient.post(`/api/templates/${templateId}/preview`, {}, { timeout: 30000 });
      } else if (docId) {
        resp = await apiClient.get(`/api/documents/${docId}/preview`);
      } else {
        setError('未指定预览目标');
        return;
      }

      setParagraphs(resp.paragraphs || []);
      setTables(resp.tables || []);
      setPageSetup(resp.page_setup || pageSetup);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || '预览加载失败';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  /* 按 role 分离结构 */
  const title = paragraphs.find(p => p.role === 'title' || (p.is_heading && p.heading_level === 0));
  const recipient = paragraphs.find(p => p.role === 'recipient');
  const body = paragraphs.filter(p =>
    p.role === 'body' || p.role === 'attachment' ||
    (p.is_heading && p.heading_level && p.heading_level >= 1 && p.role !== 'title')
  );
  const signature = paragraphs.find(p => p.role === 'signature');
  const date = paragraphs.find(p => p.role === 'date');

  /* 版头智能检测：通过红色文本识别发文机关标志，通过正则识别发文字号 */
  const DOC_NUMBER_RE = /[一-龥]+发(?:〔\d{4}〕|[（(]\d{4}[）)])\d+号/;
  const headerOrg = paragraphs.find(p => {
    const c = p.format.color?.toUpperCase();
    return c && (c === 'CC0000' || c === 'FF0000' || c === 'C00000' || c === 'E00000');
  });
  // 发文字号：排除已识别为标题/版头的段落，匹配标准格式
  const headerDocNum = paragraphs.find(p =>
    p !== headerOrg && p !== title && DOC_NUMBER_RE.test(p.text.trim())
  );
  const hasHeader = !!(headerOrg || headerDocNum);
  // 版记检测
  const ccPara = paragraphs.find(p => p.role === 'cc');
  const hasFooter = !!ccPara;

  /* 渲染单个段落 */
  const renderP = (p: DocParagraph, key: number) => {
    const fs = p.format.font_size_pt || 16;
    const ff = getFontFamily(p.format.font_name);
    const lh = p.format.line_spacing_pt ? `${p.format.line_spacing_pt}pt` : '29pt';
    const indent = p.format.first_line_indent_pt ? `${p.format.first_line_indent_pt}pt` : undefined;
    let align: string = p.format.alignment || 'left';

    const style: React.CSSProperties = {
      fontSize: `${fs}pt`, fontFamily: ff, lineHeight: lh,
      textAlign: align as any, textIndent: indent,
      margin: 0, padding: 0,
    };

    if (p.is_heading && p.heading_level === 0) {
      Object.assign(style, { fontSize: '22pt', fontFamily: '"方正小标宋简体", serif', textAlign: 'center', textIndent: '0' });
    } else if (p.is_heading && p.heading_level === 1) {
      Object.assign(style, { fontFamily: '"黑体", "SimHei", sans-serif', textIndent: '0' });
    } else if (p.is_heading && p.heading_level === 2) {
      Object.assign(style, { fontFamily: '"楷体_GB2312", "KaiTi", serif', textIndent: '0' });
    } else if (p.is_heading && p.heading_level === 3) {
      Object.assign(style, { fontFamily: '"仿宋_GB2312", "FangSong", serif' });
      // 不再整段加粗，由 run 级别控制
    }

    // 空行处理
    const isEmpty = !p.text || p.text.trim() === '';
    if (isEmpty) {
      style.lineHeight = '0.6';
      style.minHeight = `${(p.format.line_spacing_pt || 29) * 0.5}pt`;
    }

    // 按 run 渲染：每个 run 有独立的加粗状态
    if (p.runs && p.runs.length > 1) {
      return (
        <p key={key} style={style}>
          {p.runs.map((r, ri) => (
            <span key={ri} style={{ fontWeight: r.bold ? 'bold' : undefined }}>{r.text}</span>
          ))}
        </p>
      );
    }
    return <p key={key} style={style}>{p.text || ' '}</p>;
  };

  /* 渲染表格 */
  const renderTable = (table: DocTable, key: number) => {
    const cellMap: Record<string, DocTableCell> = {};
    for (const c of table.cells) { cellMap[`${c.row}-${c.col}`] = c; }
    return (
      <table key={`table-${key}`} style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12pt', fontFamily: '"仿宋_GB2312", "FangSong", serif', lineHeight: '20pt', margin: '0.5em 0' }}>
        <tbody>
          {Array.from({ length: table.rows }, (_, r) => (
            <tr key={r}>
              {Array.from({ length: table.cols }, (_, c) => {
                const cell = cellMap[`${r}-${c}`];
                const cellText = cell?.paragraphs?.map(cp => cp.text).join('') || cell?.text || '';
                const isHeader = r === 0;
                return (
                  <td key={c} style={{ border: '1px solid #000', padding: '3pt 5pt', textAlign: isHeader ? 'center' : 'left', fontWeight: isHeader ? 'bold' : undefined, fontFamily: isHeader ? '"黑体", "SimHei", sans-serif' : undefined, verticalAlign: 'top' }}>
                    {cellText}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  /* 按 insert_after_index 交错渲染 body + tables */
  const renderBodyWithTables = () => {
    const filtered = body.filter(p => p !== headerOrg && p !== headerDocNum);
    if (tables.length === 0) return filtered.map((p, i) => renderP(p, i));

    const tableMap: Record<number, DocTable[]> = {};
    for (const t of tables) {
      const idx = t.insert_after_index ?? -1;
      if (!tableMap[idx]) tableMap[idx] = [];
      tableMap[idx].push(t);
    }
    const elements: React.ReactNode[] = [];
    filtered.forEach((p, i) => {
      elements.push(renderP(p, i));
      if (tableMap[i]) { for (const t of tableMap[i]) elements.push(renderTable(t, i)); }
    });
    return elements;
  };

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
            {!isTemplateMode && docId && (
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
            <div
              style={{
                transform: `scale(${zoom / 100})`,
                transformOrigin: 'top center',
              }}
            >
              <div style={{
                width: '210mm',
                minHeight: '297mm',
                padding: `${pageSetup.margin_top_mm}mm ${pageSetup.margin_right_mm}mm ${pageSetup.margin_bottom_mm}mm ${pageSetup.margin_left_mm}mm`,
                background: 'white',
                boxShadow: '0 2px 16px rgba(0,0,0,0.2)',
                margin: '0 auto',
                position: 'relative',
                fontFamily: '"仿宋_GB2312", "FangSong", serif',
                fontSize: '16pt',
                lineHeight: '29pt',
                color: '#000',
              }}>
                {/* === 版头区域（自动检测 + gongwen 项目数值对齐） === */}
                {hasHeader && (
                  <div style={{ marginBottom: '58pt' }}>
                    {headerOrg && (
                      <p style={{
                        fontSize: '30pt',
                        fontFamily: '"方正小标宋简体", "FZXiaoBiaoSong-B05S", serif',
                        color: '#E00000',
                        textAlign: 'center',
                        margin: '0',
                        padding: '0',
                        lineHeight: '1.4',
                        letterSpacing: '0',
                      }}>
                        {headerOrg.text}
                      </p>
                    )}
                    {headerDocNum && (
                      <p style={{
                        fontSize: `${headerDocNum.format.font_size_pt || 16}pt`,
                        fontFamily: getFontFamily(headerDocNum.format.font_name),
                        textAlign: 'center',
                        margin: `${29 * 2}pt 0 4pt 0`,
                        lineHeight: `${headerDocNum.format.line_spacing_pt || 29}pt`,
                      }}>
                        {headerDocNum.text}
                      </p>
                    )}
                    <hr style={{ border: 'none', borderTop: '2px solid #E00000', margin: '0' }} />
                  </div>
                )}

                {title && renderP(title, -1)}
                {recipient && renderP(recipient, -2)}
                {renderBodyWithTables()}

                {(signature || date) && (
                  <div style={{ marginTop: '3em' }}>
                    {signature && renderP({ ...signature, format: { ...signature.format, alignment: 'right' } }, -3)}
                    {date && renderP({ ...date, format: { ...date.format, alignment: 'right' } }, -4)}
                  </div>
                )}

                {/* === 版记区域（自动检测：role=cc） === */}
                {hasFooter && (
                  <div style={{ marginTop: '1em' }}>
                    <hr style={{ border: 'none', borderTop: '2px solid #000', margin: '0 0 0.5em 0' }} />
                    {ccPara && (
                      <p style={{
                        fontSize: '14pt',
                        fontFamily: getFontFamily(ccPara.format.font_name),
                        paddingLeft: '1em', margin: 0,
                        lineHeight: `${ccPara.format.line_spacing_pt || 29}pt`,
                      }}>
                        {ccPara.text}
                      </p>
                    )}
                    <hr style={{ border: 'none', borderTop: '1px solid #000', margin: '0.5em 0 0 0' }} />
                  </div>
                )}

                {/* 页码 — GB/T 9704: 四号宋体/Times New Roman */}
                <div style={{
                  position: 'absolute',
                  bottom: `${pageSetup.margin_bottom_mm - 7}mm`,
                  left: 0, right: 0,
                  textAlign: 'center',
                  fontSize: '14pt',
                  fontFamily: '"宋体", "SimSun", "Times New Roman", serif',
                  color: '#000',
                  letterSpacing: '0.5pt',
                }}>
                  — 1 —
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
