# Changelog

所有重要的项目变更都将记录在此文件中。

---

## [1.4.6] - 2026-06-26

### 表格定位修复（端到端验证通过）

- **generator 表格定位** — `_add_table` 按 `insert_after_index` 用 XML 操作将表格插入到正确段落之后，不再追加到文档末尾
- **parser 表格位置检测** — 遍历 `doc.element.body` 计算每个表格在段落流中的精确位置
- **Table Grid 样式容错** — 文档无此预定义样式时手动添加 XML 边框

### 加粗范围修复（端到端验证通过）

- **fix_bold_range 执行顺序修复** — 移到 `FIX-C023 (set_bold heading3=true)` 之后执行，避免被覆盖
- **无冒号整段加粗** → 全部取消加粗
- **有冒号首句加粗** → 仅冒号前加粗，后续取消
- 效果：全加粗段落 17 → 0，预览与下载完全一致

### 预览 run 级别加粗渲染

- **后端 preview API** — 返回 `runs[]` 数组，每段每个 run 有独立 `bold` 状态
- **前端 A4PreviewModal** — 按 run 渲染 `<span>` 加粗，移除 heading_level=3 的整段强制加粗
- **预览与下载一致** — 首句加粗+后续不加粗在预览和下载中表现相同

### Parser 行距解析修复

- **EMU→pt 转换** — `EXACTLY` 模式下 `pf.line_spacing` 是 EMU 值（如 367665），需通过 `Length(x,0).pt` 转换为 pt（28.95）
- 数值 >100 时自动判定为 EMU 并转换

### 校审中心优化

- **同类型问题合并显示** — 按 `rule_id` 分组，如"正文应两端对齐 · 5 处"，可展开查看每一条

### 全面代码审查修复（20+ 项）

- templates.py: `save_extracted_template` 补充缺失的 `@router.post` 装饰器
- main.py: health 接口版本号改为动态读取 `app.version`
- ai.py: `save_ai_config` 不再吞掉 HTTPException
- settings.py: 172.16-31 网段判断 `len(parts)==2` → `==4`
- optimize.py: `preview-download` 添加 `BackgroundTask` 清理临时文件
- checker.py: 字体 None 漏检修复（3 处）
- modifier.py: `remove_extra_blank_lines` 后重新编号段落索引

---

## [1.4.5] - 2026-06-26

### 预览下载修复 + Markdown 表格端到端修复

- **预览下载重构** — 新增 `POST /api/optimize/preview-download` 端点，从前端预览数据（段落+表格）实时生成 docx
- **下载按钮修复** — EnhancedA4Preview 下载不再依赖 `/api/optimize/{id}/download`（需要先执行优化），直接从当前预览状态生成文件
- **表格完整保留** — 端到端验证：markdown 表格 `|方案|航线组合|...` → 4×6 表格完整写入 docx
- **页面设置传递** — 下载时将前端配置的页边距传递给生成器，确保 WYSIWYG

---

## [1.4.4] - 2026-06-26

### AI 模型可用性定时检测

- **后台健康检测** — 每 60 秒自动检测所有已配置 AI provider 的可用性
- **状态 API** — `GET /api/ai/status` 返回所有模型的在线状态和延迟
- **前端状态卡片** — AI 配置页面实时显示模型在线/离线状态和响应延迟
- **多 Provider 支持** — OpenAI 兼容接口 + Anthropic Claude 专用检测

### Markdown 表格转换修复

- **表格数据丢失修复** — `/convert-markdown` API 现在正确返回 `tables` 字段（之前只返回 `paragraphs`，表格数据丢失）
- **A4 预览表格渲染** — EnhancedA4Preview 支持渲染 markdown 转换生成的表格（带边框、表头加粗、单元格 padding）
- **后端表格序列化** — 完整序列化 Table/TableCell/Paragraph 到 API 响应

### 全量版权注释

- **所有代码文件** — Python (.py) 和 TypeScript (.tsx/.ts) 文件统一添加 MIT 版权注释头
- **标准化格式** — `(c) 2026 Jose AI (https://www.linhut.cn)`

### 构建流程规范化

- **完整发版流程** — 记录 6 步标准流程：版本号→README→提交→Release→打包→上传
- **README 功能描述** — 流程中明确包含新增功能的文档更新

