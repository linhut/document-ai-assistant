# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Templates management API: create, read, update templates.
支持两种模板体系：
  1. 规则模板 (rules/official/) — 用于格式检查和修复
  2. 样式模板 (templates/official/) — 用于生成 Word 模板文件
  3. 预置 .dotx 模板 (dotx_templates/) — 可直接使用的 Word 模板文件
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import yaml
import tempfile
import shutil
import zipfile
import os

from config import RULES_DIR, BASE_DIR, APP_DATA_DIR
from utils.logger import logger

router = APIRouter()

# 预置 .dotx 模板目录（只读，捆绑在安装目录）
OFFICIAL_TEMPLATES_DIR = BASE_DIR / "templates" / "official"

# 真实的 .dotx 模板文件目录（来自公文模板项目）
TEMPLATES_DOTX_DIR = BASE_DIR / "dotx_templates"

# 生成的模板输出目录（可写，位于用户数据目录）
_GENERATED_TEMPLATES_DIR = APP_DATA_DIR / "generated_templates"

# template_id → 中文文件名映射（与 dotx_templates/ 目录中的文件名对应）
_TEMPLATE_ID_TO_CN = {
    "notice": "通知", "request": "请示", "report": "报告", "letter": "函",
    "meeting": "会议纪要", "decision": "决定", "announcement": "通告",
    "notice_public": "公告", "opinion": "意见", "reply": "批复",
    "minutes": "纪要", "instruction": "指示", "work_plan": "工作方案",
    "summary": "总结", "regulation": "制度", "communique": "公报",
    "resolution": "决议", "command": "命令", "bill": "议案",
    "bulletin": "通报", "table_sign": "桌签",
}

# 需要在模板文件中替换的品牌名
_BRAND_REPLACEMENTS = [
    ("小恐龙", "Jose AI"),
    ("小恐龙公文", "Jose AI公文"),
    ("xkonglong", "Jose AI"),
]


class TemplateCreate(BaseModel):
    name: str
    document_type: str
    description: str
    icon: str = "📄"


