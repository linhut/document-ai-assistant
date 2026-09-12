# GB/T 9704-2012 标准证据矩阵

> 本矩阵由 `scripts/gen_audit_matrix.py` 依据规则 YAML 自动生成，将每条检查/修复规则关联到《党政机关公文格式》GB/T 9704-2012 对应条款，作为规则体系的标准依据证据链。

**统计口径说明**：规则条数为「公共基础层 + 文种层」合并去重后的生效条数。

## announcement（公告）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-A001 | P1 | 标题加粗检查 | 7.2.4 | title.bold | True |
| CHK-A002 | P1 | 通告范围检查 | — | content.scope | 明确适用范围 |
| CHK-A003 | P1 | 通告生效日期检查 | — | content.effective_date | 包含施行日期 |
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-A001 | set_bold | doc_title | CHK-A001 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## bill（通告）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-BL001 | P1 | 议案案由检查 | — | content.reason | 案由明确 |
| CHK-BL002 | P1 | 提案人检查 | — | content.proposer | 注明提案人 |
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## bulletin（公报）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-BT001 | P1 | 通报事实检查 | — | content.facts | 事实清楚 |
| CHK-BT002 | P2 | 通报目的检查 | — | content.purpose | 明确通报目的 |
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## command（命令（令））

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-CM001 | P1 | 标题加粗检查 | 7.2.4 | title.bold | True |
| CHK-CM002 | P0 | 令号检查 | — | header.doc_number | 包含令号 |
| CHK-CM003 | P1 | 签发人检查 | 7.3.5 | signature.signer | 行政首长签署 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-CM001 | set_bold | doc_title | CHK-CM001 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## communique（公报）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-CG001 | P1 | 公报事项检查 | — | content.items | 事项完整 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## decision（决定）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-D001 | P1 | 标题加粗检查 | 7.2.4 | title.bold | True |
| CHK-D002 | P1 | 决定依据检查 | — | content.legal_basis | 包含法规依据 |
| CHK-D003 | P1 | 决定事项检查 | — | content.decision_items | 决定事项明确 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-D001 | set_bold | doc_title | CHK-D001 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## instruction（意见）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-I001 | P1 | 指示依据检查 | — | content.basis | 明确指示依据 |
| CHK-I002 | P1 | 指示措施检查 | — | content.measures | 措施具体可行 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## letter（函）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-L001 | P1 | 称谓检查 | — | salutation.check | 使用规范机关称谓 |
| CHK-L002 | P1 | 结束语检查 | — | ending.check | 包含规范结束语 |
| CHK-L003 | P2 | 语言规范检查 | — | language.formal | 语言规范得体 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## meeting（会议纪要）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-M001 | P1 | 会议要素检查 | — | content.meeting_elements | 要素齐全 |
| CHK-M002 | P1 | 议定事项检查 | — | content.decisions | 议定事项明确 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## minutes（minutes）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-MN001 | P1 | 会议信息检查 | — | content.meeting_info | 包含时间地点参会人 |
| CHK-MN002 | P1 | 议定事项检查 | — | content.decisions | 议定事项明确 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## notice（通知）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-N001 | P2 | 通知结语检查 | — | ending.check | 包含规范结语 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## notice_public（公示）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-NP001 | P1 | 标题加粗检查 | 7.2.4 | title.bold | True |
| CHK-NP002 | P1 | 公告范围检查 | — | content.scope | 明确公告范围 |
| CHK-NP003 | P2 | 公告时效检查 | — | content.validity | 明确有效期限 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-NP001 | set_bold | doc_title | CHK-NP001 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## opinion（意见）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-O001 | P1 | 意见措施检查 | — | content.suggestions | 意见措施具体 |
| CHK-O002 | P2 | 意见适用范围检查 | — | content.scope | 明确适用范围 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## regulation（规定）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-REG001 | P1 | 制度条款检查 | — | content.clauses | 条款明确 |
| CHK-REG002 | P1 | 制度施行日期检查 | — | content.effective_date | 包含施行日期 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## reply（批复）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-RP001 | P0 | 批复对象检查 | — | content.reply_to | 引述请示标题 |
| CHK-RP002 | P2 | 批复结语检查 | — | ending.check | 包含规范结语 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## report（报告）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-RPT001 | P2 | 报告结语检查 | — | ending.check | 包含规范结语 |
| CHK-RPT002 | P1 | 报告事项检查 | — | content.report_items | 报告内容完整 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## request（请示）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-R001 | P0 | 请示结语检查 | — | ending.check | 使用"妥否，请批示"等 |
| CHK-R002 | P1 | 一文一事检查 | — | content.single_topic | 一文一事 |
| CHK-R003 | P1 | 主送机关检查 | — | header.recipient | 主送一个上级机关 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## resolution（决议）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-RS001 | P1 | 决议事项检查 | — | content.resolution_items | 决议事项明确 |
| CHK-RS002 | P1 | 决议程序检查 | — | content.procedure | 注明会议名称和日期 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## summary（总结）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-SUM001 | P1 | 总结结构检查 | — | content.structure | 结构完整 |
| CHK-SUM002 | P2 | 总结数据检查 | — | content.data | 有具体数据支撑 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## table_sign（表格签章）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-TS001 | P0 | 桌签字号检查 | 7.2.4 | title.size | 50pt |
| CHK-TS002 | P0 | 桌签加粗检查 | 7.2.4 | title.bold | True |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-TS001 | set_size | doc_title | — | 7.2.4 |
| FIX-TS003 | set_alignment | doc_title | — | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-TS002 | set_bold | doc_title | — | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## technical_proposal（技术方案）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-TP001 | P0 | 正文字号检查（技术方案） | 7.3.3 | body.size | 14pt |
| CHK-TP002 | P1 | 技术背景检查 | — | content.background | 包含技术背景 |
| CHK-TP003 | P1 | 方案对比检查 | — | content.alternatives | 有方案对比 |
| CHK-TP004 | P1 | 实施计划检查 | — | content.implementation_plan | 有实施计划 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-TP001 | set_size | body | CHK-TP001 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