---

## [1.4.3] - 2026-06-26

### A4 预览版头格式与国标对齐（参考 gongwen 项目数值）

- **发文机关标志字号** — 22pt → **30pt**（对齐 gongwen 项目的 DOCX 导出值）
- **发文机关标志颜色** — #CC0000 → **#E00000**（深红色，与 gongwen 一致）
- **发文机关标志字间距** — 3pt → **0**（对齐国标，无额外字距）
- **发文机关标志行高** — 新增 `line-height: 1.4`（CSS 预览与 gongwen 一致）
- **红色反线颜色** — #CC0000 → **#E00000**
- **红色反线上方间距** — 新增 `marginBottom: 4pt`（发文字号与反线间紧凑间距）
- **版头整体 marginBottom** — 1.5em → **空二行**（`lineSpacing × 2` pt，反线到标题的距离）

### A4PreviewModal 增强：自动检测版头版记

- **版头智能检测** — 通过红色文本（#CC0000/#E00000/#FF0000/#C00000）自动识别发文机关标志
- **发文字号检测** — 正则匹配 `X发〔YYYY〕N号` 标准格式
- **版头渲染** — 发文机关标志 30pt 红色居中 + 发文字号居中 + 红色反线
- **版记检测** — 通过 `role=cc` 自动识别抄送段落并渲染版记区域
- **版头版记数据扩展** — 后端 preview API 新增 `bold`、`color` 字段供前端检测

### 空行渲染优化

- **空段落紧凑渲染** — 空行 `line-height: 0.6` + `minHeight` 限制，避免连续空行撑开过多空白
- **A4PreviewModal 同步** — 空行处理逻辑与 EnhancedA4Preview 完全一致

### 字体映射统一

- **FONT_MAP 补全** — EnhancedA4Preview 新增 `方正小标宋_GBK`、`楷体`、`仿宋` 三个映射条目
- **A4PreviewModal FONT_MAP** — 新增 `Times New Roman` 映射，两个组件字体映射完全一致

### 页码格式修正（GB/T 9704）

- **页码字号** — 10pt → **14pt**（四号字，GB/T 9704 标准）
- **页码字体** — 新增宋体优先（`"宋体", "SimSun", "Times New Roman"`）

### 版记格式修正

- **抄送左空一字** — 新增 `paddingLeft: '1em'`（GB/T 9704 标准）
- **印发机关/日期缩进** — 左侧 `paddingLeft: '1em'`，右侧 `paddingRight: '1em'`

---

## [1.4.2] - 2026-06-26

### A4 实时排版预览（核心功能）

- **左右分栏布局** — 左侧格式设置面板 + 右侧 A4 实时预览，设置改动即时反映
- **格式设置面板** — 页边距/标题字体字号/正文字体字号行距缩进，全部可调
- **版头版记可视化配置** — 发文机关标志（红色方正小标宋）、发文字号、签发人（仿宋+楷体双字体）、抄送、印发机关/日期
- **版头排版标准** — 严格按 GB/T 9704-2012：标志下空二行、签发人居右空一字、签发人三字仿宋+姓名楷体
- **规则预览 Tab** — 当前所有格式参数一览
- **一键优化 Markdown** — 识别 # 标题、**加粗**、列表等语法并转为公文格式
- **DocumentConfig Context** — useReducer + localStorage 持久化，配置变更零延迟

### 格式规则引擎增强

- **convert_markdown 转换器** — 识别 12 种 markdown 语法并转为 Word 格式（标题级别、加粗、缩进、表格转 Table 对象）
- **markdown 表格转 Word 表格** — `|...|` 行自动转为真正的 Table/TableCell 对象
- **_common.yaml 规则补充** — 新增 6 条格式检查（标题加粗/主送机关/附件说明/抄送机关/页码字号）、1 条修复规则
- **所有 22 个文种 YAML 清理** — 内容规则标记 category:content，格式规则 category:format
- **技术方案继承冲突修复** — CHK-TP001(14pt) 覆盖 CHK-C005(16pt)

### 工作台增强

- **网页访问开关** — 快速操作新增一键开启/关闭局域网访问，默认开启
- **快速操作 4 卡片一排** — lg:grid-cols-4 响应式布局

### 模板中心增强

