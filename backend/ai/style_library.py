# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.

"""
公文写作风格库（原创实现）。

按 22 个法定文种登记风格画像（结构要点 / 用语风格 / 注意事项），
并提供"去 AI 味"通用规则与提示词构建函数，供 AI 润色/重写/起草使用。

设计借鉴了自研 gongwen-skill 的"维度化、声明式画像"思路，
但全部内容与代码均为本项目原创编写。
"""

from __future__ import annotations

# ---------------------------------------------------------------
# 通用"去 AI 味"规则（应用于所有文种）
# 中文引号统一使用转义 \u201c \u201d，避免源码引号歧义
# ---------------------------------------------------------------
DEAI_RULES: list[str] = [
    '避免堆砌网络流行词与空泛新词（如：赋能、抓手、闭环、颗粒度、打通、落地生根、深度耦合等）',
    '少用\u201c首先、其次、再次、最后\u201d式的机械排比，改为按工作内在逻辑自然过渡',
    '不使用\u201c综上所述、总而言之、不难看出\u201d等明显凑字结尾语',
    '不写\u201c为深入贯彻……、为扎实推进……\u201d等套话开头，直接进入事项',
    '句子控制在中短句，一句一意；避免超长定语从句式表达',
    '数字、时间、地点、文号等事实要素不得改写或模糊化',
    '语气庄重、措辞准确，不用口语、不用感叹句、不用网络表情',
    '保持原文信息量：只优化表达，不增删实质内容，不虚构数据',
    '术语与专有名称保持一致，全文统一用词',
]

# 各文种提示词模式说明
MODE_DESC: dict[str, str] = {
    'deai': '去 AI 味润色：消除机械套话与空泛表达，使文本更贴近人写公文',
    'polish': '常规润色：修正语病、规范用语、理顺逻辑，保持原意',
    'concise': '精炼压缩：在不丢失要件（时间/地点/对象/措施）的前提下压缩篇幅',
    'formal': '规范升格：将非正式表述改写为规范公文用语',
}

# 文种中文名（与规则体系一致）
TYPE_NAMES: dict[str, str] = {
    'notice': '通知',
    'report': '报告',
    'request': '请示',
    'reply': '批复',
    'meeting': '会议纪要',
    'minutes': '会议记录',
    'decision': '决定',
    'resolution': '决议',
    'announcement': '公告',
    'bill': '通告',
    'bulletin': '公报',
    'communique': '公报',
    'command': '命令（令）',
    'instruction': '意见',
    'opinion': '意见',
    'regulation': '规定',
    'letter': '函',
    'summary': '总结',
    'work_plan': '工作计划',
    'technical_proposal': '技术方案',
    'table_sign': '表格签章',
    'notice_public': '公示',
}

