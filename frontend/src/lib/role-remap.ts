/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */

/**
 * role-remap.ts — 段落角色兼容映射
 *
 * 后端 /api/documents/{id}/preview 返回的段落可能缺少 header_org / header_number /
 * red_line 等角色（parser 不设置这些角色）。A4PageRenderer 依赖这些角色渲染版头。
 *
 * 本模块通过启发式检测（发文字号正则、红色文本颜色）自动补全角色，
 * 确保 A4PageRenderer 在旧数据上也能正确渲染版头/版记。
 */
import type { DocParagraph } from '@/lib/types';

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

/** 发文字号正则：国办发〔2024〕1号 / 关于XX的(2024)1号 等 */
const DOC_NUMBER_RE = /[一-龥]+发(?:〔\d{4}〕|[（(]\d{4}[）)])\d+号/;

/** 红色色值集合（文档中发文机关标志通常是红色） */
const RED_COLORS = new Set(['CC0000', 'FF0000', 'C00000', 'E00000']);

/* ------------------------------------------------------------------ */
/*  Role Detection Helpers                                             */
/* ------------------------------------------------------------------ */

function isRedParagraph(p: DocParagraph): boolean {
  const c = p.format.color?.toUpperCase();
  return !!(c && RED_COLORS.has(c));
}

/* ------------------------------------------------------------------ */
/*  Main Export                                                        */
/* ------------------------------------------------------------------ */

/**
 * 对段落数组进行角色补全/重映射，返回新数组（不修改原数组）。
 *
 * 检测规则：
 * 1. 红色文字段落 → role = 'header_org'（发文机关标志）
 * 2. 正则匹配发文字号 → role = 'header_number'
 * 3. 在版头区域后插入合成的 'red_line' 段落（红色分隔线）
 * 4. 已有 role = 'cc' 的段落保持不变
 */
export function remapParagraphRoles(paragraphs: DocParagraph[]): DocParagraph[] {
  // 快速路径：如果已包含 header_org 角色，说明数据已是新格式，无需映射
  if (paragraphs.some(p => p.role === 'header_org')) {
    return paragraphs;
  }

  const result: DocParagraph[] = [];
  let foundHeaderOrg = false;
  let foundDocNum = false;
  let headerInserted = false;

  for (let i = 0; i < paragraphs.length; i++) {
    const p = paragraphs[i];
    const text = p.text?.trim() || '';

    // 检测发文机关标志（红色文字）
    if (!foundHeaderOrg && isRedParagraph(p) && text.length > 0) {
      result.push({ ...p, role: 'header_org' });
      foundHeaderOrg = true;
      continue;
    }

    // 检测发文字号（紧跟在 header_org 之后，或文档前几段内）
    if (!foundDocNum && foundHeaderOrg && DOC_NUMBER_RE.test(text)) {
      result.push({ ...p, role: 'header_number' });
      foundDocNum = true;
      continue;
    }

    // 发文机关 + 发文字号之后，插入红色分隔线
    if (foundHeaderOrg && foundDocNum && !headerInserted) {
      result.push({
        text: '',
        role: 'red_line',
        is_heading: false,
        format: { alignment: 'center' },
      });
      headerInserted = true;
    }

    // 如果检测到 headerOrg 但没有找到 docNum，在第一段非标题正文前也插入分隔线
    if (foundHeaderOrg && !foundDocNum && !headerInserted
      && (p.role === 'body' || p.is_heading || p.role === 'title')) {
      result.push({
        text: '',
        role: 'red_line',
        is_heading: false,
        format: { alignment: 'center' },
      });
      headerInserted = true;
    }

    result.push(p);
  }

  // 如果有 headerOrg 但循环结束了还没插入分隔线，在末尾补上
  if (foundHeaderOrg && !headerInserted) {
    result.push({
      text: '',
      role: 'red_line',
      is_heading: false,
      format: { alignment: 'center' },
    });
  }

  return result;
}
