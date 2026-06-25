# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
Templates management API: create, read, update templates.
支持两种模板体系：
  1. 规则模板 (rules/official/) — 用于格式检查和修复
  2. 样式模板 (templates/official/) — 用于生成 Word 模板文件
  3. 预置 .dotx 模板 (公文模板/) — 可直接使用的 Word 模板文件
"""
from fastapi import APIRouter, Depends, HTTPException, Query
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
TEMPLATES_DOTX_DIR = BASE_DIR / "公文模板"

# 生成的模板输出目录（可写，位于用户数据目录）
_GENERATED_TEMPLATES_DIR = APP_DATA_DIR / "generated_templates"

# template_id → 中文文件名映射（与公文模板/ 目录中的文件名对应）
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
    for template in templates:
        rule_path = RULES_DIR / template["rule_file"]
        template["has_rules"] = rule_path.exists()

    logger.info(f"Listed {len(templates)} templates")
    return {"templates": templates}


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
        logger.error(f"Style template download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        logger.error(f"Dotx template download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
#  预置 .dotx 模板下载（公文模板/ 体系）
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
    优先从 公文模板/ 目录读取真实模板（带品牌替换），
    若不存在则回退到样式模板引擎动态生成。
    """
    cn_name = _TEMPLATE_ID_TO_CN.get(template_id, template_id)
    output_dir = _GENERATED_TEMPLATES_DIR / "processed_dotx"
    output_dir.mkdir(parents=True, exist_ok=True)
    cached_path = output_dir / f"{cn_name}.dotx"

    # 1. 优先从 公文模板/ 目录读取真实 .dotx 文件
    source_dotx = TEMPLATES_DOTX_DIR / f"{cn_name}.dotx"
    if source_dotx.exists():
        # 检查缓存：如果缓存文件比源文件新则直接使用
        if cached_path.exists() and cached_path.stat().st_mtime >= source_dotx.stat().st_mtime:
            logger.info(f"使用缓存的 .dotx 模板: {cn_name}")
        else:
            # 执行品牌替换并缓存
            logger.info(f"从公文模板/读取 .dotx 模板: {cn_name}")
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
