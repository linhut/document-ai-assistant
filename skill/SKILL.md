---
name: gongwen-optimizer
description: 中文公文（党政机关公文 GB/T 9704-2012）格式检查、自动修复、模板生成、版头版记页码注入与 AI 风格优化工具。
---

# gongwen-optimizer（公文优化 Skill）

本项目为「AI 公文智能优化助手」的 Agent 可调用发行版。它把文档处理引擎打包成
可供 Claude Code / Codex / OpenCode / Kimi / Trae / ZCode 等 Agent 直接调用的 Skill：
克隆仓库即用，不依赖桌面端与数据库。

## 能力范围

| 能力 | 说明 | 调用方式 |
|---|---|---|
| 格式检查 | 按 GB/T 9704-2012 规则检查字体/字号/缩进/行距/页边距/页码等，输出问题清单（含标准条款 standard_ref） | `check` |
| 自动修复 | 一键修复格式问题并生成优化后的 .docx | `optimize` |
| 要素语义校验 | 文号、成文日期、发文机关署名等语义级检查（CHK-S 系列） | 随 `check` 输出 |
| 特殊版式 | 信函双线、命令格式、红头预印套打预留、联合行文 | 规则/模板层支持 |
| 模板生成 | 22 种法定文种模板（.dotx/.docx）生成 | 仓库 `templates/` 提供 |
| AI 风格优化 | 22 文种去 AI 味润色提示词库（`backend/ai/style_library.py`） | 配合 AI 调用 |

## 快速开始（命令行）

要求：Python 3.12+，安装依赖 `pip install -r backend/requirements.txt`。

```bash
# 从仓库根目录执行
python backend/wfp_cli.py check 输入.docx --doc-type notice
python backend/wfp_cli.py format 输入.docx --doc-type notice -o 输出.docx
python backend/wfp_cli.py optimize 输入.docx --doc-type notice -o 优化.docx --apply-fixes
```

常用参数：
- `--doc-type`：notice/report/request/meeting/decision/letter 等 22 种文种
- `--apply-fixes`：同时应用修复规则（默认关闭，仅检查）
- `--selected-rules`：只应用指定规则 ID（逗号分隔）

## 规则体系（证据链）

- 规则文件：`rules/official/*.yaml`（公共基础层 `_common.yaml` + 各文种层，三级优先级官方 < 自定义 < 用户）
- 每条检查规则关联 GB/T 9704-2012 条款（`standard_ref`），证据矩阵见 `docs/gbt9704-audit-matrix.md`
- 语义校验规则见 `backend/core/rules/semantic.py`

## 重要约定

1. 生成/修改文档必须通过 `backend/core/document/modifier.py`（单一变更点），勿直接改模型。
2. 中文字体必须走 `backend/core/document/font_utils.py` 的 `set_run_font()`（同时设置 ascii/hAnsi/eastAsia/cs 四属性）。
3. 标准字体：标题=方正小标宋简体、正文=仿宋_GB2312、西文=Times New Roman；目标机缺字体时生成器会警告。
4. 检查结果中的 `standard_ref` 为 GB/T 9704-2012 条款号，供审计与人工复核。

## 安装到各 Agent 平台

```bash
bash skill/scripts/install.sh --all          # macOS / Linux（符号链接，源目录只维护一份）
powershell -File skill/scripts/install.ps1 -All   # Windows（复制，避免符号链接权限问题）
```

支持的平台目录（随版本可能变化，可用环境变量 `SKILL_DIRS` 覆盖）：
Claude Code、Codex、OpenCode、Trae Code、Kimi Code、ZCode、TraeWork、WorkBuddy、Cursor。

## 许可

MIT。字体文件（方正小标宋简等）按其各自授权使用。
