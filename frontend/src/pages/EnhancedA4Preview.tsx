/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */

/**
 * EnhancedA4Preview — 增强版 A4 预览页面
 *
 * 左侧：格式设置面板（边距/字体/版头版记/规则预览）
 * 右侧：实时 A4 预览（设置改动即时反映）
 *
 * 入口：
 * - ?docId=123  → 从后端加载已上传文档
 * - ?templateId=notice → 从后端加载模板规则生成预览
 */
import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Settings2, Eye, RotateCcw, Download, ChevronLeft, ChevronRight,
  ZoomIn, ZoomOut, FileText, Loader2, Wand2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/api/client';
import {
  DocumentConfigProvider, useDocumentConfig, DEFAULT_CONFIG,
  type DocumentConfig,
} from '@/hooks/useDocumentConfig';

/* ------------------------------------------------------------------ */
/*  字体映射                                                           */
/* ------------------------------------------------------------------ */

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

function ff(name?: string): string {
  if (!name) return '"仿宋_GB2312", "FangSong", serif';
  return FONT_MAP[name] || `"${name}", serif`;
}

/* ------------------------------------------------------------------ */
/*  段落数据结构                                                        */
/* ------------------------------------------------------------------ */

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
  };
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

/* ------------------------------------------------------------------ */
/*  独立表单组件（定义在组件外部，避免重渲染导致输入失焦）                    */
/* ------------------------------------------------------------------ */

const SettingsSection = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <div>
    <h4 className="text-xs font-semibold text-primary-500 uppercase tracking-wider mb-2">{title}</h4>
    <div className="space-y-2">{children}</div>
  </div>
);

const NumberField = ({ label, value, onChange, min, max, step = 1, suffix }: {
  label: string; value: number; onChange: (v: number) => void;
  min?: number; max?: number; step?: number; suffix?: string;
}) => (
  <div className="flex items-center gap-2">
    <label className="text-xs text-primary-600 w-10 shrink-0">{label}</label>
    <input
      type="number" value={value}
      onChange={e => onChange(parseFloat(e.target.value) || 0)}
      min={min} max={max} step={step}
      className="flex-1 border border-primary-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-accent"
    />
    {suffix && <span className="text-xs text-primary-400">{suffix}</span>}
  </div>
);

const SelectField = ({ label, value, options, onChange }: {
  label: string; value: string; options: string[]; onChange: (v: string) => void;
}) => (
  <div className="flex items-center gap-2">
    <label className="text-xs text-primary-600 w-10 shrink-0">{label}</label>
    <select value={value} onChange={e => onChange(e.target.value)}
      className="flex-1 border border-primary-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-accent">
      {options.map(o => <option key={o} value={o}>{o}</option>)}
    </select>
  </div>
);

