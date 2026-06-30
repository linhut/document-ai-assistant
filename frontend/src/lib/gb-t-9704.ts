/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/*
 * GB/T 9704 公文格式标准常量
 *
 * 所有字号、字体、版式参数均严格按国标定义。
 * 本文件是全项目字号/字体选项的唯一权威来源。
 */

/* ------------------------------------------------------------------ */
/*  字号映射（PT → 中文号）                                             */
/*  格式规范：「中文字号名称 + 半角括号 + 精确磅值」                      */
/*  示例：三号 (16pt)、二号 (22pt)、四号 (14pt)                          */
/* ------------------------------------------------------------------ */

const FONT_SIZE_PRESET_LABELS = new Map<number, string>([
  [42,   '初号'],
  [36,   '小初'],
  [26,   '一号'],
  [24,   '小一'],
  [22,   '二号'],
  [18,   '小二'],
  [16,   '三号'],
  [15,   '小三'],
  [14,   '四号'],
  [12,   '小四'],
  [10.5, '五号'],
  [9,    '小五'],
  [7.5,  '六号'],
  [6.5,  '小六'],
  [5.5,  '七号'],
  [5,    '八号'],
]);

/**
 * 格式化字号标签
 * - 标准值：`三号 (16pt)`
 * - 非标准值：`15.5pt`（仅显示 pt 值，不加"自定义"前缀）
 */
export function formatFontSizeLabel(pt: number): string {
  const preset = FONT_SIZE_PRESET_LABELS.get(pt);
  return preset ? `${preset} (${pt}pt)` : `${pt}pt`;
}

/**
 * 字号下拉选项（仅标准值，引导用户规范选择）
 */
export const FONT_SIZE_OPTIONS: { label: string; value: number }[] = [
  42, 36, 26, 24, 22, 18, 16, 15, 14, 12, 10.5, 9, 7.5, 6.5, 5.5, 5,
].map((value) => ({
  label: formatFontSizeLabel(value),
  value,
}));

/* ------------------------------------------------------------------ */
/*  字体选项                                                           */
/* ------------------------------------------------------------------ */

export const CN_FONT_OPTIONS = [
  '方正小标宋_GBK',
  '方正小标宋简体',
  '仿宋_GB2312',
  '仿宋',
  '黑体',
  '楷体_GB2312',
  '楷体',
  '宋体',
  '华文中宋',
];

export const EN_FONT_OPTIONS = [
  'Times New Roman',
  'Arial',
  'Calibri',
];

/* ------------------------------------------------------------------ */
/*  行距选项（pt）                                                     */
/* ------------------------------------------------------------------ */

export const LINE_SPACING_OPTIONS = [22, 24, 26, 28, 28.95, 29, 29.6, 30, 32];

/* ------------------------------------------------------------------ */
/*  页码样式选项                                                       */
/* ------------------------------------------------------------------ */

export const PAGE_NUMBER_STYLE_OPTIONS = [
  { label: '单右双左（国标）', value: 'mirrored' as const },
  { label: '全居中', value: 'center' as const },
];

/* ------------------------------------------------------------------ */
/*  GB/T 9704 版式常量                                                 */
/* ------------------------------------------------------------------ */

/** 每行字数 */
export const CHARS_PER_LINE = 28;

/** 每页行数 */
export const LINES_PER_PAGE = 22;

/** A4 预览宽度：210mm @ 72dpi */
export const A4_PREVIEW_WIDTH_PX = 595.28;

/* ------------------------------------------------------------------ */
/*  单位转换                                                           */
/* ------------------------------------------------------------------ */

/** mm → px（96 DPI） */
export function mmToPx(mm: number): number {
  return mm * 96 / 25.4;
}

/** cm → px */
export function cmToPx(cm: number): number {
  return mmToPx(cm * 10);
}

/** 厘米 → 占 A4 页面百分比 (宽 210mm, 高 297mm) */
export function cmToPagePercent(cm: number, axis: 'x' | 'y'): number {
  const totalMm = axis === 'x' ? 210 : 297;
  return (cm * 10) / totalMm * 100;
}
