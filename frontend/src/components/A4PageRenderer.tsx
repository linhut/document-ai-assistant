/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/*
 * A4PageRenderer — A4 分页渲染器
 *
 * 统一的 A4 预览组件，所有 A4 预览页面共用。
 * 采用 DOM 度量 + 视窗裁剪分页方案。
 *
 * GB/T 9704 标准：210mm × 297mm，版心 156mm × 225mm
 *
 * 设计原则：
 * - 配置层使用 pt 数值（16, 28.95, 22 等）
 * - CSS 渲染时直接使用相同数值作为 px（16px ≈ 16pt 在视觉密度上近似等价）
 * - 这保证了预览与 Word 文档的行数/分页高度一致
 */
import { useState, useEffect, useRef, useMemo, useCallback, type CSSProperties } from 'react';
import { paginateByMeasurement, type PageSlice } from '@/lib/paginate';
import { mmToPx } from '@/lib/gb-t-9704';
import type { DocParagraph, DocTable, DocTableCell } from '@/lib/types';
import './A4PageRenderer.css';

/* ------------------------------------------------------------------ */
/*  字体映射（含 fallback 策略）                                         */
/*                                                                      */
/*  优先级：                                                             */
/*  1. 指定公文字体（如方正小标宋_GBK）                                   */
/*  2. 同族系统字体（如 SimHei 替代黑体）                                */
/*  3. 通用衬线/无衬线 fallback                                          */
/*                                                                      */
/*  关于页提供字体下载入口，用户可安装缺失字体。                          */
/* ------------------------------------------------------------------ */

const FONT_MAP: Record<string, string> = {
  // 标题字体：方正小标宋 → 华文中宋 → 宋体 → serif
  '方正小标宋简体': '"方正小标宋简体", "FZXiaoBiaoSong-B05S", "STZhongsong", "华文中宋", "SimSun", "宋体", serif',
  '方正小标宋_GBK': '"方正小标宋_GBK", "FZXiaoBiaoSong-B05S", "STZhongsong", "华文中宋", "SimSun", "宋体", serif',
  // 标题/一级标题：黑体 → SimHei → 微软雅黑 → sans-serif
  '黑体': '"黑体", "SimHei", "Microsoft YaHei", "微软雅黑", sans-serif',
  // 二级标题：楷体 → KaiTi → STKaiti → 仿宋 → serif
  '楷体_GB2312': '"楷体_GB2312", "KaiTi", "楷体", "STKaiti", "华文楷体", "FangSong", "仿宋", serif',
  '楷体': '"楷体", "KaiTi", "STKaiti", "华文楷体", "FangSong", "仿宋", serif',
  // 正文：仿宋 → FangSong → STFangsong → 宋体 → serif
  '仿宋_GB2312': '"仿宋_GB2312", "FangSong", "仿宋", "STFangsong", "华文仿宋", "SimSun", "宋体", serif',
  '仿宋': '"仿宋", "FangSong", "STFangsong", "华文仿宋", "SimSun", "宋体", serif',
  // 页码/版记：宋体 → SimSun → 仿宋 → serif
  '宋体': '"宋体", "SimSun", "STSong", "华文宋体", "FangSong", "仿宋", serif',
  // 英数字体
  'Times New Roman': '"Times New Roman", "Georgia", serif',
  'Arial': '"Arial", "Helvetica Neue", "Helvetica", sans-serif',
  'Calibri': '"Calibri", "Segoe UI", "Arial", sans-serif',
};

export function ff(name?: string): string {
  if (!name) return '"仿宋_GB2312", "FangSong", "仿宋", "SimSun", "宋体", serif';
  return FONT_MAP[name] || `"${name}", serif`;
}

/**
 * 检测指定字体是否在系统中可用（基于 Canvas 度量）
 *
 * 在组件挂载时调用，对不可用字体输出 console.warn 提示。
 * 注意：此检测有性能开销，仅在开发模式或首次加载时使用。
 */