## work_plan（工作计划）

### 检查规则

| 规则 ID | 严重级 | 名称 | 标准条款 | 字段 | 期望值 |
|---|---|---|---|---|---|
| CHK-C001 | P0 | 上边距检查 | 6.1 | page_setup.margins.top | 3.7cm |
| CHK-C002 | P0 | 左边距检查 | 6.1 | page_setup.margins.left | 2.8cm |
| CHK-C003 | P0 | 右边距检查 | 6.1 | page_setup.margins.right | 2.6cm |
| CHK-C004 | P0 | 正文字体检查 | 7.3.3 | body.font | 仿宋_GB2312 |
| CHK-C005 | P0 | 正文字号检查 | 7.3.3 | body.size | 16pt |
| CHK-C006 | P1 | 正文行距检查 | 7.3.3 | body.line_spacing | 28.95pt |
| CHK-C007 | P0 | 公文大标题字体检查 | 7.2.4 | title.font | 方正小标宋简体 |
| CHK-C008 | P0 | 公文大标题字号检查 | 7.2.4 | title.size | 22pt |
| CHK-C009 | P0 | 一级标题字体检查 | 6.2 | heading_1.font | 黑体 |
| CHK-C010 | P0 | 二级标题字体检查 | 6.2 | heading_2.font | 楷体_GB2312 |
| CHK-C011 | P0 | 下边距检查 | 6.1 | page_setup.margins.bottom | 3.5cm |
| CHK-C012 | P1 | 正文首行缩进检查 | 7.3.3 | body.first_line_indent | 2em |
| CHK-C013 | P1 | 正文对齐方式检查 | 7.3.3 | body.align | justify |
| CHK-C014 | P0 | 一级标题字号检查 | 6.2 | heading_1.size | 16pt |
| CHK-C015 | P0 | 二级标题字号检查 | 6.2 | heading_2.size | 16pt |
| CHK-C016 | P1 | 落款右空四字检查 | 7.3.5 | signature.align | right |
| CHK-C017 | P1 | 日期右空四字检查 | 7.3.6 | date.align | right |
| CHK-C018 | P0 | 纸张大小检查 | 6.1 | page_setup.paper_width_mm | 210 |
| CHK-C019 | P0 | 三级标题字体检查 | 6.2 | heading_3.font | 仿宋_GB2312 |
| CHK-C020 | P0 | 三级标题字号检查 | 6.2 | heading_3.size | 16pt |
| CHK-C021 | P0 | 公文大标题居中检查 | 7.2.4 | title.align | center |
| CHK-C022 | P1 | 一级标题左空二字检查 | 6.2 | heading_1.first_line_indent | 2em |
| CHK-C023 | P1 | 页码格式检查 | 7.4.2 | page_number.font | 宋体 |
| CHK-C024 | P1 | 页码位置检查 | 7.4.2 | page_number.alignment | center |
| CHK-C025 | P1 | 公文标题不加粗检查 | 7.2.4 | title.bold | False |
| CHK-C026 | P1 | 主送机关格式检查 | 7.2.5 | recipient.font | 仿宋_GB2312 |
| CHK-C027 | P2 | 附件说明格式检查 | 7.3.4 | attachment.first_line_indent | 2em |
| CHK-C028 | P2 | 抄送机关格式检查 | 7.4.1 | cc.font | 仿宋_GB2312 |
| CHK-C029 | P1 | 页码字号检查 | 7.4.2 | page_number.size | 14pt |
| CHK-C030 | P2 | 正文加粗范围检查 | 7.3.3 | body.bold_range | True |
| CHK-C032 | P1 | 一级标题行距检查 | 6.2 | heading_1.line_spacing | 28.95pt |
| CHK-C033 | P1 | 公文大标题行距检查 | 7.2.4 | title.line_spacing | 28.95pt |
| CHK-C035 | P1 | 二级标题行距检查 | 6.2 | heading_2.line_spacing | 28.95pt |
| CHK-C036 | P1 | 二级标题左空二字检查 | 6.2 | heading_2.first_line_indent | 2em |
| CHK-C037 | P1 | 三级标题行距检查 | 6.2 | heading_3.line_spacing | 28.95pt |
| CHK-C038 | P1 | 三级标题左空二字检查 | 6.2 | heading_3.first_line_indent | 2em |
| CHK-C039 | P1 | 落款字体检查 | 7.3.5 | signature.font | 仿宋_GB2312 |
| CHK-C040 | P1 | 日期字体检查 | 7.3.6 | date.font | 仿宋_GB2312 |
| CHK-WP001 | P1 | 目标任务检查 | — | content.objectives | 目标明确 |
| CHK-WP002 | P1 | 时间节点检查 | — | content.timeline | 有时间节点 |