- **自定义模板显示** — 模板列表动态扫描 custom_rules/user_rules 目录
- **模板预览** — "查看详情"改为 A4 预览弹窗，展示模板排版效果
- **导入模板** — 从已排版文档自动提取格式规则
- **文档类型下拉搜索** — 支持中文名/英文标识双向匹配，动态加载

### 规则管理增强

- **用户规则显示** — 导入生成的规则归入"用户"分类
- **规则缓存失效** — PUT/DELETE/import 操作后自动清缓存

### 安全与稳定性

- **API Key 环境变量化** — 源码不再包含明文密钥
- **CORS 配置收紧** — allow_origins 改为 localhost 白名单
- **临时文件清理** — 上传完成后删除 TEMP_DIR 文件
- **错误消息不截断** — ValueError 和 AI raw_response 完整返回

---

## [1.4.1] - 2026-06-25

### 预览空白修复（P0）

- **A4PreviewModal 错误处理** — catch 块不再静默吞错，改为显示错误信息 + 重试按钮
- **空段落状态** — A4Preview 和 A4PreviewModal 均增加 paragraphs.length===0 判断，显示"暂无预览内容"
- **路径解析增强** — preview 和 download 端点增加 OUTPUT_DIR 文件名回退查找，兼容绝对路径失效场景

### 规则引擎按文档类型优化（P0）

- **22 个 YAML 规则文件清理** — 移除与 _common.yaml 重复的格式规则和 check/fix_rules，每个文件仅保留类型特有内容检查
- **manager.py 去重合并** — _deep_merge 改为按 field/target+action 去重，不再产生重复检查和修复
- **一级标题对齐修正** — heading_1 从 center 改为 left（GB/T 9704 要求左空二字）
- **补充 GB/T 9704 规则** — 新增页码格式检查（CHK-C023/C024）
- **文档类型自动检测** — upload_document 根据文件名关键词推断类型（通知/请示/报告等），不再全部默认 notice

### 安全修复（P0）

- **API Key 移除硬编码** — 默认密钥改为环境变量 DEFAULT_AI_API_KEY 注入，源码不再包含明文密钥
- **CORS 配置收紧** — allow_origins 从 "*" 改为 localhost 白名单，allow_credentials 改为 False
- **前端密钥移除** — AISettings 页面不再显示明文测试 KEY

### 后端修复（P1）

- **版本号统一** — FastAPI/health/office 版本统一为 1.4.0
- **规则缓存失效** — rules.py 的 PUT/DELETE/import 操作后自动清除引擎缓存
- **错误消息不截断** — ValueError 消息和 AI raw_response 不再截断
- **模板写入正确目录** — create_template 写入 USER_RULES_DIR 而非只读的 RULES_DIR
- **临时文件清理** — 上传完成后删除 TEMP_DIR 中的临时文件

---

## [1.0.5] - 2026-06-25

### AI 分析全面升级

- **AI prompt 按文种定制** — 22 种公文类型各有专属检查规则，会议纪要不再套用通知标准
- **AI 建议可选择应用** — AI issues 带 Checkbox 可多选，一键应用到文档生成优化版
- **AI issues 可视化重构** — 正确显示 type/location/original/suggestion/reason/severity
- **5 级 JSON 解析容错** — 解决 AI 返回 markdown 代码块/尾逗号/截断等常见问题
- **23+ AI 服务商支持** — 新增 MiniMax、腾讯混元、豆包、零一万物、商汤、天工、OpenRouter 等

### 规则引擎修复

- **22/22 文种 body 格式全覆盖** — 为 13 个缺失文件补充 body.font/size/indent/spacing 规则
- **Parser heading 误判修复** — Word 样式名 "6" 不再误判为 heading；Heading 3 无标题信号时降级为 body
- **首行缩进端到端修复** — 优化后文档所有正文段落均正确写入 2 字符缩进
- **删除语义错误规则** — meeting.yaml FIX-M002、command.yaml FIX-CM002
- **检查规则从 154 → 190 条，修复规则从 144 → 180 条**

### 后端修复

- **AI 分析 429 限流** — 重试 5 次 + 指数退避 2-32s + 随机抖动
- **API 空内容检测** — 返回空内容时自动重试而非静默失败
- **decrypt_value None 安全** — 加密字段为 NULL 时不再崩溃
- **Axios 超时** — 分析接口超时从 30s 提升到 120s