@router.get("/list")
async def list_templates():
    """List all available document templates."""
    templates = [
        # 政府机关公文（8个）
        {
            "id": "notice",
            "name": "通知",
            "description": "工作通知、会议通知、部署通知等",
            "icon": "📄",
            "category": "government",
            "rule_file": "notice.yaml",
            "enabled": True
        },
        {
            "id": "request",
            "name": "请示",
            "description": "请示上级批准事项",
            "icon": "📝",
            "category": "government",
            "rule_file": "request.yaml",
            "enabled": True
        },
        {
            "id": "report",
            "name": "报告",
            "description": "工作报告、情况报告等",
            "icon": "📊",
            "category": "government",
            "rule_file": "report.yaml",
            "enabled": True
        },
        {
            "id": "letter",
            "name": "函",
            "description": "机关之间商洽工作、询问和答复问题",
            "icon": "✉️",
            "category": "government",
            "rule_file": "letter.yaml",
            "enabled": True
        },
        {
            "id": "meeting",
            "name": "会议纪要",
            "description": "记录会议主要情况和议定事项",
            "icon": "🗓️",
            "category": "government",
            "rule_file": "meeting.yaml",
            "enabled": True
        },
        {
            "id": "decision",
            "name": "决定",
            "description": "对重要事项作出决策和部署",
            "icon": "⚖️",
            "category": "government",
            "rule_file": "decision.yaml",
            "enabled": True
        },
        {
            "id": "announcement",
            "name": "通告",
            "description": "公布社会有关方面应当遵守或周知的事项",
            "icon": "📢",
            "category": "government",
            "rule_file": "announcement.yaml",
            "enabled": True
        },
        {
            "id": "notice_public",
            "name": "公告",
            "description": "向国内外宣布重要事项或法定事项",
            "icon": "📣",
            "category": "government",
            "rule_file": "notice_public.yaml",
            "enabled": True
        },
        # 扩展公文（4个）
        {
            "id": "opinion",
            "name": "意见",
            "description": "对重要问题提出见解和处理办法",
            "icon": "💡",
            "category": "government",
            "rule_file": "opinion.yaml",
            "enabled": True
        },
        {
            "id": "reply",
            "name": "批复",
            "description": "答复下级机关请示事项",
            "icon": "✅",
            "category": "government",
            "rule_file": "reply.yaml",
            "enabled": True
        },
        {
            "id": "minutes",
            "name": "纪要",
            "description": "记载会议主要精神和议定事项",
            "icon": "📋",
            "category": "government",
            "rule_file": "minutes.yaml",
            "enabled": True
        },
        {
            "id": "instruction",
            "name": "指示",
            "description": "对下级机关布置工作、提出要求",
            "icon": "👉",
            "category": "government",
            "rule_file": "instruction.yaml",
            "enabled": True
        },
        # 其他常用（3个）
        {
            "id": "work_plan",
            "name": "工作方案",
            "description": "工作计划和实施方案",
            "icon": "📋",
            "category": "common",
            "rule_file": "work_plan.yaml",
            "enabled": True
        },
        {
            "id": "summary",
            "name": "总结",
            "description": "工作总结和汇报总结",
            "icon": "📝",
            "category": "common",
            "rule_file": "summary.yaml",
            "enabled": True
        },
        {
            "id": "regulation",
            "name": "制度",
            "description": "规章制度和管理办法",
            "icon": "📜",
            "category": "common",
            "rule_file": "regulation.yaml",
            "enabled": True
        },
        # 新增公文类型（6个）
        {
            "id": "communique",
            "name": "公报",
            "description": "公布重要决定或重大事件",
            "icon": "📰",
            "category": "government",
            "rule_file": "communique.yaml",
            "enabled": True
        },
        {
            "id": "resolution",
            "name": "决议",
            "description": "经会议讨论通过的重大决策事项",
            "icon": "🗳️",
            "category": "government",
            "rule_file": "resolution.yaml",
            "enabled": True
        },
        {
            "id": "command",
            "name": "命令",
            "description": "公布行政法规和规章、宣布施行重大强制性措施",
            "icon": "⚔️",
            "category": "government",
            "rule_file": "command.yaml",
            "enabled": True
        },
        {
            "id": "bill",
            "name": "议案",
            "description": "向人大或常委会提请审议事项",
            "icon": "📑",
            "category": "government",
            "rule_file": "bill.yaml",
            "enabled": True
        },
        {
            "id": "bulletin",
            "name": "通报",
            "description": "表彰先进、批评错误、传达重要情况",
            "icon": "🔔",
            "category": "government",
            "rule_file": "bulletin.yaml",
            "enabled": True
        },
        {
            "id": "table_sign",
            "name": "桌签",
            "description": "会议桌签和席卡模板",
            "icon": "🏷️",
            "category": "common",
            "rule_file": "table_sign.yaml",
            "enabled": True
        },
        {
            "id": "technical_proposal",
            "name": "技术方案",
            "description": "项目技术方案、实施方案、技术报告",
            "icon": "🔧",
            "category": "common",
            "rule_file": "technical_proposal.yaml",
            "enabled": True
        },
    ]

    # Check which rule files exist
    existing_ids = set()
    for template in templates:
        rule_path = RULES_DIR / template["rule_file"]
        template["has_rules"] = rule_path.exists()
        template["source"] = "official"
        existing_ids.add(template["id"])

    # 扫描 custom_rules 和 user_rules 目录，追加自定义模板
    from config import CUSTOM_RULES_DIR, USER_RULES_DIR
    for source, src_label in [(CUSTOM_RULES_DIR, "custom"), (USER_RULES_DIR, "user")]:
        if not source.exists():
            continue
        for f in sorted(source.glob("*.yaml")):
            if f.stem.startswith("_"):
                continue
            if f.stem in existing_ids:
                continue
            existing_ids.add(f.stem)
            # 尝试读取 template_name
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = yaml.safe_load(fh) or {}
                name = data.get("template_name", f.stem)
            except Exception:
                name = f.stem
            templates.append({
                "id": f.stem,
                "name": name,
                "description": f"自定义规则（{src_label}）",
                "icon": "📋",
                "category": "custom",
                "rule_file": f.name,
                "has_rules": True,
                "source": src_label,
                "enabled": True,
            })

    logger.info(f"Listed {len(templates)} templates")
    return {"templates": templates}