### 修复规则

| 规则 ID | 动作 | 目标 | 关联检查 | 标准条款 |
|---|---|---|---|---|
| FIX-C030 | convert_markdown | all | — | — |
| FIX-C004 | remove_extra_spaces | all | — | — |
| FIX-C001 | set_font | body | CHK-C004 | 7.3.3 |
| FIX-C002 | set_size | body | CHK-C005 | 7.3.3 |
| FIX-C009 | set_first_line_indent | body | CHK-C012 | 7.3.3 |
| FIX-C010 | set_alignment | body | CHK-C013 | 7.3.3 |
| FIX-C015 | set_line_spacing | body | CHK-C006 | 7.3.3 |
| FIX-C003 | set_page_margins | page_setup | — | — |
| FIX-C016 | set_font | doc_title | CHK-C007 | 7.2.4 |
| FIX-C017 | set_size | doc_title | CHK-C008 | 7.2.4 |
| FIX-C018 | set_alignment | doc_title | CHK-C021 | 7.2.4 |
| FIX-C037 | set_line_spacing | doc_title | CHK-C033 | 7.2.4 |
| FIX-C006 | set_font | heading_1 | CHK-C009 | 6.2 |
| FIX-C011 | set_size | heading_1 | CHK-C014 | 6.2 |
| FIX-C021 | set_first_line_indent | heading_1 | CHK-C022 | 6.2 |
| FIX-C032 | set_line_spacing | heading_1 | CHK-C032 | 6.2 |
| FIX-C007 | set_font | heading_2 | CHK-C010 | 6.2 |
| FIX-C012 | set_size | heading_2 | CHK-C015 | 6.2 |
| FIX-C033 | set_line_spacing | heading_2 | CHK-C035 | 6.2 |
| FIX-C034 | set_first_line_indent | heading_2 | CHK-C036 | 6.2 |
| FIX-C008 | set_font | heading_3 | CHK-C019 | 6.2 |
| FIX-C022 | set_size | heading_3 | CHK-C020 | 6.2 |
| FIX-C023 | set_bold | heading_3 | — | — |
| FIX-C035 | set_line_spacing | heading_3 | CHK-C037 | 6.2 |
| FIX-C036 | set_first_line_indent | heading_3 | CHK-C038 | 6.2 |
| FIX-C031 | fix_bold_range | body | — | 7.3.3 |
| FIX-C013 | set_alignment | signature | CHK-C016 | 7.3.5 |
| FIX-C038 | set_font | signature | CHK-C039 | 7.3.5 |
| FIX-C039 | set_font | date | CHK-C040 | 7.3.6 |
| FIX-C024 | set_bold | doc_title | CHK-C025 | 7.2.4 |
| FIX-C005 | remove_extra_blank_lines | all | — | — |
| FIX-C019 | normalize_punctuation | all | — | — |
| FIX-C020 | normalize_headings | all | — | — |
| FIX-C025 | set_page_number | page_footer | CHK-C023 | 7.4.2 |

---
## 规则统计汇总

| 文种 | 检查规则 | 修复规则 |
|---|---|---|
| announcement（公告） | 40 | 34 |
| bill（通告） | 40 | 34 |
| bulletin（公报） | 40 | 34 |
| command（命令（令）） | 40 | 34 |
| communique（公报） | 39 | 34 |
| decision（决定） | 40 | 34 |
| instruction（意见） | 40 | 34 |
| letter（函） | 41 | 34 |
| meeting（会议纪要） | 40 | 34 |
| minutes（） | 40 | 34 |
| notice（通知） | 39 | 34 |
| notice_public（公示） | 40 | 34 |
| opinion（意见） | 40 | 34 |
| regulation（规定） | 40 | 34 |
| reply（批复） | 40 | 34 |
| report（报告） | 40 | 34 |
| request（请示） | 41 | 34 |
| resolution（决议） | 40 | 34 |
| summary（总结） | 40 | 34 |
| table_sign（表格签章） | 38 | 34 |
| technical_proposal（技术方案） | 41 | 34 |
| work_plan（工作计划） | 40 | 34 |

合计：22 个文种，合并前规则条目检查 879 条。实际生效数 = 公共基础层（_common.yaml）与该文种层合并后的并集。