/** 带防抖的文本输入（解决逐字输入卡顿问题） */
function TextField({ label, value, onChange, placeholder, hint }: {
  label: string; value: string; onChange: (v: string) => void; placeholder?: string; hint?: string;
}) {
  const [local, setLocal] = useState(value);
  const timer = useRef<ReturnType<typeof setTimeout>>();

  // 外部 value 变化时同步到 local
  useEffect(() => { setLocal(value); }, [value]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const v = e.target.value;
    setLocal(v);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => onChange(v), 300);
  }, [onChange]);

  useEffect(() => () => clearTimeout(timer.current), []);

  return (
    <div>
      <div className="flex items-center gap-2">
        <label className="text-xs text-primary-600 w-14 shrink-0">{label}</label>
        <input
          type="text" value={local} onChange={handleChange} placeholder={placeholder}
          className="flex-1 border border-primary-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-accent"
        />
      </div>
      {hint && <p className="text-[10px] text-primary-400 mt-0.5 ml-14">{hint}</p>}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  主页面包装器                                                        */
/* ------------------------------------------------------------------ */

export default function EnhancedA4PreviewPage() {
  return (
    <DocumentConfigProvider>
      <EnhancedA4PreviewInner />
    </DocumentConfigProvider>
  );
}

/* ------------------------------------------------------------------ */
/*  内部组件                                                            */
/* ------------------------------------------------------------------ */

function EnhancedA4PreviewInner() {
  const [searchParams] = useSearchParams();
  const docId = searchParams.get('docId');
  const templateId = searchParams.get('templateId');

  const { config, patch, reset } = useDocumentConfig();

  const [paragraphs, setParagraphs] = useState<DocParagraph[]>([]);
  const [tables, setTables] = useState<DocTable[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [panelOpen, setPanelOpen] = useState(true);
  const [zoom, setZoom] = useState(85);
  const [activeTab, setActiveTab] = useState<'format' | 'rules'>('format');
  const [converting, setConverting] = useState(false);

  // 一键优化 Markdown（用 useCallback 稳定引用，避免 SettingsPanel 重建）
  const paragraphsRef = useRef(paragraphs);
  paragraphsRef.current = paragraphs;

  const handleConvertMarkdown = useCallback(async () => {
    setConverting(true);
    try {
      const resp = await apiClient.post('/api/optimize/convert-markdown', {
        paragraphs: paragraphsRef.current.map(p => ({
          text: p.text, role: p.role, is_heading: p.is_heading,
          heading_level: p.heading_level, format: p.format,
        })),
      }, { timeout: 30000 });
      console.log('[Markdown转换] 响应:', { success: resp.success, paragraphs: resp.paragraphs?.length, tables: resp.tables?.length, tableRows: resp.tables?.[0]?.rows, tableCols: resp.tables?.[0]?.cols });
      if (resp.success && resp.paragraphs) {
        setParagraphs(resp.paragraphs);
        if (resp.tables && resp.tables.length > 0) {
          console.log('[Markdown转换] 设置表格:', resp.tables);
          setTables(resp.tables);
        }
      }
    } catch (err) {
      console.error('[Markdown转换] 失败:', err);
    } finally {
      setConverting(false);
    }
  }, []);

  // 从后端加载数据
  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        let resp: any;
        if (templateId) {
          resp = await apiClient.post(`/api/templates/${templateId}/preview`, {}, { timeout: 30000 });
        } else if (docId) {
          resp = await apiClient.get(`/api/documents/${docId}/preview`);
        } else {
          setError('未指定文档或模板');
          return;
        }
        if (cancelled) return;
        setParagraphs(resp.paragraphs || []);
        if (resp.page_setup) {
          patch({
            margins: {
              top: resp.page_setup.margin_top_mm / 10 || DEFAULT_CONFIG.margins.top,
              bottom: resp.page_setup.margin_bottom_mm / 10 || DEFAULT_CONFIG.margins.bottom,
              left: resp.page_setup.margin_left_mm / 10 || DEFAULT_CONFIG.margins.left,
              right: resp.page_setup.margin_right_mm / 10 || DEFAULT_CONFIG.margins.right,
            },
          });
        }
      } catch (err: any) {
        if (!cancelled) setError(err?.response?.data?.detail || '加载失败');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, [docId, templateId]);

  // 分离段落
  const title = paragraphs.find(p => p.role === 'title' || (p.is_heading && p.heading_level === 0));
  const recipient = paragraphs.find(p => p.role === 'recipient');
  const body = paragraphs.filter(p =>
    p.role === 'body' || p.role === 'attachment' ||
    (p.is_heading && p.heading_level && p.heading_level >= 1 && p.role !== 'title')
  );
  const signature = paragraphs.find(p => p.role === 'signature');
  const date = paragraphs.find(p => p.role === 'date');

  /* ---- 渲染单个段落（使用 config 驱动格式） ---- */

  const renderP = (p: DocParagraph, key: number) => {
    let fs = config.body.fontSize;
    let font = ff(config.body.fontFamily);
    let lh = `${config.body.lineSpacing}pt`;
    let indent = config.body.firstLineIndent > 0 ? `${config.body.firstLineIndent * config.body.fontSize}pt` : undefined;
    let align: string = config.body.align;
    let bold: boolean | undefined;

    if (p.is_heading && p.heading_level === 0) {
      fs = config.title.fontSize; font = ff(config.title.fontFamily);
      align = config.title.align; indent = undefined; bold = config.title.bold;
    } else if (p.is_heading && p.heading_level === 1) {
      fs = config.heading1.fontSize; font = ff(config.heading1.fontFamily);
      indent = config.heading1.indent > 0 ? `${config.heading1.indent * config.heading1.fontSize}pt` : undefined;
    } else if (p.is_heading && p.heading_level === 2) {
      fs = config.heading2.fontSize; font = ff(config.heading2.fontFamily);
    } else if (p.is_heading && p.heading_level === 3) {
      fs = config.heading3.fontSize; font = ff(config.heading3.fontFamily); bold = config.heading3.bold;
    }

    const style: React.CSSProperties = {
      fontSize: `${fs}pt`, fontFamily: font, lineHeight: lh,
      textAlign: align as any, textIndent: indent,
      margin: 0, padding: 0, fontWeight: bold ? 'bold' : undefined,
    };
    // 空行处理：无文字时用紧凑行高，避免多余空白
    const isEmpty = !p.text || p.text.trim() === '';
    if (isEmpty) {
      style.lineHeight = '0.6';
      style.minHeight = `${config.body.lineSpacing * 0.5}pt`;
    }
    return <p key={key} style={style}>{p.text || ' '}</p>;
  };

  /* ---- 渲染表格（markdown 转换生成的 Table 对象） ---- */

  const renderTable = (table: DocTable, key: number) => {
    const cellMap: Record<string, DocTableCell> = {};
    for (const c of table.cells) {
      cellMap[`${c.row}-${c.col}`] = c;
    }
    return (
      <table key={`table-${key}`} style={{
        width: '100%', borderCollapse: 'collapse',
        fontSize: `${Math.max(config.body.fontSize - 2, 12)}pt`,
        fontFamily: ff(config.body.fontFamily),
        lineHeight: `${config.body.lineSpacing}pt`,
        margin: '0.5em 0',
      }}>
        <tbody>
          {Array.from({ length: table.rows }, (_, r) => (
            <tr key={r}>
              {Array.from({ length: table.cols }, (_, c) => {
                const cell = cellMap[`${r}-${c}`];
                const cellText = cell?.paragraphs?.map(cp => cp.text).join('') || cell?.text || '';
                const isHeader = r === 0;
                return (
                  <td key={c} style={{
                    border: '1px solid #000',
                    padding: '4pt 6pt',
                    textAlign: isHeader ? 'center' : 'left',
                    fontWeight: isHeader ? 'bold' : undefined,
                    fontFamily: ff(isHeader ? '黑体' : config.body.fontFamily),
                    verticalAlign: 'top',
                  }}>
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

  // 用 ref 绑定 config/patch，让 SettingsPanel 函数引用完全稳定
  const configRef = useRef(config);
  configRef.current = config;
  const patchRef = useRef(patch);
  patchRef.current = patch;
  const resetRef = useRef(reset);
  resetRef.current = reset;

  /* ---- 设置面板（函数引用稳定，不会导致子组件重建） ---- */

  const SettingsPanel = useMemo(() => () => {
    const cfg = configRef.current;
    const p = patchRef.current;
    const rst = resetRef.current;
    return (
    <div className="space-y-4 text-sm">
      {/* 一键优化 Markdown */}
      <button
        onClick={handleConvertMarkdown}
        disabled={converting}
        className="w-full flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg bg-accent text-white text-sm font-medium hover:bg-accent-hover transition-colors disabled:opacity-50"
      >
        {converting ? (
          <><Loader2 className="h-4 w-4 animate-spin" /> 正在转换...</>
        ) : (
          <><Wand2 className="h-4 w-4" /> 一键优化 Markdown</>
        )}
      </button>
      <p className="text-[10px] text-primary-400 text-center">
        识别 # 标题、**加粗**、列表等 Markdown 语法并转为公文格式
      </p>

      {/* 页边距 */}
      <SettingsSection title="页边距 (cm)">
        <div className="grid grid-cols-2 gap-2">
          <NumberField label="上" value={cfg.margins.top} onChange={v => p({ margins: { ...cfg.margins, top: v } })} min={1} max={5} step={0.1} />
          <NumberField label="下" value={cfg.margins.bottom} onChange={v => p({ margins: { ...cfg.margins, bottom: v } })} min={1} max={5} step={0.1} />
          <NumberField label="左" value={cfg.margins.left} onChange={v => p({ margins: { ...cfg.margins, left: v } })} min={1} max={5} step={0.1} />
          <NumberField label="右" value={cfg.margins.right} onChange={v => p({ margins: { ...cfg.margins, right: v } })} min={1} max={5} step={0.1} />
        </div>
      </SettingsSection>

      {/* 公文标题 */}
      <SettingsSection title="公文标题">
        <SelectField label="字体" value={cfg.title.fontFamily} options={['方正小标宋简体', '黑体', '宋体']} onChange={v => p({ title: { ...cfg.title, fontFamily: v } })} />
        <NumberField label="字号" value={cfg.title.fontSize} onChange={v => p({ title: { ...cfg.title, fontSize: v } })} min={12} max={36} step={1} suffix="pt" />
      </SettingsSection>

      {/* 正文 */}
      <SettingsSection title="正文">
        <SelectField label="字体" value={cfg.body.fontFamily} options={['仿宋_GB2312', '宋体', '楷体_GB2312']} onChange={v => p({ body: { ...cfg.body, fontFamily: v } })} />
        <NumberField label="字号" value={cfg.body.fontSize} onChange={v => p({ body: { ...cfg.body, fontSize: v } })} min={10} max={24} step={1} suffix="pt" />
        <NumberField label="行距" value={cfg.body.lineSpacing} onChange={v => p({ body: { ...cfg.body, lineSpacing: v } })} min={20} max={40} step={0.5} suffix="pt" />
        <NumberField label="缩进" value={cfg.body.firstLineIndent} onChange={v => p({ body: { ...cfg.body, firstLineIndent: v } })} min={0} max={4} step={0.5} suffix="em" />
      </SettingsSection>

      {/* 版头设置 */}
      <SettingsSection title="版头设置">
        <label className="flex items-center gap-2 mb-2">
          <input type="checkbox" checked={cfg.header.enabled} onChange={e => p({ header: { ...cfg.header, enabled: e.target.checked } })} className="w-4 h-4" />
          <span className="font-medium">启用版头</span>
        </label>
        {cfg.header.enabled && (
          <div className="space-y-2 ml-1 pl-3 border-l-2 border-primary-100">
            <TextField label="发文机关" value={cfg.header.orgName} onChange={v => p({ header: { ...cfg.header, orgName: v } })} placeholder="国务院办公厅文件" hint="全称+文件，红色方正小标宋居中" />
            <TextField label="发文字号" value={cfg.header.docNumber} onChange={v => p({ header: { ...cfg.header, docNumber: v } })} placeholder="国办发〔2024〕1号" hint="机关代字〔年份〕序号号，六角括号" />
            <TextField label="签发人" value={cfg.header.signer} onChange={v => p({ header: { ...cfg.header, signer: v } })} placeholder="张三" hint="仅上行文，签发人三字仿宋+姓名楷体" />
          </div>
        )}
      </SettingsSection>

      {/* 版记设置 */}
      <SettingsSection title="版记设置">
        <label className="flex items-center gap-2 mb-2">
          <input type="checkbox" checked={cfg.footerNote.enabled} onChange={e => p({ footerNote: { ...cfg.footerNote, enabled: e.target.checked } })} className="w-4 h-4" />
          <span className="font-medium">启用版记</span>
        </label>
        {cfg.footerNote.enabled && (
          <div className="space-y-2 ml-1 pl-3 border-l-2 border-primary-100">
            <TextField label="抄送" value={cfg.footerNote.cc} onChange={v => p({ footerNote: { ...cfg.footerNote, cc: v } })} placeholder="XX局，XX办" hint="抄送机关名称" />
            <TextField label="印发机关" value={cfg.footerNote.printer} onChange={v => p({ footerNote: { ...cfg.footerNote, printer: v } })} placeholder="XX市人民政府办公室" hint="版记最下方左侧" />
            <TextField label="印发日期" value={cfg.footerNote.printDate} onChange={v => p({ footerNote: { ...cfg.footerNote, printDate: v } })} placeholder="2026年1月1日" hint="版记最下方右侧，与印发机关同行" />
          </div>
        )}
      </SettingsSection>

      {/* 恢复默认 */}
      <Button variant="outline" size="sm" className="w-full" onClick={rst}>
        <RotateCcw className="h-3 w-3 mr-1" /> 恢复默认（GB/T 9704）
      </Button>
    </div>
    );
  }, [converting, handleConvertMarkdown]);

  /* ---- 规则预览 ---- */

  const RulesPanel = useMemo(() => () => {
    const rules = [
      { label: '标题', font: config.title.fontFamily, size: `${config.title.fontSize}pt`, align: config.title.align },
      { label: '正文', font: config.body.fontFamily, size: `${config.body.fontSize}pt`, spacing: `${config.body.lineSpacing}pt`, indent: `${config.body.firstLineIndent}em` },
      { label: '一级标题', font: config.heading1.fontFamily, size: `${config.heading1.fontSize}pt` },
      { label: '二级标题', font: config.heading2.fontFamily, size: `${config.heading2.fontSize}pt` },
      { label: '三级标题', font: config.heading3.fontFamily, size: `${config.heading3.fontSize}pt`, bold: config.heading3.bold ? '加粗' : '' },
      { label: '页边距', value: `上${config.margins.top} 下${config.margins.bottom} 左${config.margins.left} 右${config.margins.right} cm` },
      ...(config.header.enabled ? [{ label: '版头', value: config.header.orgName || '（未填写）' }] : []),
      ...(config.footerNote.enabled ? [{ label: '版记', value: `抄送: ${config.footerNote.cc || '无'}` }] : []),
    ];
    return (
      <div className="space-y-2">
        {rules.map((r, i) => (
          <div key={i} className="flex items-center justify-between py-1.5 px-2 bg-primary-50 rounded text-xs">
            <span className="font-medium text-primary-700">{r.label}</span>
            <span className="text-primary-500 text-right">
              {r.font && `${r.font} `}
              {r.size && `${r.size} `}
              {r.spacing && `行距${r.spacing} `}
              {r.indent && `缩进${r.indent} `}
              {r.align && `${r.align} `}
              {r.bold && `${r.bold} `}
              {r.value}
            </span>
          </div>
        ))}
      </div>
    );
  }, [config]);

  /* ---- 主渲染 ---- */

  if (loading) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-primary-50">
        <Loader2 className="h-8 w-8 animate-spin text-accent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-primary-50">
        <div className="text-center">
          <FileText className="h-12 w-12 text-primary-300 mx-auto mb-3" />
          <p className="text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-primary-50 overflow-hidden">
      {/* 顶部工具栏 */}
      <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-primary-200 shrink-0">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => setPanelOpen(!panelOpen)}>
            {panelOpen ? <ChevronLeft className="h-4 w-4" /> : <Settings2 className="h-4 w-4" />}
          </Button>
          <span className="font-semibold text-primary-900">A4 实时预览</span>
          <Badge variant="outline">{paragraphs.length} 段落</Badge>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={() => setZoom(z => Math.max(50, z - 10))}><ZoomOut className="h-4 w-4" /></Button>
          <span className="text-xs text-muted-foreground w-10 text-center">{zoom}%</span>
          <Button variant="ghost" size="sm" onClick={() => setZoom(z => Math.min(150, z + 10))}><ZoomIn className="h-4 w-4" /></Button>
          <Button variant="ghost" size="sm" onClick={async () => {
            try {
              const blob = await apiClient.post('/api/optimize/preview-download', {
                paragraphs: paragraphs.map(p => ({ text: p.text, role: p.role, is_heading: p.is_heading, heading_level: p.heading_level, format: p.format })),
                tables: tables.length > 0 ? tables : undefined,
                page_setup: { margin_top_mm: config.margins.top * 10, margin_bottom_mm: config.margins.bottom * 10, margin_left_mm: config.margins.left * 10, margin_right_mm: config.margins.right * 10 },
              }, { responseType: 'blob' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a'); a.href = url; a.download = '公文预览.docx';
              document.body.appendChild(a); a.click(); document.body.removeChild(a);
              URL.revokeObjectURL(url);
            } catch (e) { console.error('Preview download failed:', e); }
          }} title="下载预览文档">
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* 左侧设置面板 */}
        {panelOpen && (
          <div className="w-80 border-r border-primary-200 bg-white overflow-y-auto shrink-0">
            <div className="flex border-b border-primary-200 sticky top-0 bg-white z-10">
              <button className={`flex-1 py-2 text-sm font-medium ${activeTab === 'format' ? 'text-accent border-b-2 border-accent' : 'text-primary-500'}`} onClick={() => setActiveTab('format')}>
                <Settings2 className="h-3.5 w-3.5 inline mr-1" /> 格式设置
              </button>
              <button className={`flex-1 py-2 text-sm font-medium ${activeTab === 'rules' ? 'text-accent border-b-2 border-accent' : 'text-primary-500'}`} onClick={() => setActiveTab('rules')}>
                <Eye className="h-3.5 w-3.5 inline mr-1" /> 规则预览
              </button>
            </div>
            <div className="p-3">
              {activeTab === 'format' ? <SettingsPanel /> : <RulesPanel />}
            </div>
          </div>
        )}

        {/* 右侧 A4 预览 */}
        <div className="flex-1 overflow-auto bg-gray-200 p-6">
          <div style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top center' }}>
            <div style={{
              width: '210mm', minHeight: '297mm',
              padding: `${config.margins.top}cm ${config.margins.right}cm ${config.margins.bottom}cm ${config.margins.left}cm`,
              background: 'white', boxShadow: '0 2px 16px rgba(0,0,0,0.2)',
              margin: '0 auto', position: 'relative',
              fontFamily: ff(config.body.fontFamily), fontSize: `${config.body.fontSize}pt`,
              lineHeight: `${config.body.lineSpacing}pt`, color: '#000',
            }}>
              {/* === 版头区域（GB/T 9704-2012 标准，间距对齐 gongwen 项目） === */}
              {config.header.enabled && (
                <div style={{ marginBottom: `${config.body.lineSpacing * 2}pt` }}>
                  {/* 发文机关标志 — 红色方正小标宋简体，居中，30pt */}
                  {config.header.orgName && (
                    <p style={{
                      fontSize: '30pt',
                      fontFamily: ff('方正小标宋简体'),
                      color: '#E00000',
                      textAlign: 'center',
                      margin: '0',
                      padding: '0',
                      lineHeight: '1.4',
                      letterSpacing: '0',
                    }}>
                      {config.header.orgName}
                    </p>
                  )}

                  {/* 发文字号 + 签发人 — 标志下空二行 */}
                  {(config.header.docNumber || config.header.signer) && (
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'baseline',
                      marginTop: `${config.body.lineSpacing * 2}pt`, // 下空二行
                      marginBottom: '4pt', // 反线上方紧凑间距
                      fontSize: `${config.body.fontSize}pt`,
                      lineHeight: `${config.body.lineSpacing}pt`,
                      fontFamily: ff(config.body.fontFamily),
                      // 有签发人时发文字号居左空一字，无签发人时居中
                      paddingLeft: config.header.signer ? '1em' : '0',
                    }}>
                      {/* 左侧：发文字号 */}
                      <span style={{ textAlign: config.header.signer ? 'left' : 'center', flex: 1 }}>
                        {config.header.docNumber}
                      </span>
                      {/* 右侧：签发人（仅上行文） */}
                      {config.header.signer && (
                        <span style={{ whiteSpace: 'nowrap', paddingRight: '1em' }}>
                          <span style={{ fontFamily: ff(config.body.fontFamily) }}>签发人：</span>
                          <span style={{ fontFamily: ff('楷体_GB2312') }}>{config.header.signer}</span>
                        </span>
                      )}
                    </div>
                  )}

                  {/* 红色反线（版头与正文的分隔线）— 反线下空二行到标题 */}
                  <hr style={{ border: 'none', borderTop: '2px solid #E00000', margin: '0' }} />
                </div>
              )}

              {/* 正文 + 表格（按 insert_after_index 交错渲染） */}
              {title && renderP(title, -1)}
              {recipient && renderP(recipient, -2)}
              {(() => {
                // 构建 insert_after_index → tables 映射
                const tableMap: Record<number, DocTable[]> = {};
                for (const t of tables) {
                  const idx = t.insert_after_index ?? -1;
                  if (!tableMap[idx]) tableMap[idx] = [];
                  tableMap[idx].push(t);
                }
                const elements: React.ReactNode[] = [];
                body.forEach((p, i) => {
                  elements.push(renderP(p, i));
                  // 在该段落之后插入对应的表格
                  if (tableMap[i]) {
                    for (const t of tableMap[i]) {
                      elements.push(renderTable(t, i));
                    }
                  }
                });
                // 插入在文档开头的表格（insert_after_index = -1）
                if (tableMap[-1]) {
                  for (const t of tableMap[-1]) {
                    elements.push(renderTable(t, -1));
                  }
                }
                // 插入在文档末尾的表格（insert_after_index 超出 body 范围）
                const maxIdx = body.length - 1;
                for (const [key, tList] of Object.entries(tableMap)) {
                  if (Number(key) > maxIdx && Number(key) !== -1) {
                    for (const t of tList) {
                      elements.push(renderTable(t, Number(key)));
                    }
                  }
                }
                return elements;
              })()}
              {/* 表格提示信息 */}
              {tables.length > 0 && (
                <div style={{ margin: '0.5em 0', padding: '4px 8px', background: '#f0f9ff', border: '1px solid #bae6fd', borderRadius: '4px', fontSize: '10pt', color: '#0369a1', textAlign: 'center' }}>
                  已识别 {tables.length} 个表格（共 {tables.reduce((s, t) => s + t.rows, 0)} 行 × {tables[0]?.cols || 0} 列）
                </div>
              )}

              {(signature || date) && (
                <div style={{ marginTop: '3em' }}>
                  {signature && renderP({ ...signature, format: { ...signature.format, alignment: 'right' } }, -3)}
                  {date && renderP({ ...date, format: { ...date.format, alignment: 'right' } }, -4)}
                </div>
              )}

              {/* 版记 — GB/T 9704: 四号仿宋，抄送左空一字 */}
              {config.footerNote.enabled && (
                <div style={{ marginTop: '1em' }}>
                  <hr style={{ border: 'none', borderTop: '2px solid #000', margin: '0 0 0.5em 0' }} />
                  {config.footerNote.cc && (
                    <p style={{ fontSize: `${config.body.fontSize - 2}pt`, fontFamily: ff(config.body.fontFamily), paddingLeft: '1em', margin: 0, lineHeight: `${config.body.lineSpacing}pt` }}>
                      抄送：{config.footerNote.cc}
                    </p>
                  )}
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.3em' }}>
                    {config.footerNote.printer && (
                      <span style={{ fontSize: `${config.body.fontSize - 2}pt`, fontFamily: ff(config.body.fontFamily), paddingLeft: '1em' }}>
                        {config.footerNote.printer}
                      </span>
                    )}
                    {config.footerNote.printDate && (
                      <span style={{ fontSize: `${config.body.fontSize - 2}pt`, fontFamily: ff(config.body.fontFamily), paddingRight: '1em' }}>
                        {config.footerNote.printDate}
                      </span>
                    )}
                  </div>
                  <hr style={{ border: 'none', borderTop: '1px solid #000', margin: '0.5em 0 0 0' }} />
                </div>
              )}

              {/* 页码 — GB/T 9704: 四号宋体/Times New Roman，— X — 格式 */}
              {config.pageNumber.show && (
                <div style={{
                  position: 'absolute', bottom: `${config.margins.bottom - 0.7}cm`,
                  left: 0, right: 0, textAlign: 'center',
                  fontSize: '14pt', fontFamily: '"宋体", "SimSun", "Times New Roman", serif',
                  letterSpacing: '0.5pt',
                }}>
                  — 1 —
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
