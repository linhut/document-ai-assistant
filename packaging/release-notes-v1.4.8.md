# Release Notes — v1.4.8

> 发布日期：2026-06-30

## 🎯 本次重点

### 编排功能全面修复
- 修复版头/版记不应用到下载文档的问题（`optimize_document` 路径无注入逻辑）
- 修复版头段落顺序错误（机关名→空行→字号→签发人→红线）
- 修复 RED_LINE / __BLACK_LINE__ 占位符文字出现在文档中
- 修复表格位置丢失（新增 `source_doc_id` 传递源文档结构）
- 修复下载按钮闭包捕获旧配置值（`config` → `configRef.current`）
- 修复缓存数据丢失（三重缓存：模块级Map + sessionStorage + localStorage）

### GB/T 9704 标准合规增强
- 修正标题行距：28.95pt → 33pt（标题/一级/二级/三级标题）
- 添加页脚距离：2.5cm（GB/T 9704 标准）
- 新增 8 条检查规则 + 8 条修复规则（标题行距、标题缩进、落款字体）
- 检查规则从 31 条提升至 39 条，修复规则从 25 条提升至 33 条

### 格式增强
- 表格智能对齐：表头居中加粗、数字右对齐、序号列居中、短文本居中
- 内联标题分割：标题+正文同段落时自动拆分
- 附件分页标记：附件前自动插入分页符
- 空行处理三模式：keep_all / delete_single / keep_single
- CLI 接口：支持 `format` / `check` / `optimize` 子命令

### 安全加固
- 添加 Bearer Token 认证中间件
- 修复路径遍历漏洞（office.py / manager.py / style_manager.py）
- 修复错误信息泄露内部路径（所有路由文件）
- 修复加密密钥文件权限（0600）
- 修复 datetime.utcnow() 废弃警告
- 修复文件上传竞态条件（UUID 前缀）

### 前端优化
- 启用 TypeScript strict 模式
- 修复 9 个页面的 AbortController 缺失
- 修复 A4PageRenderer useMemo 失效
- 修复 apiClient 类型安全（移除 `as any`）
- 修复 setTimeout 泄漏（DocumentProcess / ImportTemplate）
- 修复 Map 无限增长（MarkdownOptimize）
- 添加 Electron sandbox 模式
- 日志 RotatingFileHandler（10MB, 5 备份）

### 后端资源管理
- AI Provider 添加 async context manager（`__aenter__`/`__aexit__`）
- Office Bridge 临时文件清理（BackgroundTask）
- 规则引擎缓存失效机制
- 模型健康检测非阻塞（asyncio.to_thread）

## 📦 本次版本包

| 包名 | 平台 | 说明 |
|------|------|------|
| `doc-optimizer-v1.4.8-win-x64.exe` | Windows x64 | NSIS 安装包 |
| `doc-optimizer-v1.4.8-win-arm64.exe` | Windows ARM64 | 信创 ARM 平台 |
| `doc-optimizer-v1.4.8-linux-x64.AppImage` | Linux x64 | AppImage 格式 |
| `doc-optimizer-v1.4.8-mac-x64.dmg` | macOS x64 | DMG 安装包 |
| `doc-optimizer-v1.4.8-mac-arm64.dmg` | macOS ARM64 | Apple Silicon |
| `doc-optimizer-v1.4.8-portable.zip` | 全平台 | 便携版（无需安装） |

## 🔧 技术变更

### 后端变更文件（26个）
- main.py, auth.py, optimize.py, ai.py, check.py, documents.py, office.py, templates.py
- settings.py, template_download.py, api_models.py, ai_structure_analyzer.py
- converter.py, generator.py, modifier.py, structure_analyzer.py
- checker.py, engine.py, fixer.py, manager.py, style_manager.py
- models.py, document_service.py, model_health.py, crypto.py, logger.py
- 新增: wfp_cli.py

### 前端变更文件（24个）
- A4PageRenderer.tsx, client.ts, main.tsx, A4Preview.tsx, AISettings.tsx
- CheckCenter.tsx, DocumentProcess.tsx, EnhancedA4Preview.tsx
- ImportTemplate.tsx, Rules.tsx, TemplateRules.tsx, Templates.tsx
- Workspace.tsx, tsconfig.app.json, ai-status.ts, useDocumentConfig.tsx
- download.ts, electron/main.ts, RightPanel.tsx, Sidebar.tsx
- App.tsx, MarkdownOptimize.tsx, main.tsx

### 规则变更（1个）
- rules/official/_common.yaml（+119 行）

## 📊 统计

- 测试通过率：88/98（90%），10 个失败均为预存问题
- TypeScript 编译：零错误
- Vite 构建：1.13 秒
- 代码变更：52 个文件，+2694 行，-1293 行

## ⚠️ 已知限制

- AI 集成测试需要配置 API Key 才能运行
- Electron 打包需要 PyInstaller 环境
- 信创平台（银河麒麟/统信）需要预装 LibreOffice 用于 .doc/.wps 转换
