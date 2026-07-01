/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/*
 * EnhancedA4Preview — A4 实时预览编辑页（Module B）
 *
 * 左侧：格式设置面板（边距/字体/版头版记/特殊选项/高级设置）
 * 右侧：实时 A4 预览（A4PageRenderer 统一组件）
 *
 * 入口：
 * - ?docId=123  → 从后端加载已上传文档
 * - ?templateId=notice → 从后端加载模板规则生成预览
 * - ?from=markdown → 从 sessionStorage 加载 Markdown 模块传递的数据
 */
import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Settings2, Eye, RotateCcw, Download, ChevronLeft,
  ZoomIn, ZoomOut, FileText, Loader2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/api/client';
import { downloadFromPost, buildPreviewPayload } from '@/lib/download';
import A4PageRenderer from '@/components/A4PageRenderer';
import {
  useDocumentConfig, DEFAULT_CONFIG,
} from '@/hooks/useDocumentConfig';
import { CN_FONT_OPTIONS, FONT_SIZE_OPTIONS, formatFontSizeLabel } from '@/lib/gb-t-9704';
import type { DocParagraph, DocTable } from '@/lib/types';
import { getCachedPreview } from '@/pages/MarkdownOptimize';

/* ------------------------------------------------------------------ */
/*  独立表单组件                                                        */
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

