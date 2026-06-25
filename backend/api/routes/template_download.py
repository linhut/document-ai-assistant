# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Template download API: generate and download template documents.
根据规则生成标准的公文模板文档供用户下载

模板生成流程：
  1. 加载对应公文类型的 YAML 规则
  2. 根据规则创建 DocumentModel
  3. 通过 Document Generator 生成 docx
  4. 返回下载

确保生成的文件：
  - 正确的页边距（GB/T 9704标准）
  - 正确的标题字体（方正小标宋简体）
  - 正确的正文字体（仿宋_GB2312）
  - 正确的数字字体（Times New Roman）
  - eastAsia 字体属性正确写入 XML
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from core.document.generator import generate_docx
from core.document.models import (
    DocumentModel, Paragraph, Run, RunFormat,
    ParagraphFormat, PageSetup
)
from utils.logger import logger
from config import APP_DATA_DIR

router = APIRouter()

# Define DATA_DIR
DATA_DIR = APP_DATA_DIR


@router.get("/download/{template_id}")
async def download_template(template_id: str):
    """
    Generate and download a template document with pre-configured styles.

    Args:
        template_id: Template identifier (e.g., 'notice', 'request')

    Returns:
        FileResponse with the generated .docx file
    """
    try:
        # Load template configuration
        from core.rules.manager import load_rules_merged
        rules = load_rules_merged(template_id)

        template_name = rules.get("template_name", template_id)

        # Create a sample document with configured styles
        doc_model = _create_template_document(template_id, rules)

        # Generate the document
        output_dir = DATA_DIR / "templates"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{template_id}_template.docx"
        generate_docx(doc_model, output_path)

        logger.info(f"Generated template document: {template_id}")

        return FileResponse(
            path=str(output_path),
            filename=f"{template_name}模板.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        logger.error(f"Download template {template_id} failed: {e}")
        raise HTTPException(status_code=500, detail=f"生成模板失败: {str(e)}")


def _create_template_document(template_id: str, rules: dict) -> DocumentModel:
    """
    Create a sample document with styles from the template rules.
    根据公文类型生成不同的示例内容，所有格式严格遵循 YAML 规则。
    """
    # Extract style configurations
    title_config = rules.get("title", {})
    body_config = rules.get("body", {})

    # 页码边距 - 优先用 page_setup 规则，回退到 _common 标准
    page_setup_rules = rules.get("page_setup", {})
    margins = page_setup_rules.get("margins", {})

    template_name = rules.get("template_name", "文档")

    # Create document model with proper page setup
    doc = DocumentModel(
        filename=f"{template_id}_template.docx",
        page_setup=PageSetup(
            paper_width_mm=210,
            paper_height_mm=297,
            margin_top_mm=_parse_margin(margins.get("top", "3.7cm")),
            margin_bottom_mm=_parse_margin(margins.get("bottom", "3.5cm")),
            margin_left_mm=_parse_margin(margins.get("left", "2.8cm")),
            margin_right_mm=_parse_margin(margins.get("right", "2.6cm")),
        ),
    )

    # 根据模板类型生成不同的示例内容
    template_content = _get_template_content(template_id, template_name)

    # Add title paragraph
    title_para = Paragraph(
        text=template_content["title"],
        index=0,
        is_heading=True,
        heading_level=1,
        format=ParagraphFormat(
            alignment=title_config.get("align", "center"),
            first_line_indent_pt=0,
            space_after_pt=_parse_size(title_config.get("spacing_after", 20)),
        ),
        runs=[
            Run(
                index=0,
                text=template_content["title"],
                format=RunFormat(
                    font_name=title_config.get("font", "方正小标宋简体"),
                    font_size_pt=_parse_size(title_config.get("size", 22)),
                    bold=title_config.get("bold", False),
                ),
            )
        ],
    )
    doc.paragraphs.append(title_para)

    # Add body paragraphs
    for idx, para_text in enumerate(template_content["paragraphs"]):
        if not para_text.strip():
            # Empty paragraph
            empty_para = Paragraph(
                text="",
                index=idx + 1,
                format=ParagraphFormat(),
                runs=[],
            )
            doc.paragraphs.append(empty_para)
            continue

        # Determine if this is a signature/date paragraph (right-aligned)
        is_signature = any(k in para_text for k in ["落款", "单位名称", "XXXX年"])

        alignment = "right" if is_signature else body_config.get("align", "justify")
        indent = 0 if (is_signature or _is_recipient(para_text)) else \
            _parse_indent(body_config.get("first_line_indent", "2em"))

        body_para = Paragraph(
            text=para_text,
            index=idx + 1,
            format=ParagraphFormat(
                alignment=alignment,
                first_line_indent_pt=indent,
                line_spacing_pt=_parse_size(body_config.get("line_spacing", 28.95)),
            ),
            runs=[
                Run(
                    index=0,
                    text=para_text,
                    format=RunFormat(
                        font_name=body_config.get("font", "仿宋_GB2312"),
                        font_size_pt=_parse_size(body_config.get("size", 16)),
                    )
                )
            ],
        )
        doc.paragraphs.append(body_para)

    return doc


def _is_recipient(text: str) -> bool:
    """Check if paragraph text is a recipient/salutation line."""
    return bool(text.strip().endswith("：") or text.strip().endswith(":"))


def _get_template_content(template_id: str, template_name: str) -> dict:
    """
    Get template-specific sample content.
    根据不同公文类型返回相应的示例内容。
    """
    templates = {
        "notice": {
            "title": f"关于XXX工作的通知",
            "paragraphs": [
                "",
                "各部门、各单位：",
                "",
                "为进一步做好XXX工作，现将有关事项通知如下：",
                "一、工作目标",
                "（具体内容）",
                "二、工作要求",
                "（具体内容）",
                "三、其他事项",
                "（具体内容）",
                "特此通知。",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "request": {
            "title": f"关于XXX事项的请示",
            "paragraphs": [
                "",
                "XXX（上级机关）：",
                "",
                "根据XXX工作需要，现就XXX事项请示如下：",
                "一、基本情况",
                "（具体内容）",
                "二、请示事项",
                "（具体内容）",
                "三、建议方案",
                "（具体内容）",
                "以上请示妥否，请批复。",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "report": {
            "title": f"关于XXX工作的报告",
            "paragraphs": [
                "",
                "XXX（上级机关）：",
                "",
                "根据XXX要求，现将XXX工作情况报告如下：",
                "一、工作开展情况",
                "（具体内容）",
                "二、主要成效",
                "（具体内容）",
                "三、存在问题",
                "（具体内容）",
                "四、下一步工作计划",
                "（具体内容）",
                "特此报告。",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "meeting": {
            "title": f"XXX会议纪要",
            "paragraphs": [
                "",
                "时间：XXXX年XX月XX日XX时",
                "地点：XXX会议室",
                "主持人：XXX",
                "参会人员：XXX、XXX、XXX等XX人",
                "",
                "会议主要内容：",
                "一、XXX议题",
                "（具体内容）",
                "二、XXX议题",
                "（具体内容）",
                "",
                "会议决定：",
                "一、（决定事项）",
                "二、（决定事项）",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "letter": {
            "title": f"关于XXX事项的函",
            "paragraphs": [
                "",
                "XXX（受文单位）：",
                "",
                "你单位《关于XXX的XXX》收悉。经研究，现函复如下：",
                "（具体内容）",
                "特此函告。",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "decision": {
            "title": f"关于XXX的决定",
            "paragraphs": [
                "",
                "为XXX，经研究决定：",
                "一、（决定事项）",
                "二、（决定事项）",
                "三、（决定事项）",
                "本决定自发布之日起施行。",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "announcement": {
            "title": f"关于XXX的通告",
            "paragraphs": [
                "",
                "为XXX，现通告如下：",
                "一、（通告内容）",
                "二、（通告内容）",
                "三、（通告内容）",
                "特此通告。",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "notice_public": {
            "title": f"关于XXX的公告",
            "paragraphs": [
                "",
                "根据XXX，现公告如下：",
                "一、（公告内容）",
                "二、（公告内容）",
                "三、（公告内容）",
                "特此公告。",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "communique": {
            "title": f"XXX公报",
            "paragraphs": [
                "",
                "（XXXX年XX月XX日）",
                "",
                "XXX会议于XXXX年XX月XX日在XXX举行。会议XXX。",
                "会议指出，（具体内容）。",
                "会议强调，（具体内容）。",
                "会议认为，（具体内容）。",
                "会议要求，（具体内容）。",
                "",
                "",
                "（发布机关）",
                "XXXX年XX月XX日",
            ],
        },
        "resolution": {
            "title": f"关于XXX的决议",
            "paragraphs": [
                "",
                "（XXXX年XX月XX日XXX会议通过）",
                "",
                "XXX会议审议了XXX，会议决定：",
                "一、（决议事项）",
                "二、（决议事项）",
                "三、（决议事项）",
                "会议号召，（具体号召内容）。",
                "",
                "",
                "（会议名称）",
                "XXXX年XX月XX日",
            ],
        },
        "command": {
            "title": f"XXX令",
            "paragraphs": [
                "",
                "第XXX号",
                "",
                "《XXX规定》已经XXXX年XX月XX日XXX会议通过，现予公布，自XXXX年XX月XX日起施行。",
                "",
                "",
                "（签发人职务）  （签发人姓名）",
                "XXXX年XX月XX日",
            ],
        },
        "bill": {
            "title": f"关于提请审议《XXX》的议案",
            "paragraphs": [
                "",
                "XXX（审议机关）：",
                "",
                "为了XXX，XXX（起草单位）拟定了《XXX》。现提请审议。",
                "一、制定背景",
                "（具体内容）",
                "二、主要内容",
                "（具体内容）",
                "三、需要说明的问题",
                "（具体内容）",
                "",
                "",
                "（提案机关/提案人）",
                "XXXX年XX月XX日",
            ],
        },
        "bulletin": {
            "title": f"关于XXX的通报",
            "paragraphs": [
                "",
                "各部门、各单位：",
                "",
                "（通报事由概述）。",
                "一、基本情况",
                "（具体内容）",
                "二、原因分析",
                "（具体内容）",
                "三、处理意见",
                "（具体内容）",
                "四、工作要求",
                "（具体内容）",
                "特此通报。",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "table_sign": {
            "title": "XXX",
            "paragraphs": [
                "",
                "",
                "",
                "",
            ],
        },
        "minutes": {
            "title": "XXX会议纪要",
            "paragraphs": [
                "",
                "时间：XXXX年XX月XX日",
                "地点：XXX会议室",
                "主持人：XXX",
                "出席人员：XXX、XXX、XXX",
                "缺席人员：XXX",
                "记录人：XXX",
                "",
                "会议议定事项如下：",
                "",
                "一、关于XXX事项",
                "会议认为，（具体内容）。",
                "会议决定，（具体内容）。",
                "",
                "二、关于XXX事项",
                "会议认为，（具体内容）。",
                "会议决定，（具体内容）。",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "instruction": {
            "title": "关于XXX工作的指示",
            "paragraphs": [
                "",
                "各部门、各单位：",
                "",
                "当前，XXX工作面临新的形势和任务。为切实做好XXX工作，现作如下指示：",
                "一、充分认识XXX工作的重要意义",
                "（具体内容）",
                "二、明确XXX工作的总体要求和目标任务",
                "（具体内容）",
                "三、切实加强XXX工作的组织领导",
                "（具体内容）",
                "各级各部门要认真贯彻落实本指示精神，确保各项工作落到实处。",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "regulation": {
            "title": "XXX管理办法",
            "paragraphs": [
                "",
                "第一章  总则",
                "",
                "第一条  为加强XXX管理，规范XXX行为，根据XXX有关规定，制定本办法。",
                "第二条  本办法适用于XXX范围内的XXX活动。",
                "第三条  XXX工作应当遵循XXX原则。",
                "",
                "第二章  XXX",
                "",
                "第四条  （具体内容）",
                "第五条  （具体内容）",
                "",
                "第三章  XXX",
                "",
                "第六条  （具体内容）",
                "第七条  （具体内容）",
                "",
                "第四章  附则",
                "",
                "第八条  本办法由XXX负责解释。",
                "第九条  本办法自XXXX年XX月XX日起施行。",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "summary": {
            "title": "关于XXX工作的总结",
            "paragraphs": [
                "",
                "XXX（上级机关）：",
                "",
                "根据XXX要求，现将XXX工作情况总结如下：",
                "一、基本情况",
                "（总体概述工作背景和完成情况）",
                "二、主要做法和成效",
                "（具体内容）",
                "三、存在的主要问题",
                "（具体内容）",
                "四、下一步工作打算",
                "（具体内容）",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "work_plan": {
            "title": "关于XXX工作的实施方案",
            "paragraphs": [
                "",
                "为深入贯彻落实XXX精神，扎实推进XXX工作，制定本方案。",
                "",
                "一、指导思想",
                "（具体内容）",
                "",
                "二、工作目标",
                "（具体内容）",
                "",
                "三、主要任务",
                "（一）XXX。",
                "（二）XXX。",
                "（三）XXX。",
                "",
                "四、实施步骤",
                "（一）准备阶段（XXXX年XX月—XX月）。",
                "（二）实施阶段（XXXX年XX月—XX月）。",
                "（三）总结阶段（XXXX年XX月—XX月）。",
                "",
                "五、保障措施",
                "（具体内容）",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "reply": {
            "title": "关于XXX的批复",
            "paragraphs": [
                "",
                "XXX（下级机关）：",
                "",
                "你单位《关于XXX的请示》（XXX〔XXXX〕X号）收悉。经研究，现批复如下：",
                "一、（批复意见）",
                "二、（批复意见）",
                "此复。",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
        "opinion": {
            "title": "关于XXX工作的意见",
            "paragraphs": [
                "",
                "各部门、各单位：",
                "",
                "为深入贯彻落实XXX精神，加快推进XXX工作，现提出以下意见：",
                "一、充分认识XXX的重要意义",
                "（具体内容）",
                "二、总体要求",
                "（具体内容）",
                "三、主要措施",
                "（具体内容）",
                "四、组织保障",
                "（具体内容）",
                "",
                "",
                "（单位名称）",
                "XXXX年XX月XX日",
            ],
        },
    }

    # Default template if not found
    default = {
        "title": f"{template_name}标题",
        "paragraphs": [
            "",
            "正文第一段内容。",
            "正文第二段内容。",
            "正文第三段内容。",
            "",
            "",
            "（单位名称）",
            "XXXX年XX月XX日",
        ],
    }

    return templates.get(template_id, default)


def _parse_size(size_value) -> float:
    """Parse size value like '22pt', 22, or '22pt' to float."""
    if isinstance(size_value, (int, float)):
        return float(size_value)
    return float(str(size_value).replace("pt", "").strip())


def _parse_indent(indent_str) -> float:
    """Parse indent string like '2em' to points (assuming 1em ≈ 16pt)."""
    if isinstance(indent_str, (int, float)):
        return float(indent_str)
    indent_str = str(indent_str).strip()
    if "em" in indent_str:
        em_value = float(indent_str.replace("em", "").strip())
        return em_value * 16  # 1em ≈ 16pt for Chinese fonts
    return float(indent_str.replace("pt", "").strip())


def _parse_margin(value) -> float:
    """Parse margin value like '3.7cm' or '37mm' to mm."""
    if isinstance(value, (int, float)):
        return float(value)
    value = str(value).strip()
    if "cm" in value:
        return float(value.replace("cm", "").strip()) * 10
    elif "mm" in value:
        return float(value.replace("mm", "").strip())
    return float(value)