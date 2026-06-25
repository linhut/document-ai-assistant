# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Pydantic data models for the intermediate document representation.
All operations work on this JSON model -- never directly on python-docx objects.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional


# ---------------------------------------------------------------------------
#  Primitives
# ---------------------------------------------------------------------------

class RunFormat(BaseModel):
    """Formatting information for a single text run."""
    font_name: Optional[str] = None
    font_size_pt: Optional[float] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    color: Optional[str] = None


class Run(BaseModel):
    """A contiguous span of text sharing the same formatting."""
    index: int = 0
    text: str
    format: RunFormat = Field(default_factory=RunFormat)


class ParagraphFormat(BaseModel):
    """Paragraph-level formatting."""
    alignment: Optional[str] = None          # left / center / right / justify
    first_line_indent_pt: Optional[float] = None
    left_indent_pt: Optional[float] = None
    right_indent_pt: Optional[float] = None
    space_before_pt: Optional[float] = None
    space_after_pt: Optional[float] = None
    line_spacing_pt: Optional[float] = None
    line_spacing_rule: Optional[str] = None  # multiple / exact / atLeast


class Paragraph(BaseModel):
    """A single paragraph in the document."""
    index: int
    text: str
    style_name: Optional[str] = None
    is_heading: bool = False
    heading_level: Optional[int] = None      # 1-9 for Word heading levels
    runs: list[Run] = Field(default_factory=list)
    format: ParagraphFormat = Field(default_factory=ParagraphFormat)


class TableCell(BaseModel):
    """A single cell inside a table."""
    row: int
    col: int
    text: str
    paragraphs: list[Paragraph] = Field(default_factory=list)


class Table(BaseModel):
    """A table in the document."""
    index: int
    rows: int
    cols: int
    cells: list[TableCell] = Field(default_factory=list)


class HeaderFooter(BaseModel):
    """Content in a page header or footer."""
    section_index: int = 0
    type: str = "header"                     # header / footer
    text: str = ""
    paragraphs: list[Paragraph] = Field(default_factory=list)
    has_page_number: bool = False            # 是否包含页码域


# ---------------------------------------------------------------------------
#  Page setup
# ---------------------------------------------------------------------------

class PageSetup(BaseModel):
    """Page layout settings."""
    paper_width_mm: Optional[float] = None
    paper_height_mm: Optional[float] = None
    margin_top_mm: Optional[float] = None
    margin_bottom_mm: Optional[float] = None
    margin_left_mm: Optional[float] = None
    margin_right_mm: Optional[float] = None
    orientation: str = "portrait"


# ---------------------------------------------------------------------------
#  Metadata
# ---------------------------------------------------------------------------

class DocumentMetadata(BaseModel):
    """Document-level metadata."""
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    created: Optional[str] = None
    modified: Optional[str] = None
    category: Optional[str] = None


# ---------------------------------------------------------------------------
#  Top-level Document Model
# ---------------------------------------------------------------------------

class DocumentModel(BaseModel):
    """
    The canonical intermediate representation of a Word document.
    All rule engine checks and modifications operate on this model.
    """
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    page_setup: PageSetup = Field(default_factory=PageSetup)
    paragraphs: list[Paragraph] = Field(default_factory=list)
    tables: list[Table] = Field(default_factory=list)
    headers: list[HeaderFooter] = Field(default_factory=list)
    footers: list[HeaderFooter] = Field(default_factory=list)

    # Source file info
    filename: Optional[str] = Field(default=None, exclude=True)
    source_path: Optional[str] = Field(default=None, exclude=True)