const FontSizeField = ({ label, value, onChange }: {
  label: string; value: number; onChange: (v: number) => void;
}) => (
  <div className="flex items-center gap-2">
    <label className="text-xs text-primary-600 w-10 shrink-0">{label}</label>
    <select value={value} onChange={e => onChange(parseInt(e.target.value))}
      className="flex-1 border border-primary-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-accent">
      {FONT_SIZE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
  </div>
);

/** 带防抖的文本输入 */
function TextField({ label, value, onChange, placeholder, hint }: {
  label: string; value: string; onChange: (v: string) => void; placeholder?: string; hint?: string;
}) {
  const [local, setLocal] = useState(value);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);
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

export default function EnhancedA4Preview() {
  const [searchParams] = useSearchParams();
  const docId = searchParams.get('docId');
  const templateId = searchParams.get('templateId');
  const cacheKey = searchParams.get('cache');
  const fromMarkdown = searchParams.get('from') === 'markdown' || !!cacheKey;

  const { config, patch, reset } = useDocumentConfig();

  const [paragraphs, setParagraphs] = useState<DocParagraph[]>([]);
  const [tables, setTables] = useState<DocTable[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [panelOpen, setPanelOpen] = useState(true);
  const [zoom, setZoom] = useState(85);
  const [activeTab, setActiveTab] = useState<'format' | 'rules'>('format');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [docName, setDocName] = useState('公文');

  // 从后端加载数据
  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError('');

      // 优先从模块级缓存读取（MarkdownOptimize 传入），其次 sessionStorage
      if (fromMarkdown) {
        try {
          let data: any = null;
          if (cacheKey) {
            data = getCachedPreview(cacheKey);
          }
          // 兜底：兼容旧版/缓存读不到时从 sessionStorage 取
          if (!data) {
            const raw = sessionStorage.getItem('markdown_preview_data');
            if (raw) {
              data = JSON.parse(raw);
              sessionStorage.removeItem('markdown_preview_data');
            }
          }
          // 第二层兜底：从 localStorage 取（防止刷新页面丢失）
          if (!data) {
            const rawLocal = localStorage.getItem('markdown_preview_data');
            if (rawLocal) {
              data = JSON.parse(rawLocal);
            }
          }
          if (data && !cancelled) {
            setParagraphs(data.paragraphs || []);
            setTables(data.tables || []);
            setDocName(data.doc_type || data.template_name || 'Markdown公文');
            if (data.page_setup) {
              const ps = data.page_setup;
              const mt = ps.margin_top_mm / 10;
              const mb = ps.margin_bottom_mm / 10;
              const ml = ps.margin_left_mm / 10;
              const mr = ps.margin_right_mm / 10;
              patch({
                margins: {
                  top: (mt > 0 && !isNaN(mt)) ? mt : DEFAULT_CONFIG.margins.top,
                  bottom: (mb > 0 && !isNaN(mb)) ? mb : DEFAULT_CONFIG.margins.bottom,
                  left: (ml > 0 && !isNaN(ml)) ? ml : DEFAULT_CONFIG.margins.left,
                  right: (mr > 0 && !isNaN(mr)) ? mr : DEFAULT_CONFIG.margins.right,
                },
              });
            }
            setLoading(false);
            return;
          }
        } catch (e) {
          console.error('Load markdown cache failed:', e);
        }
      }

      try {
        let resp: any;
        if (templateId) {
          resp = await apiClient.post(`/api/templates/${templateId}/preview`, {}, { timeout: 30000 });
          if (!cancelled) setDocName(resp.template_name || templateId || '模板');
        } else if (docId) {
          resp = await apiClient.get(`/api/documents/${docId}/preview`);
          if (!cancelled) setDocName(resp.filename || resp.doc_type || `文档${docId}`);
        } else {
          setError('未指定文档或模板');
          return;
        }
        if (cancelled) return;
        setParagraphs(resp.paragraphs || []);
        setTables(resp.tables || []);
        if (resp.page_setup) {
          const ps = resp.page_setup;
          patch({
            margins: {
              top: ps.margin_top_mm > 0 ? ps.margin_top_mm / 10 : DEFAULT_CONFIG.margins.top,
              bottom: ps.margin_bottom_mm > 0 ? ps.margin_bottom_mm / 10 : DEFAULT_CONFIG.margins.bottom,
              left: ps.margin_left_mm > 0 ? ps.margin_left_mm / 10 : DEFAULT_CONFIG.margins.left,
              right: ps.margin_right_mm > 0 ? ps.margin_right_mm / 10 : DEFAULT_CONFIG.margins.right,
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
  }, [docId, templateId, cacheKey, fromMarkdown]);

  // 用 ref 绑定 config/patch/reset，让 SettingsPanel 函数引用完全稳定
  const configRef = useRef(config);
  configRef.current = config;
  const patchRef = useRef(patch);
  patchRef.current = patch;
  const resetRef = useRef(reset);
  resetRef.current = reset;

  /* ---- 设置面板 ---- */

  const SettingsPanel = useMemo(() => () => {
    const cfg = configRef.current;
    const p = patchRef.current;
    const rst = resetRef.current;
    return (
    <div className="space-y-4 text-sm">
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
        <SelectField label="字体" value={cfg.title.fontFamily} options={CN_FONT_OPTIONS.slice(0, 6)} onChange={v => p({ title: { ...cfg.title, fontFamily: v } })} />
        <FontSizeField label="字号" value={cfg.title.fontSize} onChange={v => p({ title: { ...cfg.title, fontSize: v } })} />
      </SettingsSection>

      {/* 正文 */}
      <SettingsSection title="正文">
        <SelectField label="字体" value={cfg.body.fontFamily} options={CN_FONT_OPTIONS.slice(2, 7)} onChange={v => p({ body: { ...cfg.body, fontFamily: v } })} />
        <FontSizeField label="字号" value={cfg.body.fontSize} onChange={v => p({ body: { ...cfg.body, fontSize: v } })} />
        <NumberField label="行距" value={cfg.body.lineSpacing} onChange={v => p({ body: { ...cfg.body, lineSpacing: v } })} min={20} max={40} step={0.5} suffix="pt" />
        <NumberField label="缩进" value={cfg.body.firstLineIndent} onChange={v => p({ body: { ...cfg.body, firstLineIndent: v } })} min={0} max={4} step={0.5} suffix="em" />
      </SettingsSection>

      {/* 页码设置 */}
      <SettingsSection title="页码设置">
        <label className="flex items-center gap-2 mb-2">
          <input type="checkbox" checked={cfg.pageNumber.show} onChange={e => p({ pageNumber: { ...cfg.pageNumber, show: e.target.checked } })} className="w-4 h-4" />
          <span className="font-medium">显示页码</span>
        </label>
        {cfg.pageNumber.show && (
          <div className="space-y-2 ml-1 pl-3 border-l-2 border-primary-100">
            <div className="flex items-center gap-2">
              <label className="text-xs text-primary-600 w-14 shrink-0">字体</label>
              <select value={cfg.pageNumber.font} onChange={e => p({ pageNumber: { ...cfg.pageNumber, font: e.target.value } })}
                className="flex-1 border border-primary-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-accent">
                <option value="宋体">宋体</option>
                <option value="Times New Roman">Times New Roman</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <label className="text-xs text-primary-600 w-14 shrink-0">样式</label>
              <select value={cfg.pageNumber.position} onChange={e => p({ pageNumber: { ...cfg.pageNumber, position: e.target.value as 'center' | 'right-left' } })}
                className="flex-1 border border-primary-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-accent">
                <option value="center">居中（单面打印）</option>
                <option value="right-left">单右双左（国标）</option>
              </select>
            </div>
          </div>
        )}
      </SettingsSection>

      {/* ====== 高级设置（折叠） ====== */}
      <div>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="w-full flex items-center justify-between py-2 text-xs font-semibold text-primary-500 uppercase tracking-wider"
        >
          <span>高级设置</span>
          <span className={`transform transition-transform ${showAdvanced ? 'rotate-180' : ''}`}>▼</span>
        </button>
        {showAdvanced && (
          <div className="space-y-4 pl-1 border-l-2 border-primary-100 ml-1">
            {/* 版头设置 */}
            <SettingsSection title="版头设置（GB/T 9704 §7.2）">
              <label className="flex items-center gap-2 mb-2">
                <input type="checkbox" checked={cfg.header.enabled} onChange={e => p({ header: { ...cfg.header, enabled: e.target.checked } })} className="w-4 h-4" />
                <span className="font-medium">启用版头</span>
              </label>
              {cfg.header.enabled && (
                <div className="space-y-2 ml-1 pl-3 border-l-2 border-primary-100">
                  <TextField label="发文机关" value={cfg.header.orgName} onChange={v => p({ header: { ...cfg.header, orgName: v } })} placeholder="国务院办公厅文件" hint="红色方正小标宋居中" />
                  <TextField label="发文字号" value={cfg.header.docNumber} onChange={v => p({ header: { ...cfg.header, docNumber: v } })} placeholder="国办发〔2026〕1号" hint="国办发〔2026〕1号" />
                  <TextField label="签发人" value={cfg.header.signer} onChange={v => p({ header: { ...cfg.header, signer: v } })} placeholder="张三" hint="仅上行文" />
                </div>
              )}
            </SettingsSection>

            {/* 版记设置 */}
            <SettingsSection title="版记设置（GB/T 9704 §7.4）">
              <label className="flex items-center gap-2 mb-2">
                <input type="checkbox" checked={cfg.footerNote.enabled} onChange={e => p({ footerNote: { ...cfg.footerNote, enabled: e.target.checked } })} className="w-4 h-4" />
                <span className="font-medium">启用版记</span>
              </label>
              {cfg.footerNote.enabled && (
                <div className="space-y-2 ml-1 pl-3 border-l-2 border-primary-100">
                  <TextField label="抄送" value={cfg.footerNote.cc} onChange={v => p({ footerNote: { ...cfg.footerNote, cc: v } })} placeholder="XX局，XX办" hint="四号仿宋，左空一字" />
                  <TextField label="印发机关" value={cfg.footerNote.printer} onChange={v => p({ footerNote: { ...cfg.footerNote, printer: v } })} placeholder="XX市人民政府办公室" />
                  <TextField label="印发日期" value={cfg.footerNote.printDate} onChange={v => p({ footerNote: { ...cfg.footerNote, printDate: v } })} placeholder="2026年1月1日" />
                </div>
              )}
            </SettingsSection>

            {/* 特殊选项 */}
            <SettingsSection title="特殊选项">
              <label className="flex items-center gap-2">
                <input type="checkbox" checked={cfg.special.firstParaBold} onChange={e => p({ special: { ...cfg.special, firstParaBold: e.target.checked } })} className="w-4 h-4" />
                <span className="text-xs">正文首句加粗</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" checked={cfg.special.heading3Bold} onChange={e => p({ special: { ...cfg.special, heading3Bold: e.target.checked } })} className="w-4 h-4" />
                <span className="text-xs">三级标题加粗</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" checked={cfg.special.stamp} onChange={e => p({ special: { ...cfg.special, stamp: e.target.checked } })} className="w-4 h-4" />
                <span className="text-xs">加盖印章</span>
              </label>
              {cfg.special.stamp && (
                <div className="ml-6 mt-2 space-y-2 p-2 bg-primary-50 rounded">
                  <div>
                    <label className="text-[10px] text-primary-600 block mb-1">上传印章图片（透明底 PNG）</label>
                    <input type="file" accept="image/png" onChange={e => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      if (!file.type.includes('png')) { alert('请上传 PNG 格式图片'); return; }
                      const reader = new FileReader();
                      reader.onload = () => p({ special: { ...cfg.special, stampImage: reader.result as string } });
                      reader.readAsDataURL(file);
                    }} className="text-xs w-full" />
                    {cfg.special.stampImage && (
                      <div className="mt-1 flex items-center gap-2">
                        <img src={cfg.special.stampImage} alt="印章预览" className="w-12 h-12 object-contain border rounded" />
                        <button onClick={() => p({ special: { ...cfg.special, stampImage: '' } })} className="text-xs text-red-500 hover:underline">移除</button>
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="text-[10px] text-primary-600 w-14 shrink-0">盖章页码</label>
                    <input type="number" value={cfg.special.stampPage} onChange={e => p({ special: { ...cfg.special, stampPage: parseInt(e.target.value) || 0 } })} min={0} className="w-16 border border-primary-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-accent" />
                    <span className="text-[10px] text-primary-400">0 = 最后一页</span>
                  </div>
                </div>
              )}
            </SettingsSection>

            {/* 各级标题字体配置 */}
            <SettingsSection title="标题字体配置">
              <p className="text-[10px] text-primary-400 mb-2">一级、二级、三级标题统一在此配置中文字体、英数字体和字号</p>
              {([['heading1', '一级标题'], ['heading2', '二级标题'], ['heading3', '三级标题']] as const).map(([key, label]) => (
                <div key={key} className="mb-3 p-2 bg-primary-50 rounded">
                  <p className="text-xs font-medium text-primary-700 mb-1.5">{label}</p>
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <label className="text-[10px] text-primary-600 w-14 shrink-0">中文字体</label>
                      <select value={cfg[key].fontFamily} onChange={e => p({ [key]: { ...cfg[key], fontFamily: e.target.value } })}
                        className="flex-1 border border-primary-200 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-accent">
                        {CN_FONT_OPTIONS.map(f => <option key={f} value={f}>{f}</option>)}
                      </select>
                    </div>
                    <FontSizeField label="字号" value={cfg[key].fontSize} onChange={v => p({ [key]: { ...cfg[key], fontSize: v } })} />
                  </div>
                </div>
              ))}
            </SettingsSection>
          </div>
        )}
      </div>

      {/* 恢复默认 */}
      <Button variant="outline" size="sm" className="w-full" onClick={rst}>
        <RotateCcw className="h-3 w-3 mr-1" /> 恢复默认（GB/T 9704）
      </Button>
    </div>
    );
  }, [showAdvanced]);

  /* ---- 规则预览 ---- */

  const RulesPanel = useMemo(() => () => {
    const cfg = configRef.current;
    const rules = [
      { label: '标题', font: cfg.title.fontFamily, size: formatFontSizeLabel(cfg.title.fontSize) },
      { label: '正文', font: cfg.body.fontFamily, size: formatFontSizeLabel(cfg.body.fontSize), spacing: `${cfg.body.lineSpacing}pt`, indent: `${cfg.body.firstLineIndent}em` },
      { label: '一级标题', font: cfg.heading1.fontFamily, size: formatFontSizeLabel(cfg.heading1.fontSize) },
      { label: '二级标题', font: cfg.heading2.fontFamily, size: formatFontSizeLabel(cfg.heading2.fontSize) },
      { label: '三级标题', font: cfg.heading3.fontFamily, size: formatFontSizeLabel(cfg.heading3.fontSize), bold: cfg.special.heading3Bold ? '加粗' : '' },
      { label: '页边距', value: `上${cfg.margins.top} 下${cfg.margins.bottom} 左${cfg.margins.left} 右${cfg.margins.right} cm` },
      ...(cfg.header.enabled ? [{ label: '版头', value: cfg.header.orgName || '（未填写）' }] : []),
      ...(cfg.footerNote.enabled ? [{ label: '版记', value: `抄送: ${cfg.footerNote.cc || '无'}` }] : []),
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
              {r.bold && `${r.bold} `}
              {r.value}
            </span>
          </div>
        ))}
      </div>
    );
  }, []);

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
              // 使用 configRef.current 确保读取最新配置（避免闭包捕获旧值）
              const cfg = configRef.current;
              const payload = buildPreviewPayload(paragraphs, tables, cfg);
              // 强制注入版头/版记/页码配置
              if (cfg.header) {
                payload.header_config = {
                  org_name: cfg.header.orgName || '',
                  doc_number: cfg.header.docNumber || '',
                  signer: cfg.header.signer || '',
                  enabled: cfg.header.enabled,
                };
              }
              if (cfg.footerNote) {
                payload.footer_note_config = {
                  cc: cfg.footerNote.cc || '',
                  printer: cfg.footerNote.printer || '',
                  print_date: cfg.footerNote.printDate || '',
                  enabled: cfg.footerNote.enabled,
                };
              }
              if (cfg.pageNumber) {
                payload.page_number_config = {
                  show: cfg.pageNumber.show,
                  position: cfg.pageNumber.position || 'center',
                  font: cfg.pageNumber.font || '宋体',
                };
              }
              // 传递源文档 ID，保留原始文档结构（表格位置等）
              if (docId) {
                payload.source_doc_id = parseInt(docId, 10);
              }
              console.log('[Download] header_config:', payload.header_config);
              console.log('[Download] footer_note_config:', payload.footer_note_config);
              console.log('[Download] source_doc_id:', payload.source_doc_id);
              await downloadFromPost('/api/optimize/preview-download', payload, `${docName}（编排）.docx`);
            } catch (e) { console.error('Download failed:', e); }
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
                <Settings2 className="h-3.5 w-3.5 inline mr-1" /> 格式
              </button>
              <button className={`flex-1 py-2 text-sm font-medium ${activeTab === 'rules' ? 'text-accent border-b-2 border-accent' : 'text-primary-500'}`} onClick={() => setActiveTab('rules')}>
                <Eye className="h-3.5 w-3.5 inline mr-1" /> 规则
              </button>
            </div>
            <div className="p-3">
              {activeTab === 'format' ? <SettingsPanel /> : <RulesPanel />}
            </div>
          </div>
        )}

        {/* 右侧 A4 预览 */}
        <div className="flex-1 overflow-auto bg-gray-200 p-6">
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
        </div>
      </div>
    </div>
  );
}