# ---------------------------------------------------------------
# 22 文种风格画像
# 每个画像：structure(结构要点) / tone(用语风格) / caution(注意事项)
# ---------------------------------------------------------------
STYLE_PROFILES: dict[str, dict] = {
    'notice': {
        'name': '通知',
        'structure': ['标题：发文机关（可省）+事由+通知', '主送机关顶格', '正文：缘由+事项+要求三块', '落款：机关署名+成文日期'],
        'tone': '事项具体、要求明确，指令性话语适度，多用\u201c请、务必、现将、特此通知\u201d',
        'caution': '部署类通知要写明时间节点；转发类通知避免层层照转、要有本机关要求',
    },
    'report': {
        'name': '报告',
        'structure': ['标题：事由+报告', '正文：情况概述+主要做法/成效+存在问题+下一步打算', '结尾：\u201c特此报告\u201d'],
        'tone': '陈述为主、只汇报不请示，语气客观平实，用事实和数据说话',
        'caution': '报告中不得夹带请示事项；进展类报告要标注截至时间',
    },
    'request': {
        'name': '请示',
        'structure': ['标题：事由+请示', '正文：缘由（为何请示）+事项（请示什么）+结语', '结尾：\u201c妥否，请批示\u201d'],
        'tone': '一文一事，语气恳切规范，理由充分、目的明确',
        'caution': '必须一事一请示；结尾用语规范，不写\u201c请批准为盼\u201d等口语',
    },
    'reply': {
        'name': '批复',
        'structure': ['标题：发文机关+事由+批复', '正文：引述请示标题文号+批复意见', '结尾：\u201c此复\u201d'],
        'tone': '态度明确、用语肯定，\u201c同意/不同意/原则同意\u201d表述清晰，必要时说明理由',
        'caution': '只答复请示事项本身，不夹带其他事项；同意要有明确执行要求',
    },
    'meeting': {
        'name': '会议纪要',
        'structure': ['标题：会议名称+纪要', '会议基本信息（时间/地点/主持/出席）', '正文：议定事项分层表述', '落款：印发机关+日期'],
        'tone': '记实不记虚，忠实反映议定事项，语言凝练，多用\u201c会议指出、会议决定、会议要求\u201d',
        'caution': '别写成记录流水账；议定事项要有责任主体和时间要求',
    },
    'minutes': {
        'name': '会议记录',
        'structure': ['会议基本信息表头', '发言内容如实记录', '主持小结/决定事项'],
        'tone': '客观如实，直录要点，不加工不评价',
        'caution': '与纪要区分：记录重原始性，纪要重结论性',
    },
    'decision': {
        'name': '决定',
        'structure': ['标题：机关+事由+决定', '正文：依据/缘由+决定事项', '结尾：执行要求'],
        'tone': '庄重严肃、权威性强，条文式表述，语气果断',
        'caution': '涉及奖惩的决定要写明依据和具体条款',
    },
    'resolution': {
        'name': '决议',
        'structure': ['标题：会议名称+决议', '通过依据（某会议X年X月X日通过）', '正文决议事项'],
        'tone': '高度概括、原则性强，多为围绕重大事项的结论性表述',
        'caution': '须写明通过会议与时间；语言精当不展开论证',
    },
    'announcement': {
        'name': '公告',
        'structure': ['标题：机关+事由+公告', '正文：依据+事项+要求', '结尾：\u201c特此公告\u201d'],
        'tone': '面向社会公众，语言规范简明，庄重明白',
        'caution': '适用范围限定严格，只有法定机关可用；事项表述无歧义',
    },
    'bill': {
        'name': '通告',
        'structure': ['标题：事由+通告', '正文：缘由+具体事项+施行要求', '结尾：\u201c特此通告\u201d'],
        'tone': '面向一定范围，要求明确具体，语气平和而坚决',
        'caution': '写明有效期限与适用范围；禁止性事项表述清楚',
    },
    'bulletin': {
        'name': '公报',
        'structure': ['标题：机关+公报', '正文：会议/统计/外交等事项公报内容'],
        'tone': '庄重权威，叙述性文种，数据准确、事实清楚',
        'caution': '统计公报数字必须与原始数据一致，不四舍五入失实',
    },
    'communique': {
        'name': '公报',
        'structure': ['标题：机关+公报', '正文：事项内容'],
        'tone': '与 bulletin 类似，依使用习惯选择',
        'caution': '保持与 bulletin 同一机关口径一致',
    },
    'command': {
        'name': '命令（令）',
        'structure': ['标题：发文机关标志+令号', '正文：依据+命令事项', '落款：签发人职务+姓名+日期'],
        'tone': '权威简短，多为一句话命令，不加议论',
        'caution': '个人署名的命令须有签发人职务；依据须写明文号',
    },
    'instruction': {
        'name': '意见',
        'structure': ['标题：事由+意见', '正文：总体要求+主要任务+保障措施'],
        'tone': '指导性、说理性兼具，措施具体可操作，语气平实',
        'caution': '发对象要明确（下发的意见/报上级的意见行文方向不同）',
    },
    'opinion': {
        'name': '意见',
        'structure': ['标题：事由+意见', '正文：指导思想+重点任务+组织保障'],
        'tone': '同 instruction，突出指导性与针对性',
        'caution': '避免大而全，聚焦本地区本部门实际问题',
    },
    'regulation': {
        'name': '规定',
        'structure': ['标题：机关+规定', '第一章 总则：目的依据适用范围', '分章：具体条款', '末章 附则：施行日期解释权'],
        'tone': '条文式、条款化，用语严谨无歧义，可操作性第一',
        'caution': '条款之间不冲突；处罚/权利义务表述须有上位法依据',
    },
    'letter': {
        'name': '函',
        'structure': ['标题：事由+函', '主送机关：发文机关规范化称呼', '正文：缘由+事项+表态', '落款'],
        'tone': '平等协商语气，礼貌得体，\u201c请予函复\u201d\u201c致函商洽\u201d等规范用语',
        'caution': '商洽函与答复函区别对待；不写命令式口吻',
    },
    'summary': {
        'name': '总结',
        'structure': ['标题：单位+时限+总结', '正文：工作回顾+成效亮点+问题不足+经验体会+下步安排'],
        'tone': '实事求是，成绩不夸大、问题不回避，归纳提炼要具体',
        'caution': '避免流水账式罗列；数据与事实须真实',
    },
    'work_plan': {
        'name': '工作计划',
        'structure': ['标题：单位+时限+工作计划', '正文：目标要求+重点任务+进度安排+保障措施'],
        'tone': '目标量化、任务分解、责任到人，语言干脆',
        'caution': '目标要与上级要求衔接；措施要可考核',
    },
    'technical_proposal': {
        'name': '技术方案',
        'structure': ['标题：项目+技术方案', '正文：背景目标+技术路线+实施方案+进度+验收标准'],
        'tone': '专业严谨，术语规范，可读性与可验收性并重',
        'caution': '技术指标要明确可测；风险与应对要交代',
    },
    'table_sign': {
        'name': '表格签章',
        'structure': ['表格信息填写完整', '签章栏：机关署名+日期+盖章'],
        'tone': '简洁规范，文字与表格对应无误',
        'caution': '签章名称与印章一致；日期不涂改',
    },
    'notice_public': {
        'name': '公示',
        'structure': ['标题：事项+公示', '正文：基本情况+公示期限+意见反馈渠道', '落款机关+日期'],
        'tone': '客观中立，反馈渠道清晰，措辞审慎',
        'caution': '个人隐私信息要脱敏；公示期计算方式写明',
    },
}

