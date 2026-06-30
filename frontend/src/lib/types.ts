/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/*
 * 共享文档数据类型
 * 用于 A4 预览组件之间的类型复用
 */

export interface DocParagraph {
  text: string;
  role?: string;
  is_heading: boolean;
  heading_level?: number;
  format: {
    alignment?: string;
    first_line_indent_pt?: number;
    left_indent_pt?: number;
    font_name?: string;
    font_size_pt?: number;
    line_spacing_pt?: number;
    line_spacing_rule?: 'exact' | 'multiple' | 'atLeast';
    bold?: boolean;
    color?: string;
  };
  runs?: Array<{
    text: string;
    bold?: boolean;
    font_name?: string;
    font_size_pt?: number;
    color?: string;
  }>;
}

export interface DocTableCellPara {
  text: string;
  format: { alignment?: string; font_name?: string; font_size_pt?: number; bold?: boolean };
}

export interface DocTableCell {
  row: number;
  col: number;
  text: string;
  paragraphs: DocTableCellPara[];
}

export interface DocTable {
  index: number;
  rows: number;
  cols: number;
  cells: DocTableCell[];
  insert_after_index?: number;
}