export function detectMissingFonts(fontNames: string[]): string[] {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  if (!ctx) return [];

  const testString = '中文测试 ABC abc 123';

  // 用已知存在的字体建立基线
  const knownFonts = ['serif', 'sans-serif', 'monospace'];
  const baseline: Record<string, number> = {};
  for (const f of knownFonts) {
    ctx.font = `72px ${f}`;
    baseline[f] = ctx.measureText(testString).width;
  }

  const missing: string[] = [];
  for (const fontName of fontNames) {
    // 跳过已映射的非原生字体名
    const primaryName = fontName.replace(/["']/g, '').split(',')[0].trim();
    ctx.font = `72px "${primaryName}", serif`;
    const width = ctx.measureText(testString).width;
    // 如果宽度与 serif 基线完全一致，说明该字体未安装，回退到了 serif
    if (Math.abs(width - baseline['serif']) < 0.1) {
      missing.push(primaryName);
    }
  }

  return missing;
}

/* ------------------------------------------------------------------ */
/*  Props                                                              */
/* ------------------------------------------------------------------ */

export interface A4PageRendererProps {
  paragraphs: DocParagraph[];
  tables: DocTable[];
  margins: { top: number; bottom: number; left: number; right: number }; // cm
  bodyFontSize?: number;          // pt 数值，CSS 中直接当 px 使用
  bodyLineSpacing?: number;       // pt 数值，CSS 中直接当 px 使用
  titleFontFamily?: string;
  titleFontSize?: number;
  titleBold?: boolean;
  titleAlign?: string;
  heading1FontFamily?: string;
  heading1FontSize?: number;
  heading2FontFamily?: string;
  heading2FontSize?: number;
  heading3FontFamily?: string;
  heading3FontSize?: number;
  heading3Bold?: boolean;
  pageNumberShow?: boolean;
  pageNumberPosition?: 'center' | 'right-left';
  pageNumberFont?: string;
  firstParaBold?: boolean;
  stamp?: boolean;
  stampImage?: string;
  stampPage?: number;
  zoom?: number;
  headerConfig?: { enabled: boolean; orgName: string; docNumber: string; signer: string };
  footerNoteConfig?: { enabled: boolean; cc: string; printer: string; printDate: string };
}

/* ------------------------------------------------------------------ */
/*  段落渲染                                                           */
/* ------------------------------------------------------------------ */

function renderParagraph(p: DocParagraph, key: number, cfg: {
  bodyFontSize: number;
  bodyLineSpacing: number;
  titleFontFamily: string;
  titleFontSize: number;
  titleBold: boolean;
  titleAlign: string;
  heading1FontFamily: string;
  heading1FontSize: number;
  heading2FontFamily: string;
  heading2FontSize: number;
  heading3FontFamily: string;
  heading3FontSize: number;
  heading3Bold: boolean;
  firstParaBold: boolean;
}): React.ReactNode {
  // 数值直接当 px 使用（与 Word pt 值 1:1 对应，保证行数/分页一致）
  let fs = cfg.bodyFontSize;
  let font = ff();
  let lh = `${cfg.bodyLineSpacing}px`;
  let indent = `${cfg.bodyFontSize * 2}px`;  // 首行缩进 = 2字符宽
  let align: string = 'justify';
  let bold: boolean | undefined;

  // 版头特殊段落
  if (p.role === 'header_org') {
    return <p key={key} className="a4-header-org">{p.text}</p>;
  }
  if (p.role === 'header_number') {
    return (
      <div key={key} className="a4-header-meta">
        <span>{p.text}</span>
      </div>
    );
  }
  if (p.role === 'red_line') {
    return <div key={key} className="a4-header-separator" />;
  }
  if (p.role === 'footer_line') {
    return <div key={key} className="a4-footer-note-line-top" />;
  }
  if (p.role === 'cc') {
    return (
      <div key={key} className="a4-footer-note-cc">
        <span className="a4-footer-note-cc-label">抄送：</span>
        <span className="a4-footer-note-cc-text">{p.text.replace(/^抄送：/, '')}</span>
      </div>
    );
  }
  if (p.role === 'footer_info') {
    return (
      <div key={key} className="a4-footer-note-printer">
        <span>{p.text}</span>
      </div>
    );
  }

  // 标题样式 — 字号来自配置（数值直接当 px，与 Word pt 值 1:1）
  let className = 'a4-paragraph';
  if (p.is_heading && p.heading_level === 0) {
    fs = cfg.titleFontSize; font = ff(cfg.titleFontFamily);
    align = cfg.titleAlign; indent = '0'; bold = cfg.titleBold;
    className = 'a4-title';
  } else if (p.is_heading && p.heading_level === 1) {
    fs = cfg.heading1FontSize; font = ff(cfg.heading1FontFamily);
    align = 'left'; indent = `${cfg.bodyFontSize * 2}px`;
    className = 'a4-h1';
  } else if (p.is_heading && p.heading_level === 2) {
    fs = cfg.heading2FontSize; font = ff(cfg.heading2FontFamily);
    align = 'left'; indent = `${cfg.bodyFontSize * 2}px`;
    className = 'a4-h2';
  } else if (p.is_heading && p.heading_level === 3) {
    fs = cfg.heading3FontSize; font = ff(cfg.heading3FontFamily);
    bold = cfg.heading3Bold; align = 'left'; indent = `${cfg.bodyFontSize * 2}px`;
    className = 'a4-h3';
  }

  // 首句加粗
  if (cfg.firstParaBold && !p.is_heading && p.role === 'body' && p.text?.trim()) {
    const dotIdx = p.text.indexOf('。');
    if (dotIdx > 0 && dotIdx < p.text.length - 1) {
      return (
        <p key={key} className={className} style={{
          fontSize: `${fs}px`, fontFamily: font, lineHeight: lh,
          textAlign: align as any, textIndent: indent, margin: 0,
        }}>
          <strong className="a4-bold-first">{p.text.slice(0, dotIdx + 1)}</strong>
          {p.text.slice(dotIdx + 1)}
        </p>
      );
    }
  }

  const style: CSSProperties = {
    fontSize: `${fs}px`, fontFamily: font, lineHeight: lh,
    textAlign: align as any, textIndent: indent,
    margin: 0, fontWeight: bold ? 'bold' : undefined,
  };

  if (!p.text?.trim()) {
    return <p key={key} className="a4-empty-line" style={{ lineHeight: lh, height: lh, margin: 0 }}>&nbsp;</p>;
  }

  return <p key={key} className={className} style={style}>{p.text}</p>;
}

/* ------------------------------------------------------------------ */
/*  表格渲染                                                           */
/* ------------------------------------------------------------------ */

function renderTable(table: DocTable, key: number, bodyFontSize: number): React.ReactNode {
  const cellMap: Record<string, DocTableCell> = {};
  for (const c of table.cells) { cellMap[`${c.row}-${c.col}`] = c; }
  return (
    <table key={`table-${key}`} style={{
      width: '100%', borderCollapse: 'collapse',
      fontSize: `${Math.max(bodyFontSize - 2, 12)}px`,
      fontFamily: ff(), lineHeight: `${bodyFontSize + 4}px`, margin: '0.5em 0',
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
                  border: '1px solid #000', padding: '4pt 6pt',
                  textAlign: isHeader ? 'center' : 'left',
                  fontWeight: isHeader ? 'bold' : undefined,
                  fontFamily: ff(isHeader ? '黑体' : undefined), verticalAlign: 'top',
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
}

/* ------------------------------------------------------------------ */
/*  内容流渲染                                                         */
/* ------------------------------------------------------------------ */

function renderContentFlow(paragraphs: DocParagraph[], tables: DocTable[], cfg: any): React.ReactNode[] {
  const elements: React.ReactNode[] = [];

  const title = paragraphs.find(p => p.role === 'title' || (p.is_heading && p.heading_level === 0));
  const recipient = paragraphs.find(p => p.role === 'recipient');
  if (title) elements.push(renderParagraph(title, -1, cfg));
  if (recipient) elements.push(renderParagraph(recipient, -2, cfg));

  const body = paragraphs.filter(p =>
    (p.role === 'body' || p.role === 'attachment' ||
    (p.is_heading && p.heading_level && p.heading_level >= 1 && p.role !== 'title'))
    && !['header_org', 'header_number', 'red_line', 'footer_line', 'cc', 'footer_info'].includes(p.role || '')
  );

  const tableMap: Record<number, DocTable[]> = {};
  for (const t of tables) {
    const idx = t.insert_after_index ?? -1;
    if (!tableMap[idx]) tableMap[idx] = [];
    tableMap[idx].push(t);
  }

  body.forEach((p, i) => {
    elements.push(renderParagraph(p, i, cfg));
    if (tableMap[i]) for (const t of tableMap[i]) elements.push(renderTable(t, i, cfg.bodyFontSize));
  });
  if (tableMap[-1]) for (const t of tableMap[-1]) elements.push(renderTable(t, -1, cfg.bodyFontSize));

  const signature = paragraphs.find(p => p.role === 'signature');
  const date = paragraphs.find(p => p.role === 'date');
  if (signature || date) {
    elements.push(
      <div key="signatures" style={{ marginTop: '3em' }}>
        {signature && renderParagraph({ ...signature, format: { ...signature.format, alignment: 'right' } }, -3, cfg)}
        {date && renderParagraph({ ...date, format: { ...date.format, alignment: 'right' } }, -4, cfg)}
      </div>
    );
  }

  return elements;
}

/* ------------------------------------------------------------------ */
/*  主组件                                                             */
/* ------------------------------------------------------------------ */

export default function A4PageRenderer(props: A4PageRendererProps) {
  const {
    paragraphs, tables, margins,
    bodyFontSize = 16, bodyLineSpacing = 28.95,
    titleFontFamily = '方正小标宋简体', titleFontSize = 22,
    titleBold = false, titleAlign = 'center',
    heading1FontFamily = '黑体', heading1FontSize = 16,
    heading2FontFamily = '楷体_GB2312', heading2FontSize = 16,
    heading3FontFamily = '仿宋_GB2312', heading3FontSize = 16, heading3Bold = true,
    pageNumberShow = true, pageNumberPosition = 'center', pageNumberFont = '宋体',
    firstParaBold = false, stamp = false, stampImage, stampPage = 0,
    zoom = 100,
    headerConfig, footerNoteConfig,
  } = props;

  // 使用 useMemo 缓存 cfg 对象，避免每次渲染都重新创建
  const cfg = useMemo(() => ({
    bodyFontSize, bodyLineSpacing,
    titleFontFamily, titleFontSize, titleBold, titleAlign,
    heading1FontFamily, heading1FontSize, heading2FontFamily, heading2FontSize,
    heading3FontFamily, heading3FontSize, heading3Bold,
    firstParaBold,
  }), [
    bodyFontSize, bodyLineSpacing,
    titleFontFamily, titleFontSize, titleBold, titleAlign,
    heading1FontFamily, heading1FontSize, heading2FontFamily, heading2FontSize,
    heading3FontFamily, heading3FontSize, heading3Bold,
    firstParaBold,
  ]);

  const measurerRef = useRef<HTMLDivElement>(null);
  const [pages, setPages] = useState<PageSlice[]>([{ offsetY: 0, clipHeight: 0 }]);

  // CSS 变量（margins 单位为 cm → ×10 转 mm；字号/行距数值直接当 px）
  const cssVars = useMemo((): CSSProperties => ({
    '--margin-top': `${margins.top * 10}mm`,
    '--margin-right': `${margins.right * 10}mm`,
    '--margin-bottom': `${margins.bottom * 10}mm`,
    '--margin-left': `${margins.left * 10}mm`,
    '--body-font': ff(),
    '--body-size': `${bodyFontSize}px`,
    '--body-line-height': `${bodyLineSpacing}px`,
    '--page-number-font': pageNumberFont,
  } as CSSProperties), [margins, bodyFontSize, bodyLineSpacing, pageNumberFont]);

  // DOM 度量分页（行级度量）
  const recalculate = useCallback(() => {
    const el = measurerRef.current;
    if (!el) return;

    const scrollContainer = el.parentElement;

    // 测量版头高度（含 margin）
    let headerHeightPx = 0;
    const headerEl = scrollContainer?.querySelector('.a4-header-section') as HTMLElement | null;
    if (headerEl) {
      const rect = headerEl.getBoundingClientRect();
      const style = getComputedStyle(headerEl);
      headerHeightPx = rect.height + parseFloat(style.marginTop) + parseFloat(style.marginBottom);
    }

    // 测量版记高度
    let footerNoteHeightPx = 0;
    const footerEl = scrollContainer?.querySelector('.a4-footer-note') as HTMLElement | null;
    if (footerEl) footerNoteHeightPx = footerEl.getBoundingClientRect().height;

    const pageHeightPx = mmToPx(297);
    const marginTopPx = mmToPx(margins.top * 10);
    const marginBottomPx = mmToPx(margins.bottom * 10);

    const result = paginateByMeasurement(
      el, paragraphs, tables,
      pageHeightPx, marginTopPx, marginBottomPx,
      headerHeightPx, footerNoteHeightPx,
      pageNumberShow,
    );

    setPages(prev => {
      if (prev.length !== result.length) return result;
      for (let i = 0; i < prev.length; i++) {
        if (Math.abs(prev[i].offsetY - result[i].offsetY) > 1 ||
            Math.abs(prev[i].clipHeight - result[i].clipHeight) > 1) return result;
      }
      return prev;
    });
  }, [paragraphs, tables, margins, pageNumberShow]);

  useEffect(() => {
    const el = measurerRef.current;
    if (!el) return;
    const frameId = requestAnimationFrame(() => recalculate());
    const observer = new ResizeObserver(() => recalculate());
    observer.observe(el);
    return () => { cancelAnimationFrame(frameId); observer.disconnect(); };
  }, [recalculate]);

  const contentFlow = useMemo(() => renderContentFlow(paragraphs, tables, cfg), [paragraphs, tables, cfg]);

  const headerFlow = useMemo(() => {
    if (!headerConfig?.enabled) return null;
    return (
      <div className="a4-header-section">
        {headerConfig.orgName && <p className="a4-header-org">{headerConfig.orgName}</p>}
        {(headerConfig.docNumber || headerConfig.signer) && (
          <div className={`a4-header-meta${headerConfig.signer ? ' a4-header-meta--with-signer' : ''}`}>
            <span>{headerConfig.docNumber}</span>
            {headerConfig.signer && (
              <span>
                <span className="a4-header-signer-label">签发人：</span>
                <span className="a4-header-signer-name">{headerConfig.signer}</span>
              </span>
            )}
          </div>
        )}
        <div className="a4-header-separator" />
      </div>
    );
  }, [headerConfig]);

  const footerNoteFlow = useMemo(() => {
    if (!footerNoteConfig?.enabled) return null;
    return (
      <div className="a4-footer-note">
        <div className="a4-footer-note-line-top" />
        {footerNoteConfig.cc && (
          <div className="a4-footer-note-cc">
            <span className="a4-footer-note-cc-label">抄送：</span>
            <span className="a4-footer-note-cc-text">{footerNoteConfig.cc}。</span>
          </div>
        )}
        {footerNoteConfig.cc && (footerNoteConfig.printer || footerNoteConfig.printDate) && (
          <div className="a4-footer-note-line-middle" />
        )}
        {(footerNoteConfig.printer || footerNoteConfig.printDate) && (
          <div className="a4-footer-note-printer">
            <span>{footerNoteConfig.printer}</span>
            <span>{footerNoteConfig.printDate}{footerNoteConfig.printDate ? '印发' : ''}</span>
          </div>
        )}
        <div className="a4-footer-note-line-bottom" />
      </div>
    );
  }, [footerNoteConfig]);

  return (
    <div style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top center' }}>
      {/* 隐藏度量容器 */}
      <div ref={measurerRef} aria-hidden="true" className="a4-page" style={{
        position: 'absolute', visibility: 'hidden', zIndex: -1,
        height: 'auto',
        ...cssVars,
      }}>
        <div className="a4-content" style={{ height: 'auto', overflow: 'visible' }}>
          {contentFlow}
        </div>
      </div>

      {/* 可见页面 */}
      {pages.map((page, pageIdx) => (
        <div key={pageIdx} className="a4-page" style={cssVars}>
          <div className="a4-content">
            {/* 版头（仅第一页） */}
            {pageIdx === 0 && headerFlow}

            {/* 内容裁剪视窗 */}
            <div className="a4-content-viewport" style={{ height: `${page.clipHeight}px` }}>
              <div style={{ transform: `translateY(-${page.offsetY}px)` }}>
                {contentFlow}
              </div>
            </div>
          </div>

          {/* 版记（仅最后一页） */}
          {pageIdx === pages.length - 1 && footerNoteFlow}

          {/* 页码 */}
          {pageNumberShow && (
            <div className={`a4-page-number ${
              pageNumberPosition === 'right-left'
                ? (pageIdx % 2 === 0 ? 'a4-page-number--odd' : 'a4-page-number--even')
                : 'a4-page-number--center'
            }`}>
              — {pageIdx + 1} —
            </div>
          )}

          {/* 印章 */}
          {stamp && (() => {
            const targetPage = stampPage > 0 ? stampPage - 1 : pages.length - 1;
            if (pageIdx !== targetPage) return null;
            return stampImage ? (
              <img src={stampImage} alt="印章" style={{
                position: 'absolute',
                right: `calc(var(--margin-right, 26mm) + 15mm)`,
                bottom: `calc(var(--margin-bottom, 35mm) + 25mm)`,
                width: '40mm', height: '40mm',
                opacity: 0.85, pointerEvents: 'none',
              }} />
            ) : (
              <div className="a4-stamp-placeholder">印章位置</div>
            );
          })()}
        </div>
      ))}
    </div>
  );
}