# 通用兜底画像（未收录的文种使用）
_GENERIC_PROFILE: dict = {
    'name': '公文',
    'structure': ['标题规范', '正文分层清晰', '落款完整'],
    'tone': '庄重、准确、简明，符合党政机关公文表达规范',
    'caution': '格式遵守 GB/T 9704；要素齐全',
}


def list_style_profiles() -> list[dict]:
    """返回全部文种画像（文种键 + 名称）。"""
    return [{'document_type': k, 'name': v['name']} for k, v in STYLE_PROFILES.items()]


def get_profile(document_type: str) -> dict:
    """按文种取画像（未收录时回退通用画像）。"""
    return STYLE_PROFILES.get(document_type or '', _GENERIC_PROFILE)


def build_rewrite_instruction(document_type: str = 'notice', mode: str = 'deai') -> str:
    """构建系统指令（不含正文），供 provider.rewrite 作为 context 使用。"""
    profile = get_profile(document_type)
    mode_text = MODE_DESC.get(mode, MODE_DESC['deai'])
    lines = [
        '你是党政机关公文写作专家，擅长依据《党政机关公文处理工作条例》规范表达。',
        f'本次任务：{mode_text}。',
        f'文种：{profile["name"]}（{document_type}）。',
        f'结构要点：{"；".join(profile["structure"])}。',
        f'用语风格：{profile["tone"]}。',
        f'注意事项：{profile.get("caution", "")}。',
        '所有文种通用要求：',
    ]
    lines.extend(f'- {rule}' for rule in DEAI_RULES)
    lines.append('输出要求：只输出改写后的正文，不要解释、不要重复原文。')
    return '\n'.join(lines)


def build_rewrite_prompt(text: str, document_type: str = 'notice', mode: str = 'deai') -> str:
    """构建完整提示词（系统指令 + 原文），便于调试与测试。"""
    return build_rewrite_instruction(document_type, mode) + '\n\n待处理原文：\n' + text