### 前端修复

- **AI 配置下拉框** — 用 label 做唯一标识，解决多个 custom 服务商同时选中的 bug
- **工作台 AI 状态** — 使用 detectActiveAI() 自动检测已启用的服务商，不再硬编码 deepseek
- **PyInstaller 控制台** — 生产版不再弹出黑色命令行窗口

---

## [1.4.0-rc2] - 2026-06-24

### P0 修复：数据目录架构重构 + 后端错误处理 + 前端导航修复

#### 数据目录架构（P0 核心修复）
- ♻️ **`config.py` 路径分层重构**
  - 新增 `APP_DATA_DIR`：可写运行时数据目录
  - `BASE_DIR` 仅用于只读资源（rules/official、templates/official、TTF）
  - 生产模式：`APP_DATA_DIR` 由 Electron 通过环境变量传入 → `%APPDATA%/AI公文助手`
  - 开发模式：`APP_DATA_DIR` = `BASE_DIR/data`（项目目录内）
  - 解决 Program Files 下写权限问题
- ♻️ **`electron/main.ts` 传递 `APP_DATA_DIR` 环境变量**
  - 生产模式 spawn 时设置 `APP_DATA_DIR = app.getPath('userData')`
  - 所有模式统一设置 `PYTHONIOENCODING=utf-8` 和 `PYTHONUNBUFFERED=1`
- ♻️ **`logger.py` 使用 `config.APP_DATA_DIR`**，消除重复的 `_get_base_dir()`
- ♻️ **`crypto.py` 使用 `config.APP_DATA_DIR`**，消除重复的 `_BASE` 路径解析
- ♻️ **`style_manager.py` 和 `manager.py`** 使用 config 统一路径导入
- ♻️ **`office.py`、`documents.py`、`templates.py`、`template_download.py`** 全部改用 config 路径

#### 后端错误处理
- 🐛 **`document_service.py` 全面加固**
  - `optimize_document()` 添加 try/except（parse_docx、RuleEngine、generate_docx、DB commit）
  - DB 操作添加 rollback 保护（check_document、optimize_document）
  - 添加 `_safe_filename()` 防止路径遍历攻击
  - 移除无用导入 `detect_inconsistencies`
- 🐛 **`modifier.py` 解析函数鲁棒性**
  - `_parse_mm_value`/`_parse_pt_value`/`_parse_indent_value` 添加 try/except，非数字输入返回 None
  - 所有 modifier 函数添加 None guard，防止静默数据损坏
- 🐛 **`fixer.py` None value 防护**
  - 缺少 `value` 字段的 fix rule 跳过并记录警告
  - `remove_*` 类动作不需要 value，不受影响
- 🐛 **`optimize.py` 错误码修正**
  - 解析失败返回 422 而非 404
  - 输出文件名使用 `_OPTIMIZED_SUFFIX` 常量消除 DRY 违规
- 🐛 **`documents.py` 文件名安全处理**
  - 上传文件名通过 `_safe_filename()` 清洗

#### 前端 API 修复
- 🐛 **`DocumentProcess.tsx` 导航修复**
  - `window.location.href` → `useNavigate()`（HashRouter 兼容）
- 🐛 **`CheckCenter.tsx` 查询参数修复**
  - `window.location.search` → `useSearchParams()`（HashRouter 兼容）
- ♻️ **`check.ts` 重写**
  - 4 个端点路径全部修正为匹配后端
  - 死代码变为可用模块
- ♻️ **`documents.ts` 重写**
  - `UploadResponse` 接口字段修正（`document_id` → `id`）
  - 移除不存在的 `downloadDocument` 端点
- 🐛 **`AISettings.tsx` 空 catch block 修复**
  - `loadDefaultConfig` 添加日志
  - `is_active` toggle 失败时回滚状态

---

## [1.4.0-rc1] - 2026-06-23

### RC1 修复：Electron桌面化 + API统一 + AI配置完善

#### Electron 桌面壳修复
- 🐛 **修复 `electron/main.ts` 路径问题**
  - preload 路径：`__dirname/preload.js`（编译后正确）
  - 后端脚本路径：开发模式 vs 生产模式分别处理
  - 添加日志写入 `userData/logs/electron.log`
  - 后端启动失败时弹窗提示（不再静默失败）
  - 健康检查超时增加重试对话框
