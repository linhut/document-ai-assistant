"""
Document Modifier 测试：验证文档修改器的各种操作
"""
import pytest
from core.document.models import (
    DocumentModel, Paragraph, Run, RunFormat, ParagraphFormat, PageSetup
)
from core.document.modifier import (
    modify_font, modify_size, modify_alignment, modify_line_spacing,
    modify_first_line_indent, modify_margins,
    remove_extra_spaces, remove_extra_blank_lines,
    replace_paragraph_text, apply_modifications,
)


def _make_model() -> DocumentModel:
    """创建测试用的 DocumentModel。"""
    return DocumentModel(
        page_setup=PageSetup(
            paper_width_mm=210, paper_height_mm=297,
            margin_top_mm=37, margin_bottom_mm=35,
            margin_left_mm=28, margin_right_mm=26,
        ),
        paragraphs=[
            Paragraph(
                text="测试标题", index=0, is_heading=True, heading_level=1,
                format=ParagraphFormat(alignment="center"),
                runs=[Run(text="测试标题", index=0, format=RunFormat(
                    font_name="Arial", font_size_pt=18,
                ))],
            ),
            Paragraph(
                text="正文内容第一段。", index=1,
                format=ParagraphFormat(alignment="left", first_line_indent_pt=0),
                runs=[Run(text="正文内容第一段。", index=0, format=RunFormat(
                    font_name="Arial", font_size_pt=12,
                ))],
            ),
            Paragraph(
                text="正文内容第二段。", index=2,
                format=ParagraphFormat(alignment="left"),
                runs=[Run(text="正文内容第二段。", index=0, format=RunFormat(
                    font_name="Arial", font_size_pt=12,
                ))],
            ),
            Paragraph(
                text="正文内容第三段。", index=3,
                format=ParagraphFormat(alignment="left"),
                runs=[Run(text="正文内容第三段。", index=0, format=RunFormat(
                    font_name="Arial", font_size_pt=12,
                ))],
            ),
            Paragraph(
                text="正文内容第四段。", index=4,
                format=ParagraphFormat(alignment="left"),
                runs=[Run(text="正文内容第四段。", index=0, format=RunFormat(
                    font_name="Arial", font_size_pt=12,
                ))],
            ),
            Paragraph(
                text="（单位名称）", index=5,
                format=ParagraphFormat(alignment="left"),
                runs=[Run(text="（单位名称）", index=0, format=RunFormat(
                    font_name="Arial", font_size_pt=12,
                ))],
            ),
            Paragraph(
                text="2026年6月25日", index=6,
                format=ParagraphFormat(alignment="left"),
                runs=[Run(text="2026年6月25日", index=0, format=RunFormat(
                    font_name="Arial", font_size_pt=12,
                ))],
            ),
        ],
    )


class TestModifyFont:
    def test_modify_title_font(self):
        model = _make_model()
        modify_font(model, "title", "方正小标宋简体")
        assert model.paragraphs[0].runs[0].format.font_name == "方正小标宋简体"

    def test_modify_body_font(self):
        model = _make_model()
        modify_font(model, "body", "仿宋_GB2312")
        assert model.paragraphs[1].runs[0].format.font_name == "仿宋_GB2312"
        assert model.paragraphs[2].runs[0].format.font_name == "仿宋_GB2312"
        # 标题不应被修改
        assert model.paragraphs[0].runs[0].format.font_name == "Arial"

    def test_modify_all_font(self):
        model = _make_model()
        modify_font(model, "all", "KaiTi")
        for para in model.paragraphs:
            for run in para.runs:
                assert run.format.font_name == "KaiTi"

    def test_modify_empty_font_ignored(self):
        model = _make_model()
        original = model.paragraphs[0].runs[0].format.font_name
        modify_font(model, "title", "")
        assert model.paragraphs[0].runs[0].format.font_name == original


class TestModifySize:
    def test_modify_body_size(self):
        model = _make_model()
        modify_size(model, "body", 16.0)
        assert model.paragraphs[1].runs[0].format.font_size_pt == 16.0

    def test_modify_title_size(self):
        model = _make_model()
        modify_size(model, "title", 22.0)
        assert model.paragraphs[0].runs[0].format.font_size_pt == 22.0


class TestModifyAlignment:
    def test_modify_title_alignment(self):
        model = _make_model()
        modify_alignment(model, "title", "center")
        assert model.paragraphs[0].format.alignment == "center"

    def test_modify_body_alignment(self):
        model = _make_model()
        modify_alignment(model, "body", "justify")
        assert model.paragraphs[1].format.alignment == "justify"
        assert model.paragraphs[2].format.alignment == "justify"


class TestModifySpacing:
    def test_modify_line_spacing(self):
        model = _make_model()
        modify_line_spacing(model, "body", 28.95)
        assert model.paragraphs[1].format.line_spacing_pt == 28.95

    def test_modify_first_line_indent(self):
        model = _make_model()
        modify_first_line_indent(model, "body", 32.0)
        assert model.paragraphs[1].format.first_line_indent_pt == 32.0


class TestModifyMargins:
    def test_modify_margins(self):
        model = _make_model()
        modify_margins(model, {"top": "3.7cm", "bottom": "3.5cm"})
        assert abs(model.page_setup.margin_top_mm - 37) < 0.1
        assert abs(model.page_setup.margin_bottom_mm - 35) < 0.1


class TestTextCleanup:
    def test_remove_extra_spaces(self):
        model = _make_model()
        model.paragraphs[1].runs[0].text = "正文   内容   第一段。"
        remove_extra_spaces(model)
        assert "   " not in model.paragraphs[1].runs[0].text

    def test_remove_extra_blank_lines(self):
        model = _make_model()
        # 插入连续空行
        model.paragraphs.insert(2, Paragraph(text="", index=2, format=ParagraphFormat()))
        model.paragraphs.insert(3, Paragraph(text="", index=3, format=ParagraphFormat()))
        original_count = len(model.paragraphs)
        remove_extra_blank_lines(model)
        assert len(model.paragraphs) < original_count


class TestReplaceText:
    def test_replace_paragraph_text(self):
        model = _make_model()
        replace_paragraph_text(model, 1, "替换后的文本")
        assert model.paragraphs[1].text == "替换后的文本"

    def test_replace_out_of_range_ignored(self):
        model = _make_model()
        original_count = len(model.paragraphs)
        replace_paragraph_text(model, 999, "test")
        assert len(model.paragraphs) == original_count


class TestApplyModifications:
    def test_apply_text_replace(self):
        model = _make_model()
        mods = [{"type": "replace_text", "location": "paragraph:1", "value": "新文本"}]
        fixed = apply_modifications(model, mods)
        assert fixed.paragraphs[1].text == "新文本"

    def test_apply_set_format(self):
        model = _make_model()
        mods = [{"type": "set_format", "location": "paragraph:1", "attribute": "alignment", "value": "right"}]
        fixed = apply_modifications(model, mods)
        assert fixed.paragraphs[1].format.alignment == "right"

    def test_does_not_mutate_original(self):
        model = _make_model()
        mods = [{"type": "replace_text", "location": "paragraph:1", "value": "新文本"}]
        fixed = apply_modifications(model, mods)
        assert model.paragraphs[1].text != "新文本"
        assert fixed.paragraphs[1].text == "新文本"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])