# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
文档结构分析器 - 智能识别文档结构
基于AIPoliDoc项目的思路，结合我们的公文格式需求
"""
from __future__ import annotations
import re
from typing import List, Dict, Optional, Tuple
from core.document.models import DocumentModel, Paragraph
from utils.logger import logger


class DocumentStructureAnalyzer:
    """
    文档结构分析器

    功能：
    1. 分析未排版的文档内容
    2. 识别标题、正文、落款、日期等结构
    3. 为AI提供结构提示
    4. 辅助规则引擎进行精确匹配
    """

    def __init__(self):
        """初始化文档结构分析器"""
        # 标题关键词
        self.title_keywords = [
            "通知", "请示", "报告", "函", "纪要", "决定", "通告", "公告",
            "会议", "关于", "的通知", "的请示", "的报告", "的函"
        ]

        # 主送机关关键词
        self.recipient_keywords = [
            "各", "全体", "全市", "全县", "各部门", "各单位", "各处室",
            "市", "县", "区", "局", "办", "委", "厅"
        ]

        # 落款关键词
        self.signature_keywords = [
            "特此通知", "特此函告", "妥否", "请批复", "请示",
            "局", "办", "委", "厅", "部", "组", "处", "科"
        ]

        # 日期模式
        self.date_patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',  # 2023年1月1日
            r'\d{4}\.\d{1,2}\.\d{1,2}',     # 2023.1.1
            r'\d{4}-\d{1,2}-\d{1,2}',       # 2023-01-01
        ]

        # 会议纪要特殊关键词
        self.meeting_keywords = {
            "time": ["时间", "会议时间", "召开时间"],
            "location": ["地点", "会议地点", "召开地点"],
            "attendees": ["参会人员", "参加人员", "出席人员", "与会人员"],
            "host": ["主持人", "主持", "由", "主持会议"],
            "topics": ["议题", "会议议题", "讨论议题", "主要议题"],
            "decisions": ["决定", "会议决定", "形成决议", "一致同意"]
        }

    def analyze(self, model: DocumentModel) -> Dict[str, any]:
        """
        分析文档结构

        Args:
            model: 文档模型

        Returns:
            结构分析结果
        """
        result = {
            "title": None,          # 标题段落索引
            "recipient": None,      # 主送机关段落索引
            "body_start": None,     # 正文开始索引
            "body_end": None,       # 正文结束索引
            "signature": None,      # 落款段落索引
            "date": None,          # 日期段落索引
            "special_sections": {}, # 特殊部分（会议纪要用）
            "structure_type": None, # 文档结构类型
        }

        paragraphs = model.paragraphs
        if not paragraphs:
            logger.warning("文档无段落内容")
            return result

        # 识别标题（通常是第一个非空段落）
        result["title"] = self._find_title(paragraphs)

        # 识别主送机关（标题后的第一个段落）
        result["recipient"] = self._find_recipient(paragraphs, result["title"])

        # 识别落款和日期（文档末尾）
        result["signature"], result["date"] = self._find_signature_and_date(paragraphs)

        # 识别正文范围
        result["body_start"], result["body_end"] = self._find_body_range(
            paragraphs, result["recipient"], result["signature"]
        )

        # 识别会议纪要特殊部分
        result["special_sections"] = self._find_meeting_sections(paragraphs)

        # 判断文档结构类型
        result["structure_type"] = self._determine_structure_type(paragraphs, result)

        logger.info(f"文档结构分析完成: {result['structure_type']}")
        return result

    def _find_title(self, paragraphs: List[Paragraph]) -> Optional[int]:
        """查找标题段落"""
        for i, para in enumerate(paragraphs):
            text = para.text.strip()
            if not text:
                continue

            # 第一个非空段落，且长度不超过50字
            if len(text) <= 50:
                # 包含标题关键词
                for keyword in self.title_keywords:
                    if keyword in text:
                        logger.debug(f"识别到标题: 段落{i}, 内容: {text[:30]}...")
                        return i

                # 或者是第一个非空段落且较短
                if i < 3 and len(text) < 30:
                    logger.debug(f"识别到标题(首段): 段落{i}, 内容: {text[:30]}...")
                    return i

        return 0  # 默认第一段

    def _find_recipient(self, paragraphs: List[Paragraph], title_idx: Optional[int]) -> Optional[int]:
        """查找主送机关段落"""
        if title_idx is None:
            return None

        # 从标题后开始查找
        start_idx = title_idx + 1
        for i in range(start_idx, min(start_idx + 5, len(paragraphs))):
            text = paragraphs[i].text.strip()
            if not text:
                continue

            # 包含主送机关特征
            for keyword in self.recipient_keywords:
                if text.startswith(keyword) or keyword in text[:10]:
                    logger.debug(f"识别到主送机关: 段落{i}")
                    return i

            # 以冒号结尾，可能是主送机关
            if text.endswith("：") or text.endswith(":"):
                logger.debug(f"识别到主送机关(冒号): 段落{i}")
                return i

        return None

    def _find_signature_and_date(self, paragraphs: List[Paragraph]) -> Tuple[Optional[int], Optional[int]]:
        """查找落款和日期段落"""
        signature_idx = None
        date_idx = None

        # 从文档末尾向前查找
        for i in range(len(paragraphs) - 1, max(0, len(paragraphs) - 10), -1):
            text = paragraphs[i].text.strip()
            if not text:
                continue

            # 查找日期
            if date_idx is None:
                for pattern in self.date_patterns:
                    if re.search(pattern, text):
                        date_idx = i
                        logger.debug(f"识别到日期: 段落{i}")
                        break

            # 查找落款（日期前一段）
            if signature_idx is None and date_idx is not None and i < date_idx:
                # 落款通常包含单位名称
                for keyword in self.signature_keywords:
                    if keyword in text:
                        signature_idx = i
                        logger.debug(f"识别到落款: 段落{i}")
                        break

                # 或者是日期前的最后一个非空段落
                if signature_idx is None:
                    signature_idx = i
                    logger.debug(f"识别到落款(默认): 段落{i}")
                    break

        return signature_idx, date_idx

    def _find_body_range(self, paragraphs: List[Paragraph],
                        recipient_idx: Optional[int],
                        signature_idx: Optional[int]) -> Tuple[Optional[int], Optional[int]]:
        """查找正文范围"""
        # 正文开始：主送机关后的第一个段落
        body_start = (recipient_idx + 1) if recipient_idx is not None else 1

        # 正文结束：落款前的最后一个段落
        body_end = (signature_idx - 1) if signature_idx is not None else len(paragraphs) - 3

        # 确保范围有效
        if body_start >= len(paragraphs):
            body_start = 1
        if body_end <= body_start:
            body_end = len(paragraphs) - 3

        logger.debug(f"正文范围: {body_start} - {body_end}")
        return body_start, body_end

    def _find_meeting_sections(self, paragraphs: List[Paragraph]) -> Dict[str, int]:
        """查找会议纪要的特殊部分"""
        sections = {}

        for i, para in enumerate(paragraphs):
            text = para.text.strip()
            if not text:
                continue

            # 检查每种会议要素
            for section_type, keywords in self.meeting_keywords.items():
                if section_type in sections:
                    continue  # 已找到，跳过

                for keyword in keywords:
                    if text.startswith(keyword) or keyword in text[:10]:
                        sections[section_type] = i
                        logger.debug(f"识别到会议{section_type}: 段落{i}")
                        break

        return sections

    def _determine_structure_type(self, paragraphs: List[Paragraph], result: Dict) -> str:
        """判断文档结构类型"""
        # 检查标题内容
        if result["title"] is not None:
            title_text = paragraphs[result["title"]].text

            if "会议" in title_text or "纪要" in title_text:
                return "meeting"
            elif "通知" in title_text:
                return "notice"
            elif "请示" in title_text:
                return "request"
            elif "报告" in title_text:
                return "report"
            elif "函" in title_text:
                return "letter"
            elif "决定" in title_text:
                return "decision"
            elif "通告" in title_text:
                return "announcement"
            elif "公告" in title_text:
                return "notice_public"

        # 检查会议纪要特征
        if len(result["special_sections"]) >= 3:
            return "meeting"

        return "notice"  # 默认为通知

    def generate_ai_prompt(self, model: DocumentModel, structure: Dict, rules: Dict) -> str:
        """
        生成AI分析提示词

        Args:
            model: 文档模型
            structure: 结构分析结果
            rules: 排版规则

        Returns:
            AI提示词
        """
        # 提取文档文本
        doc_text = "\n\n".join([p.text for p in model.paragraphs if p.text.strip()])

        # 构建结构提示
        structure_hints = []
        if structure["title"] is not None:
            structure_hints.append(f"- 段落{structure['title']}是标题")
        if structure["recipient"] is not None:
            structure_hints.append(f"- 段落{structure['recipient']}是主送机关")
        if structure["body_start"] is not None and structure["body_end"] is not None:
            structure_hints.append(f"- 段落{structure['body_start']}到{structure['body_end']}是正文")
        if structure["signature"] is not None:
            structure_hints.append(f"- 段落{structure['signature']}是落款")
        if structure["date"] is not None:
            structure_hints.append(f"- 段落{structure['date']}是日期")

        hints_text = "\n".join(structure_hints)

        prompt = f"""
你是一个专业的公文排版助手。请分析以下公文文档，并根据结构提示和排版规则进行智能排版。

文档内容：
{doc_text}

结构提示：
{hints_text}

文档类型：{structure['structure_type']}

排版规则：
{rules}

请识别文档中的每个部分，并应用相应的格式。返回JSON格式的排版指令：
{{
  "elements": [
    {{
      "paragraph_index": 0,
      "type": "标题",
      "format": {{...}}
    }},
    ...
  ]
}}
"""
        return prompt