- 🐛 **修复 `package.json` 构建脚本**
  - 新增 `electron:build:preview`（--publish=never 防止误发布）
  - 新增 `electron:compile`（单独编译 TS）

#### API 路径统一化
- 🐛 **消除前端所有硬编码 `http://127.0.0.1:8765`**
  - `api/client.ts`：统一封装，支持 Electron/开发/生产三种模式
  - 新增 `downloadFile()` 辅助函数
  - `CheckCenter.tsx`：下载改用 `downloadFile()`
  - `Templates.tsx`：3处下载改用 `downloadFile()`
  - `handlers/downloadTemplate.ts`：改用 `downloadFile()`

#### AI 配置完善
- ✨ **新增 Claude Provider**（前端 + 后端）
- ✨ **新增 Ollama Provider**（前端 + 后端）
- ✨ **获取模型按钮**：调用 `/api/ai/models` 获取可用模型列表
- ✨ **默认内置配置**：`https://cpa.linhut.cn/v1`
- ✨ **API Key 脱敏显示**：`sk-xxxx****xxxx`

#### 公文字体下载
- ✨ **字体下载 API**：`GET /api/settings/fonts` + `GET /api/settings/fonts/download/{filename}`
- ✨ **关于页面字体下载区**：显示方正小标宋简体/仿宋_GB2312/楷体_GB2312，一键下载+安装说明

#### 版本号统一
- 🎨 `Sidebar.tsx`：v1.1.0 → v1.4.0
- 🎨 `main.py`：API version 0.1.0 → v1.4.0
- 🎨 `About.tsx`：版本号 0.9.0 → v1.4.0-rc1

### 文档
- 📝 **`docs/RC1_EXECUTION_PLAN.md`**：RC1 执行计划
- 📝 **`docs/BUILD_PREVIEW.md`**：Preview EXE 构建指南
- 📝 **`docs/RC_FINAL_AUDIT_REPORT.md`**：RC 最终审计报告
- 📝 **`docs/WPS插件开发规划.md`**：重写与当前架构对齐

---

## [1.4.0] - 2026-06-23

### 新增：文档质量自动验证器
- ✨ **`backend/core/document/validator.py`**
  - 四维度验证：字体/样式/段落格式/页面设置
  - 输出结构化报告 `{font_errors, style_errors, layout_errors, page_errors, fallback_fonts}`
  - 检测 MS Gothic/Mincho 等无效替代字体
  - 验证 docDefaults/Normal 样式存在
- ✨ **API 端点** `POST /api/documents/{id}/validate`
- ✨ **`docs/QA_DOCUMENT_TEST_PLAN.md`**
  - 22 个自动化测试用例
  - 5 个维度（Font/Style/Layout/Page/Generation）
  - 验收标准：字体异常 = 0

### 新增：AI Provider 多模型升级
- ✨ **Claude Provider** (`ai/providers/claude_provider.py`)
  - Anthropic Messages API
  - 默认模型：claude-sonnet-4-20250514
- ✨ **Ollama Provider** (`ai/providers/ollama_provider.py`)
  - 本地模型支持
  - 默认：qwen2.5:7b
- ✨ **模型列表获取** `POST /api/ai/models`
  - 调用 /models 端点获取可用模型
- ✨ **默认内置 AI 配置**
  - 自动回退到内置聚合服务
  - API Key 加密存储 + 前端脱敏显示
- ✨ **错误分类系统**
  - auth / permission / endpoint / timeout / network / config
  - 禁止统一显示"处理失败"
- ✨ **`docs/AI_PROVIDER_DESIGN.md`**

### 改进
- 🎨 **`available_providers()` 返回结构化信息**（含默认 Base URL / 模型）
- 🎨 **AI API 增强**
  - `GET /api/ai/providers` 返回 Provider 列表 + 默认配置
  - `GET /api/ai/config/{provider}` 返回脱敏 API Key
  - `GET /api/ai/default` 返回默认配置

---

## [1.3.0] - 2026-06-23

### 新增：样式模板中心
- ✨ **8 个官方样式模板 YAML**
  - `templates/official/`：notice/request/report/letter/meeting/decision/announcement/notice_public
  - 每个模板包含 page/styles/sample 三部分
  - 字体定义：eastAsia + latin 分离，符合 GB/T 9704-2012
