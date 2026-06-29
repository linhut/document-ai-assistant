/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */

/**
 * download.ts — 共享下载工具
 *
 * 提供两类下载能力：
 * 1. downloadFromPost  — POST blob 下载（预览数据 → docx）
 * 2. buildPreviewPayload — 合并用户配置到段落格式，构建下载 payload
 */
import { apiClient } from '@/api/client';
import type { DocParagraph, DocTable } from '@/lib/types';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

/** 文档配置（来自 useDocumentConfig） */
export interface DownloadConfig {
  margins: { top: number; bottom: number; left: number; right: number };
  body: {
    fontFamily: string;
    fontSize: number;
    lineSpacing: number;
    firstLineIndent: number;
    align: string;
  };
  title: { fontFamily: string; fontSize: number; bold: boolean; align: string };
  heading1: { fontFamily: string; fontSize: number };
  heading2: { fontFamily: string; fontSize: number };
  heading3: { fontFamily: string; fontSize: number };
  special: { heading3Bold: boolean; stamp: boolean; stampImage: string; stampPage: number };
  header?: { enabled: boolean; orgName: string; docNumber: string; signer: string };
  footerNote?: { enabled: boolean; cc: string; printer: string; printDate: string };
  pageNumber?: { show: boolean; format: string; position: string; font: string };
}

/* ------------------------------------------------------------------ */
/*  下载函数                                                            */
/* ------------------------------------------------------------------ */

/**
 * 通过 POST 请求下载 blob 文件。
 * 用于预览数据 → docx 的场景（POST body 包含段落/表格数据）。
 */
export async function downloadFromPost(
  endpoint: string,
  body: Record<string, unknown>,
  filename: string,
  timeout = 30000,
): Promise<void> {
  const blob = await apiClient.post<Blob>(endpoint, body, { responseType: 'blob', timeout }) as unknown as Blob;
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/* ------------------------------------------------------------------ */
/*  Payload 构建                                                        */
/* ------------------------------------------------------------------ */

/**
 * 合并用户配置到段落格式，构建 preview-download 的请求体。
 *
 * 确保下载的 docx 与前端 A4PageRenderer 预览一致：
 * - 正文段落：应用 body 配置
 * - 标题段落：按 heading_level 应用对应配置
 * - 签名/日期：使用正文字体，右对齐
 */
export function buildPreviewPayload(
  paragraphs: DocParagraph[],
  tables: DocTable[],
  config: DownloadConfig,
): Record<string, unknown> {
  const mergedParagraphs = paragraphs.map(p => {
    const baseFormat = { ...p.format };

    // 正文段落
    if (p.role === 'body' || p.role === 'attachment' || (!p.role && !p.is_heading)) {
      baseFormat.font_name = config.body.fontFamily;
      baseFormat.font_size_pt = config.body.fontSize;
      baseFormat.line_spacing_pt = config.body.lineSpacing;
      baseFormat.line_spacing_rule = 'exact';
      baseFormat.first_line_indent_pt = config.body.fontSize * config.body.firstLineIndent;
      baseFormat.alignment = config.body.align;
    }

    // 标题段落
    if (p.is_heading) {
      if (p.heading_level === 0) {
        baseFormat.font_name = config.title.fontFamily;
        baseFormat.font_size_pt = config.title.fontSize;
        baseFormat.bold = config.title.bold;
        baseFormat.alignment = config.title.align;
      } else if (p.heading_level === 1) {
        baseFormat.font_name = config.heading1.fontFamily;
        baseFormat.font_size_pt = config.heading1.fontSize;
      } else if (p.heading_level === 2) {
        baseFormat.font_name = config.heading2.fontFamily;
        baseFormat.font_size_pt = config.heading2.fontSize;
      } else if (p.heading_level === 3) {
        baseFormat.font_name = config.heading3.fontFamily;
        baseFormat.font_size_pt = config.heading3.fontSize;
        baseFormat.bold = config.special.heading3Bold;
      }
    }

    // 签名/日期
    if (p.role === 'signature' || p.role === 'date') {
      baseFormat.font_name = config.body.fontFamily;
      baseFormat.font_size_pt = config.body.fontSize;
      baseFormat.alignment = 'right';
    }

    return {
      text: p.text,
      role: p.role,
      is_heading: p.is_heading,
      heading_level: p.heading_level,
      format: baseFormat,
    };
  });

  const payload: Record<string, unknown> = {
    paragraphs: mergedParagraphs,
    tables: tables.length > 0 ? tables : undefined,
    page_setup: {
      margin_top_mm: config.margins.top * 10,
      margin_bottom_mm: config.margins.bottom * 10,
      margin_left_mm: config.margins.left * 10,
      margin_right_mm: config.margins.right * 10,
    },
  };

  // 印章
  if (config.special.stamp && config.special.stampImage) {
    payload.stamp = {
      image_base64: config.special.stampImage,
      page_number: config.special.stampPage || 0,
      x_mm: 30,
      y_mm: 25,
      width_mm: 40,
      height_mm: 40,
    };
  }

  // 版头配置
  if (config.header?.enabled) {
    payload.header_config = {
      org_name: config.header.orgName || '',
      doc_number: config.header.docNumber || '',
      signer: config.header.signer || '',
    };
  }

  // 版记配置
  if (config.footerNote?.enabled) {
    payload.footer_note_config = {
      cc: config.footerNote.cc || '',
      printer: config.footerNote.printer || '',
      print_date: config.footerNote.printDate || '',
    };
  }

  // 页码配置
  if (config.pageNumber) {
    payload.page_number_config = {
      show: config.pageNumber.show,
      position: config.pageNumber.position || 'center',
      font: config.pageNumber.font || '宋体',
    };
  }

  return payload;
}