# NOTE: /{template_id} 必须放在所有 /xxx 固定路由之后，否则会拦截 /create、/extract 等路径


@router.post("/create")
async def create_template(data: TemplateCreate):
    """Create a new template from basic model."""
    from config import USER_RULES_DIR
    USER_RULES_DIR.mkdir(parents=True, exist_ok=True)
    template_file = USER_RULES_DIR / f"{data.document_type}.yaml"

    if template_file.exists():
        raise HTTPException(status_code=400, detail="Template already exists")

    # Create basic template structure
    template_data = {
        "template_name": data.name,
        "document_type": data.document_type,
        "title": {
            "font": "方正小标宋简体",
            "font_fallback": "SimSun",
            "size": "22pt",
            "align": "center",
            "bold": False
        },
        "body": {
            "font": "仿宋_GB2312",
            "font_fallback": "FangSong",
            "size": "16pt",
            "line_spacing": "28.95pt",
            "first_line_indent": "2em",
            "align": "justify"
        },
        "check_rules": [
            {
                "id": f"CHK-{data.document_type.upper()[:3]}001",
                "name": "标题字体检查",
                "severity": "P0",
                "field": "title.font",
                "expected": "方正小标宋简体",
                "message": "标题应使用方正小标宋简体"
            },
            {
                "id": f"CHK-{data.document_type.upper()[:3]}002",
                "name": "正文字体检查",
                "severity": "P0",
                "field": "body.font",
                "expected": "仿宋_GB2312",
                "message": "正文应使用仿宋_GB2312字体"
            }
        ],
        "fix_rules": [
            {
                "id": f"FIX-{data.document_type.upper()[:3]}001",
                "ref_check": f"CHK-{data.document_type.upper()[:3]}001",
                "action": "set_font",
                "target": "title",
                "value": "方正小标宋简体"
            },
            {
                "id": f"FIX-{data.document_type.upper()[:3]}002",
                "ref_check": f"CHK-{data.document_type.upper()[:3]}002",
                "action": "set_font",
                "target": "body",
                "value": "仿宋_GB2312"
            }
        ]
    }

    # Write YAML file
    with open(template_file, 'w', encoding='utf-8') as f:
        yaml.dump(template_data, f, allow_unicode=True, sort_keys=False)

    logger.info(f"Created template: {data.document_type}")
    return {
        "success": True,
        "template_id": data.document_type,
        "message": f"模板 {data.name} 创建成功"
    }


# ---------------------------------------------------------------------------
#  导入文档自动生成模板规则
# ---------------------------------------------------------------------------

class SaveExtractedRequest(BaseModel):
    template_name: str
    document_type: str
    yaml_content: dict