- ✨ **`core/template/style_manager.py`**
  - 三层模板管理（user > custom > official）
  - CRUD + 导入/导出
  - `get_style_for_type()` / `get_page_setup()` 查询接口
- ✨ **`core/template/generator.py`**
  - `generate_docx_template()`：从 YAML 生成 .docx 模板
  - `generate_dotx_template()`：生成可安装的 .dotx 模板
  - 样式写入 Word 样式库（非内联格式）
- ✨ **样式模板 API**
  - `GET /api/templates/styles/list`：列出样式模板
  - `GET /api/templates/styles/{id}`：获取模板详情
  - `GET /api/templates/styles/{id}/download/docx`：下载 .docx
  - `GET /api/templates/styles/{id}/download/dotx`：下载 .dotx
  - `POST /api/templates/styles/import`：导入模板

### 新增：Office 插件 Bridge
- ✨ **`office-plugin/bridge/local_api.py`**
  - `check_document_from_file()` / `check_document_from_bytes()`
  - `optimize_document_from_file()` / `optimize_document_from_bytes()`
  - `get_template_list()` / `download_template_docx()` / `download_template_dotx()`
  - `health_check()`
- ✨ 设计文档 `docs/OFFICE_PLUGIN_DESIGN.md` 更新

### 改进
- 🎨 **前端模板中心**：新增「样式.docx」和「安装.dotx」下载按钮
- 🎨 **PROJECT_STATUS.md**：更新至 v1.3.0，总体完成度 93%

---

## [1.2.0] - 2026-06-23

### UI 自适应优化
- 🎨 **侧边栏响应式**
  - 宽屏展开（w-60），窄屏折叠（w-16）
  - 移动端（<768px）自动折叠 + overlay
  - 汉堡菜单按钮
  - 版本号更新至 v1.1.0
- 🎨 **主布局自适应**
  - `AppLayout` 支持 sidebar toggle
  - `min-w-0` 防止主内容溢出
- 🎨 **页面响应式**
  - Workspace：`grid-cols-1/sm:2/lg:3` 自适应
  - CheckCenter：筛选器小屏堆叠
  - DocumentProcess：响应式 padding
  - Templates：筛选按钮 wrap
  - Rules：Tab 栏小屏堆叠
  - PageHeader：标题/操作小屏纵排

### Electron 桌面壳完善
- ✨ `electron/main.ts` 完善
  - `minWidth: 1024, minHeight: 768`
  - 外部链接默认浏览器打开
  - 后端健康检查等待（15s 超时）
  - Windows `python` 命令适配

### 测试体系完善
- ✅ **新增 68 个测试用例，全部通过**
  - `tests/rules/test_rule_manager.py`（17 个）
    - 三层规则合并验证
    - 用户规则覆盖官方规则
    - CRUD 操作
    - 导入/导出
    - 规则验证
  - `tests/rules/test_modifier.py`（18 个）
    - 字体/字号/对齐/行距/缩进/页边距修改
    - 空格清理/空行清理
    - 文本替换
    - 不可变性验证
  - `tests/backend/test_ai_error_handling.py`（11 个）
    - Provider 初始化
    - 自定义重试配置
    - Provider 接口一致性
    - 错误处理
  - `tests/document/test_document_quality.py`（22 个）
    - 模板生成/字体XML/格式规则/优化对比
  - `tests/conftest.py` 统一 Python path 配置

### 修复
- 🐛 **修复 `test_font_validation_detects_issues` 中 `get_or_create_rPr` → `get_or_add_rPr`**
- 🐛 **修复 `PageHeader` 小屏标题截断问题**

---

## [1.1.0] - 2026-06-23

### P0 修复：中文字体异常
- 🐛 **修复 MS Gothic/MS Mincho 替代字体问题**
  - 根因：`run.font.name` 不写入 `w:eastAsia`，Word 使用默认东亚字体
  - `font_utils.py` 重构：`set_run_font()` 同时写入 ascii/hAnsi/eastAsia/cs
  - `generator.py` 所有 run 走 `set_run_font()` 统一入口
  - `parser.py` 使用 `get_effective_font()` 优先读取 eastAsia
  - 生成后 `validate_document_fonts()` 自动检测 MS Gothic
  - 8 个字体 XML 测试用例

