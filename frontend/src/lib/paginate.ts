/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/*
 * paginate.ts — A4 分页引擎（行级 DOM 度量方案）
 *
 * 核心思路（复用 gongwen 项目算法）：
 * 1. 将全部内容渲染到隐藏度量容器中
 * 2. 遍历每个 <p> 元素，按 lineHeight 拆成逐行位置
 * 3. 按行边界分页（不是按段落边界）→ 段落内可自然断页
 * 4. 返回每页的 {offsetY, clipHeight}
 *
 * GB/T 9704 标准：
 * - A4 纸张：210mm × 297mm
 * - 版心：156mm × 225mm
 */

import type { DocParagraph, DocTable } from './types';
import { mmToPx } from './gb-t-9704';

/* ------------------------------------------------------------------ */
/*  类型                                                               */
/* ------------------------------------------------------------------ */

export interface PageSlice {
  offsetY: number;    // px — 该页在完整内容流中的起始偏移
  clipHeight: number; // px — 该页应显示的高度
}

interface LinePos {
  top: number;
  bottom: number;
}

/* ------------------------------------------------------------------ */
/*  行级 DOM 度量分页                                                   */
/* ------------------------------------------------------------------ */

/**
 * 行级度量分页：将每个 <p> 拆成逐行位置，按行边界切割页面。
 *
 * @param measurerEl - 隐藏度量容器 DOM 元素（已渲染完所有内容）
 * @param _paragraphs - 段落数据（未使用，保留接口兼容）
 * @param _tables - 表格数据（未使用，保留接口兼容）
 * @param pageHeightPx - A4 页面像素高度
 * @param marginTopPx - 上边距像素
 * @param marginBottomPx - 下边距像素
 * @param headerHeightPx - 版头区域像素高度（仅首页）
 * @param footerNoteHeightPx - 版记区域像素高度（仅末页）
 * @param showPageNumber - 是否显示页码（影响可用内容区高度）
 */
export function paginateByMeasurement(
  measurerEl: HTMLElement,
  _paragraphs: DocParagraph[],
  _tables: DocTable[],
  pageHeightPx: number,
  marginTopPx: number,
  marginBottomPx: number,
  headerHeightPx: number = 0,
  footerNoteHeightPx: number = 0,
  showPageNumber: boolean = true,
): PageSlice[] {
  // ① 同步度量容器宽度：从可见 .a4-page 读取精确浮点宽度
  const scrollContainer = measurerEl.parentElement;
  if (scrollContainer) {
    const a4Page = scrollContainer.querySelector('.a4-page:not([aria-hidden])') as HTMLElement | null;
    if (a4Page) {
      measurerEl.style.width = `${a4Page.getBoundingClientRect().width}px`;
    }
  }

  // ② 读取可用内容区高度
  // 可用高度 = 页面高度 - 上边距 - 下边距 - 页码区域(可选) - 安全余量
  const pageNumberHeight = showPageNumber ? 28 : 0;  // 页码约 7mm，隐藏时不扣除
  const safetyMargin = 8;
  const fullAvailable = pageHeightPx - marginTopPx - marginBottomPx - pageNumberHeight - safetyMargin;
  const firstPageAvailable = fullAvailable - headerHeightPx;

  // ③ 获取度量容器内所有 <p> 元素（正文流）
  // 度量容器结构：measurerEl > div > p, table, div...
  const contentEl = measurerEl.querySelector('div') || measurerEl;
  const paragraphs = contentEl.querySelectorAll<HTMLElement>(':scope > p, :scope > table, :scope > div');

  if (paragraphs.length === 0) {
    return [{ offsetY: 0, clipHeight: firstPageAvailable }];
  }

  // ④ 收集所有行的 top/bottom 位置（行级度量）
  const lines: LinePos[] = [];
  const contentRect = contentEl.getBoundingClientRect();

  for (const el of paragraphs) {
    const pRect = el.getBoundingClientRect();
    const pTop = pRect.top - contentRect.top;
    const pHeight = pRect.height;

    if (pHeight <= 0) continue;

    const computedStyle = getComputedStyle(el);
    const lineHeight = parseFloat(computedStyle.lineHeight);

    if (isNaN(lineHeight) || lineHeight <= 0 || pHeight <= lineHeight * 1.5) {
      // 单行元素（标题、表格、短段落）：整体作为一行
      lines.push({ top: pTop, bottom: pTop + pHeight });
    } else {
      // 多行段落：按 lineHeight 逐行切割
      const lineCount = Math.max(1, Math.round(pHeight / lineHeight));
      for (let i = 0; i < lineCount; i++) {
        lines.push({
          top: pTop + i * lineHeight,
          // 最后一行 bottom 取段落实际底部，衔接下一段
          bottom: i < lineCount - 1 ? pTop + (i + 1) * lineHeight : pTop + pHeight,
        });
      }
    }
  }

  if (lines.length === 0) {
    return [{ offsetY: 0, clipHeight: firstPageAvailable }];
  }

  const totalContentHeight = lines[lines.length - 1].bottom;

  // ⑤ Phase 1: 按行边界分页
  //    首页使用 firstPageAvailable（扣除版头），后续页使用 fullAvailable。
  const breakOffsets: number[] = [0];
  let pageStart = 0;
  let currentAvailable = firstPageAvailable;

  for (const line of lines) {
    // 当前行底部超出当前页可用高度 → 断页
    // line.top - pageStart > 0.5 防止页首行触发分页（死循环保护）
    if (line.bottom - pageStart > currentAvailable && line.top - pageStart > 0.5) {
      pageStart = line.top;
      breakOffsets.push(pageStart);
      currentAvailable = fullAvailable; // 后续页恢复全量高度
    }
  }

  // ⑥ Phase 2: 末页为版记预留空间
  //    版记绝对定位于页面底部，会挤压可用内容空间。
  //    如果末页内容 + 版记高度超出可用空间，迭代地将溢出行推入新页。
  if (footerNoteHeightPx > 0) {
    let maxIterations = 10; // 安全上限，防止死循环
    let stable = false;
    while (!stable && maxIterations-- > 0) {
      stable = true;
      const lastIdx = breakOffsets.length - 1;
      const lastStart = breakOffsets[lastIdx];
      const isAlsoFirstPage = lastIdx === 0;
      const lastPageBase = isAlsoFirstPage ? firstPageAvailable : fullAvailable;
      const lastPageAvailable = lastPageBase - footerNoteHeightPx;
      const lastPageContent = totalContentHeight - lastStart;

      if (lastPageContent > lastPageAvailable + 0.5) {
        // 在末页中找到溢出行并创建新断点
        for (const line of lines) {
          if (line.top < lastStart + 0.5) continue;
          if (line.bottom - lastStart > lastPageAvailable && line.top - lastStart > 0.5) {
            breakOffsets.push(line.top);
            stable = false;
            break;
          }
        }
      }
    }
  }

  // ⑦ 根据断点计算每页 clipHeight
  //    clipHeight = 下一页 offsetY - 当前页 offsetY，天然对齐行边界。
  const result: PageSlice[] = breakOffsets.map((offset, i) => {
    const nextOffset = i < breakOffsets.length - 1 ? breakOffsets[i + 1] : totalContentHeight;
    return {
      offsetY: offset,
      clipHeight: nextOffset - offset,
    };
  });

  return result.length > 0 ? result : [{ offsetY: 0, clipHeight: firstPageAvailable }];
}