@router.post("/extract")
async def extract_template_from_doc(file: UploadFile = File(...)):
    """从上传的 .docx 文档中提取格式信息，生成规则模板预览。"""
    import re

    # 校验文件类型
    filename = file.filename or "document.docx"
    ext = Path(filename).suffix.lower()
    if ext not in ('.docx', '.doc', '.wps'):
        raise HTTPException(status_code=400, detail="仅支持 .docx/.doc/.wps 格式")

    # 保存到临时目录
    tmp_dir = Path(tempfile.mkdtemp())
    safe_name = re.sub(r'[^\w一-鿿._-]', '_', Path(filename).name)
    tmp_path = tmp_dir / safe_name

    try:
        content = await file.read()
        with open(tmp_path, 'wb') as f:
            f.write(content)

        # .doc/.wps 转 .docx
        if ext in ('.doc', '.wps'):
            from core.document.converter import convert_to_docx
            tmp_path = convert_to_docx(tmp_path, tmp_dir)

        # 提取格式
        from core.document.format_extractor import (
            FormatExtractor, extract_format_from_docx, generate_template_from_docx
        )
        from core.document.parser import parse_docx

        model = parse_docx(str(tmp_path))
        extractor = FormatExtractor(model)
        extracted = extractor.extract_all()

        # 生成默认模板名和类型标识
        stem = Path(filename).stem
        # 尝试从文件名推断类型
        from services.document_service import _detect_doc_type
        doc_type = _detect_doc_type(filename)
        template_name = stem

        # 生成 YAML 预览
        yaml_data = extractor.generate_yaml(template_name, doc_type)
        yaml_preview = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False)

        return {
            "success": True,
            "template_name": template_name,
            "document_type": doc_type,
            "format_info": extracted['summary'],
            "sections": extracted['sections'],
            "page_setup": extracted['page_setup'],
            "check_rules_count": len(yaml_data.get('check_rules', [])),
            "fix_rules_count": len(yaml_data.get('fix_rules', [])),
            "yaml_preview": yaml_preview,
            "yaml_content": yaml_data,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Format extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"格式提取失败: {str(e)}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@router.post("/{template_id}/preview")
async def preview_template(template_id: str):
    """根据模板规则生成示例文档，返回 A4 预览数据。"""
    from core.rules.manager import load_rules_merged
    from core.document.models import (
        DocumentModel, DocumentMetadata, PageSetup,
        Paragraph, ParagraphFormat, Run, RunFormat,
    )

    try:
        rules = load_rules_merged(template_id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"模板 {template_id} 不存在")

    # 从规则中提取格式定义
    title_fmt = rules.get('doc_title') or rules.get('title') or {}
    h1_fmt = rules.get('heading_1') or {}
    h2_fmt = rules.get('heading_2') or {}
    h3_fmt = rules.get('heading_3') or {}
    body_fmt = rules.get('body') or {}
    sig_fmt = rules.get('signature') or {}
    date_fmt = rules.get('date') or {}
    ps = rules.get('page_setup', {})
    margins = ps.get('margins', {})

    def _parse_pt(val, default=16):
        if val is None: return default
        s = str(val).replace('pt', '').strip()
        try: return float(s)
        except: return default

    def _parse_cm(val, default_mm=37):
        if val is None: return default_mm
        s = str(val).replace('cm', '').replace('mm', '').strip()
        try:
            v = float(s)
            return v * 10 if 'cm' in str(val) else v
        except: return default_mm

    def _parse_indent(val, base_pt=16):
        if val is None: return None
        s = str(val)
        if 'em' in s:
            try: return float(s.replace('em', '').strip()) * base_pt
            except: return None
        return _parse_pt(val, None)

    def _mk_para(text, font=None, size=None, align=None, bold=False, indent=None,
                 line_spacing=None, is_heading=False, heading_level=None, role=None):
        rf = RunFormat(font_name=font, font_size_pt=size, bold=bold or None)
        pf = ParagraphFormat(
            alignment=align,
            first_line_indent_pt=indent,
            line_spacing_pt=line_spacing,
            line_spacing_rule='exact' if line_spacing else None,
        )
        return Paragraph(
            index=0, text=text, is_heading=is_heading,
            heading_level=heading_level, role=role,
            runs=[Run(index=0, text=text, format=rf)],
            format=pf,
        )

    body_size = _parse_pt(body_fmt.get('size'), 16)
    body_indent = _parse_indent(body_fmt.get('first_line_indent'), body_size)

    paras = []
    idx = 0

    # 标题
    template_name = rules.get('template_name', template_id)
    paras.append(_mk_para(
        f"关于印发《{template_name}》的通知",
        font=title_fmt.get('font', '方正小标宋简体'),
        size=_parse_pt(title_fmt.get('size'), 22),
        align=title_fmt.get('align', 'center'),
        is_heading=True, heading_level=0, role='title',
    ))
    paras[-1].index = idx; idx += 1

    # 一级标题
    if h1_fmt:
        paras.append(_mk_para(
            "一、总体要求",
            font=h1_fmt.get('font', '黑体'),
            size=_parse_pt(h1_fmt.get('size'), 16),
            align=h1_fmt.get('align', 'left'),
            is_heading=True, heading_level=1,
        ))
        paras[-1].index = idx; idx += 1

    # 正文段落
    sample_body = [
        "为深入贯彻落实上级文件精神，进一步规范工作流程，提高工作效率，确保各项工作任务有序推进，结合实际情况，特制定本方案。",
        "各单位要高度重视，认真组织实施，确保各项工作要求落到实处。要加强沟通协调，及时反馈工作中遇到的问题和困难。",
    ]
    for text in sample_body:
        paras.append(_mk_para(
            text,
            font=body_fmt.get('font', '仿宋_GB2312'),
            size=body_size,
            align=body_fmt.get('align', 'justify'),
            indent=body_indent,
            line_spacing=_parse_pt(body_fmt.get('line_spacing'), 28.95),
            role='body',
        ))
        paras[-1].index = idx; idx += 1

    # 二级标题
    if h2_fmt:
        paras.append(_mk_para(
            "（一）加强组织领导",
            font=h2_fmt.get('font', '楷体_GB2312'),
            size=_parse_pt(h2_fmt.get('size'), 16),
            align=h2_fmt.get('align'),
            is_heading=True, heading_level=2,
        ))
        paras[-1].index = idx; idx += 1
        paras.append(_mk_para(
            "各责任部门要明确专人负责，建立工作台账，定期检查工作进展情况，确保各项措施有效落实。",
            font=body_fmt.get('font', '仿宋_GB2312'), size=body_size,
            align=body_fmt.get('align', 'justify'), indent=body_indent,
            line_spacing=_parse_pt(body_fmt.get('line_spacing'), 28.95), role='body',
        ))
        paras[-1].index = idx; idx += 1

    # 三级标题
    if h3_fmt:
        paras.append(_mk_para(
            "1. 明确责任分工",
            font=h3_fmt.get('font', '仿宋_GB2312'),
            size=_parse_pt(h3_fmt.get('size'), 16),
            bold=h3_fmt.get('bold', True),
            is_heading=True, heading_level=3,
        ))
        paras[-1].index = idx; idx += 1

    # 落款 + 日期
    paras.append(_mk_para(
        rules.get('template_name', 'XX单位'),
        font=sig_fmt.get('font', '仿宋_GB2312'), size=_parse_pt(sig_fmt.get('size'), 16),
        align=sig_fmt.get('align', 'right'), role='signature',
    ))
    paras[-1].index = idx; idx += 1
    paras.append(_mk_para(
        "2026年06月25日",
        font=date_fmt.get('font', '仿宋_GB2312'), size=_parse_pt(date_fmt.get('size'), 16),
        align=date_fmt.get('align', 'right'), role='date',
    ))
    paras[-1].index = idx; idx += 1

    # 组装预览数据
    paragraphs_data = []
    for p in paras:
        rf = p.runs[0].format if p.runs else RunFormat()
        paragraphs_data.append({
            "text": p.text,
            "role": p.role,
            "is_heading": p.is_heading,
            "heading_level": p.heading_level,
            "format": {
                "alignment": p.format.alignment,
                "first_line_indent_pt": p.format.first_line_indent_pt,
                "font_name": rf.font_name,
                "font_size_pt": rf.font_size_pt,
                "line_spacing_pt": p.format.line_spacing_pt,
            },
        })

    return {
        "paragraphs": paragraphs_data,
        "page_setup": {
            "margin_top_mm": _parse_cm(margins.get('top'), 37),
            "margin_bottom_mm": _parse_cm(margins.get('bottom'), 35),
            "margin_left_mm": _parse_cm(margins.get('left'), 28),
            "margin_right_mm": _parse_cm(margins.get('right'), 26),
        },
    }


@router.post("/save-extracted")
async def save_extracted_template(body: SaveExtractedRequest):
    """保存从文档提取的规则模板。"""
    from config import CUSTOM_RULES_DIR, USER_RULES_DIR
    from core.rules.manager import validate_rule, save_rule

    # 校验文档类型标识
    doc_type = body.document_type.strip()
    if not doc_type or not doc_type.replace('_', '').replace('-', '').isalnum():
        raise HTTPException(status_code=400, detail="文档类型标识只能包含字母、数字、下划线和连字符")

    # 校验规则结构
    try:
        validate_rule(body.yaml_content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"规则格式无效: {str(e)}")

    # 确保 template_name 同步
    body.yaml_content['template_name'] = body.template_name
    body.yaml_content['document_type'] = doc_type

    # 保存到 USER_RULES_DIR（用户规则目录）
    USER_RULES_DIR.mkdir(parents=True, exist_ok=True)
    file_path = USER_RULES_DIR / f"{doc_type}.yaml"

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(body.yaml_content, f, allow_unicode=True, default_flow_style=False)
        logger.info(f"Extracted template saved: {file_path}")
    except Exception as e:
        logger.error(f"Failed to save extracted template: {e}")
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")

    # 清除规则缓存
    import services.document_service as svc
    svc.clear_rule_cache()

    return {
        "success": True,
        "document_type": doc_type,
        "file_path": str(file_path),
        "message": f"模板 '{body.template_name}' 已保存为自定义规则",
    }


# ---------------------------------------------------------------------------
#  样式模板中心 API（templates/official/ 体系）
# ---------------------------------------------------------------------------

@router.get("/styles/list")
async def list_style_templates(source: str = Query("all", pattern="^(all|official|custom|user)$")):
    """列出所有样式模板。"""
    from core.template.style_manager import list_templates
    templates = list_templates(source)
    return {"templates": templates, "total": len(templates)}


@router.get("/styles/{template_id}")
async def get_style_template(template_id: str, source: str = Query("all")):
    """获取单个样式模板详情。"""
    from core.template.style_manager import get_template
    template = get_template(template_id, source)
    if not template:
        raise HTTPException(status_code=404, detail=f"Style template not found: {template_id}")
    return template


@router.get("/styles/{template_id}/download/docx")
async def download_style_template_docx(template_id: str):
    """下载样式模板 .docx 文件。"""
    from core.template.generator import generate_docx_template
    output_dir = _GENERATED_TEMPLATES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{template_id}_style.docx"

    try:
        generate_docx_template(template_id, output_path)
        # Get template name for the download filename
        from core.template.style_manager import get_template
        tmpl = get_template(template_id)
        name = tmpl.get("name", template_id) if tmpl else template_id

        return FileResponse(
            path=str(output_path),
            filename=f"{name}_样式模板.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        logger.error(f"Style template download failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="模板下载失败，请稍后重试")


@router.get("/styles/{template_id}/download/dotx")
async def download_style_template_dotx(template_id: str):
    """下载样式模板 .dotx 文件（可安装到 Word/WPS 模板库）。"""
    from core.template.generator import generate_dotx_template
    output_dir = _GENERATED_TEMPLATES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{template_id}_style.dotx"

    try:
        generate_dotx_template(template_id, output_path)
        from core.template.style_manager import get_template
        tmpl = get_template(template_id)
        name = tmpl.get("name", template_id) if tmpl else template_id

        return FileResponse(
            path=str(output_path),
            filename=f"{name}_样式模板.dotx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document.template",
        )
    except Exception as e:
        logger.error(f"Dotx template download failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="模板下载失败，请稍后重试")


@router.post("/styles/import")
async def import_style_template(
    template_id: str = Query(...),
    source: str = Query("user"),
    yaml_text: str = Query(""),
):
    """导入样式模板（从YAML文本）。"""
    from core.template.style_manager import import_template
    result = import_template(template_id, yaml_text, source)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Import failed"))
    return result


# ---------------------------------------------------------------------------
#  预置 .dotx 模板下载（dotx_templates/ 体系）
# ---------------------------------------------------------------------------

def _replace_brand_in_dotx(src_path: Path, dst_path: Path) -> None:
    """
    处理 .dotx 文件，将 "小恐龙" 等品牌名替换为 "Jose AI"。
    .dotx 本质是 ZIP（OOXML），遍历内部 XML 文件进行文本替换。
    """
    tmp_dir = tempfile.mkdtemp(prefix="dotx_brand_")
    try:
        # 解压 .dotx
        with zipfile.ZipFile(src_path, 'r') as zf:
            zf.extractall(tmp_dir)

        # 遍历所有 XML 文件，执行文本替换
        replaced_count = 0
        for root, dirs, files in os.walk(tmp_dir):
            for fname in files:
                if fname.endswith(('.xml', '.rels', '.vml')):
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        original = content
                        for old_text, new_text in _BRAND_REPLACEMENTS:
                            content = content.replace(old_text, new_text)
                        if content != original:
                            replaced_count += 1
                            with open(fpath, 'w', encoding='utf-8') as f:
                                f.write(content)
                    except (UnicodeDecodeError, PermissionError):
                        # 二进制XML或其他编码问题，跳过
                        pass

        # 重新打包为 .dotx
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(dst_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(tmp_dir):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    arcname = os.path.relpath(fpath, tmp_dir)
                    zf.write(fpath, arcname)

        logger.info(f"品牌替换完成: {replaced_count} 个文件已更新 -> {dst_path.name}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@router.get("/official/{template_id}/download/dotx")
async def download_official_dotx(template_id: str):
    """
    下载预置的官方 .dotx 模板文件。
    优先从 dotx_templates/ 目录读取真实模板（带品牌替换），
    若不存在则回退到样式模板引擎动态生成。
    """
    cn_name = _TEMPLATE_ID_TO_CN.get(template_id, template_id)
    output_dir = _GENERATED_TEMPLATES_DIR / "processed_dotx"
    output_dir.mkdir(parents=True, exist_ok=True)
    cached_path = output_dir / f"{cn_name}.dotx"

    # 1. 优先从 dotx_templates/ 目录读取真实 .dotx 文件
    source_dotx = TEMPLATES_DOTX_DIR / f"{cn_name}.dotx"
    if source_dotx.exists():
        # 检查缓存：如果缓存文件比源文件新则直接使用
        if cached_path.exists() and cached_path.stat().st_mtime >= source_dotx.stat().st_mtime:
            logger.info(f"使用缓存的 .dotx 模板: {cn_name}")
        else:
            # 执行品牌替换并缓存
            logger.info(f"从 dotx_templates/读取 .dotx 模板: {cn_name}")
            _replace_brand_in_dotx(source_dotx, cached_path)

        return FileResponse(
            path=str(cached_path),
            filename=f"{cn_name}_公文模板.dotx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document.template",
        )

    # 2. 回退：动态生成
    try:
        from core.template.generator import generate_dotx_template
        output_path = output_dir / f"{template_id}_generated.dotx"
        generate_dotx_template(template_id, output_path)

        from core.template.style_manager import get_template
        tmpl = get_template(template_id)
        name = tmpl.get("name", template_id) if tmpl else template_id

        return FileResponse(
            path=str(output_path),
            filename=f"{cn_name}_公文模板.dotx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document.template",
        )
    except Exception as e:
        logger.error(f"Official .dotx template download failed: {e}")
        raise HTTPException(status_code=404, detail=f"模板 {template_id} 不存在")


# ---------------------------------------------------------------------------
#  通用模板详情（放在最后，避免拦截 /create、/extract 等固定路径）
# ---------------------------------------------------------------------------

@router.get("/{template_id}")
async def get_template(template_id: str):
    """Get template details."""
    from core.rules.manager import load_rules_merged

    try:
        rules = load_rules_merged(template_id)
        return {
            "template_id": template_id,
            "rules": rules,
            "exists": True
        }
    except Exception as e:
        logger.error(f"Get template {template_id} failed: {e}")
        return {
            "template_id": template_id,
            "exists": False,
            "error": str(e)
        }