### 架构改进
- ♻️ **Fixer 架构统一**
  - 新增 `core/document/modifier.py`：所有文档修改的唯一入口
  - `core/rules/fixer.py` 简化为 YAML 规则解释层
  - 消除双 fixer 重复逻辑
- ♻️ **三层规则系统完善**
  - `config.py` 新增 `CUSTOM_RULES_DIR`、`USER_RULES_DIR`
  - `manager.py` 实现 user > custom > official 三层 deep merge
  - `RuleEngine` 使用 `load_rules_merged` 替代 `load_rules_for_type`
  - 规则修改真正影响生成流程

### 新增
- ✨ **Electron 桌面壳**
  - `frontend/electron/main.ts` 主进程
  - `frontend/electron/preload.ts` 预加载脚本
  - 自动启动/停止 Python 后端
  - 健康检查等待后端就绪
  - `package.json` electron-builder 配置
- ✨ **AI Provider 稳定性**
  - 指数退避重试（1s→2s→4s，最多 3 次）
  - 区分可重试（429/500/502/503）和不可重试（401/403/404）错误
  - 详细中文错误信息（认证失败/访问被拒绝/超时等）
  - 60 秒请求超时 + 10 秒连接超时
- ✨ **文档质量测试体系**（`tests/document/test_document_quality.py`）
  - 模板生成测试（内容/页边距/纸张）
  - 字体 XML 测试（eastAsia/MS Gothic 排除/拉丁字体）
  - 格式规则测试（action 兼容性/规则加载）
  - 优化前后对比测试（内容保留/字体改进）

### 改进
- 🎨 **模板下载三层规则支持**
  - `template_download.py` 使用 `load_rules_merged` 替代 `load_rules_for_type`
  - 用户自定义规则影响模板生成
- 🎨 **`manager.py` 验证增强**
  - `validate_rule()` 检查 check_rules/fix_rules 结构
  - fix_rules 必须包含 action 字段
  - check_rules 必须包含 id 和 severity

---

## [0.9.0] - 2026-06-23

### 新增
- ✨ **规则编辑独立页面**
  - 新建 TemplateRules.tsx 页面
  - 完整的规则编辑功能
  - 路由：/templates/:id/rules
- ✨ **字段下拉选择器**
  - 17个字段分组显示
  - 带 Emoji 图标
  - 应用于模板新增和规则编辑

### 改进
- 🎨 **用户体验全面优化**
  - 12+ 处交互优化
  - 5+ 处视觉增强
  - 8+ 处提示文字优化
  - 表单验证完善
- 🎨 **模板中心优化**
  - 添加分类筛选（全部/政府/国企）
  - 卡片 hover 效果增强
  - 操作按钮更突出
- 🎨 **工作台优化**
  - 添加 /workspace 路由
  - 首页跳转正常
  - 快速操作卡片可点击

### 修复
- 🐛 **修复编辑规则跳转问题**
- 🐛 **修复工作台首页访问问题**
- 🐛 **修复规则配置字段输入不便问题**

---

## [0.8.0] - 2026-06-23

### 新增
- ✨ **新增 4 个公文模板**
  - opinion.yaml - 意见模板
  - reply.yaml - 批复模板
  - minutes.yaml - 纪要模板
  - instruction.yaml - 指示模板
- ✨ **新增模板创建功能**
  - POST /api/templates/create API
  - 前端新增模板对话框
  - 自动生成基础规则结构
- ✨ **添加下载优化文档功能**
  - CheckCenter 添加下载按钮
  - 优化状态自动检测
  - 应用修复后自动显示下载按钮

### 修复
- 🐛 **修复 Templates 和 Rules 数据显示**
  - 修复路由注册问题
  - 后端已加载 templates 和 rules 路由
- 🐛 **修复所有 API 响应访问问题**
  - 涉及 5 个前端页面
  - 统一修复 response.data.xxx 访问

### 改进
- 🎨 **UI 布局优化**（已在 v0.6.1 完成）
  - 所有页面响应式布局
  - 适配多种屏幕尺寸

### 完成
- ✅ **Phase 6 - Rule Refinement 完成**
- ✅ **所有核心功能 100% 完成**
- ✅ **项目达到生产就绪状态**

---

## [0.6.1] - 2026-06-23

### 修复
- 🐛 **关键修复**：修复所有页面的 API 响应访问问题
  - 修复 DocumentProcess.tsx 中的 `response.data.id` → `response.id`
  - 修复 CheckCenter.tsx 中的响应数据访问
  - 修复 AISettings.tsx 中的响应数据访问
  - 修复 Templates.tsx 中的响应数据访问
  - 修复 Rules.tsx 中的响应数据访问
  - 问题：API 拦截器已返回 `response.data`，但代码仍访问 `response.data.xxx`
  - 影响：文档处理功能"处理失败，请重试"

### 改进
- 🎨 优化所有页面的布局宽度
  - CheckCenter: max-w-7xl → max-w-[1600px]
  - Templates: max-w-7xl → max-w-[1600px]
  - Rules: max-w-7xl → max-w-[1600px]
  - DocumentProcess: max-w-3xl → max-w-4xl
  - AISettings: max-w-3xl → max-w-4xl
  - 改进响应式布局，适配 1366×768、1920×1080、2K 屏幕

### 测试
- ✅ 完整端到端测试通过
- ✅ 所有 API 端点验证通过
- ✅ AI 功能验证通过
- ✅ 性能测试通过（< 0.8s 总处理时间）

---

## [0.6.0] - 2026-06-23

### 新增
- ✨ AISettings 真实功能 - 连接后端 API，保存配置，测试连接
- ✨ Templates 前端页面 - 连接真实 API，显示 8 种模板
- ✨ Rules 前端页面 - 连接真实 API，显示所有规则
- ✨ Templates 后端 API - GET /api/templates/list, GET /api/templates/{id}
- ✨ Rules 后端 API - GET /api/rules/list, GET /api/rules/{id}
- ✨ AI 后端 API - POST /api/ai/config, GET /api/ai/config/{provider}, POST /api/ai/test
- ✨ 加密存储工具 - utils/crypto.py 使用 Fernet 加密 API Key

### 改进
- 🎨 优化界面宽度 - 所有页面自适应布局
- 🎨 优化 AISettings 用户体验 - 错误提示、成功提示、加载状态
- 📝 完善 notice.yaml 规则 - 增加到 7 条检查规则

### 修复
- 🐛 修复 CheckCenter 使用 Mock 数据的问题
- 🐛 修复 DocumentProcess 上传功能
- 🐛 修复应用按钮不工作的问题

---

## [0.5.0] - 2026-06-22

### 新增
- ✨ Phase 5 - AI Integration 完成
- ✨ AI Provider 架构 - 支持 OpenAI、DeepSeek、Custom
- ✨ AI 配置数据库表 - AIConfig
- ✨ AI API 测试功能

---

## [0.4.0] - 2026-06-21

### 新增
- ✨ Phase 4 - Rule Engine 完成
- ✨ Rule Checker - 执行 YAML 检查规则
- ✨ Rule Fixer - 应用自动修复
- ✨ CheckCenter 真实功能
- ✨ 完整流程验证 - 100% 修复成功率

### 改进
- 📝 8 种公文模板 YAML 规则

---

## [0.3.0] - 2026-06-20

### 新增
- ✨ Phase 3 - Document Engine 完成
- ✨ Document Parser - 解析 .docx 为 DocumentModel
- ✨ Document Generator - 从 DocumentModel 生成 .docx
- ✨ DocumentModel - 完整的 Pydantic 数据模型
- ✨ 单元测试 - 所有测试通过

---

## [0.2.0] - 2026-06-19

### 新增
- ✨ Phase 2 - 桌面 UI 完成
- ✨ 7 个完整页面
- ✨ 温暖大地色系设计
- ✨ 所有 UI 组件

---

## [0.1.0] - 2026-06-18

### 新增
- ✨ Phase 1 - 架构设计完成
- ✨ 项目架构设计报告
- ✨ 技术选型
- ✨ 目录结构设计
- ✨ 开发路线规划

---

## 类型说明

- ✨ 新增 (Added)
- 🎨 改进 (Changed)
- 🗑️ 废弃 (Deprecated)
- 🐛 修复 (Fixed)
- 🔒 安全 (Security)
