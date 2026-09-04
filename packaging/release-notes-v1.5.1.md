<!--
  (c) 2026 Jose AI (https://www.linhut.cn)
  https://github.com/linhut/document-ai-assistant
  Licensed under the MIT License. See the LICENSE file for details.
-->

## v1.5.1 更新说明

> 发布日期：2026-08-06

### 本次版本包

| 包名 | 平台 | 说明 |
|------|------|------|
| `doc-optimizer-v1.5.1-win-x64.exe` | Windows x64 | NSIS 安装包 |
| `doc-optimizer-v1.5.1-win-arm64.exe` | Windows ARM64 | 信创 ARM 平台 |
| `doc-optimizer-v1.5.1-x86_64.AppImage` | Linux x64 | AppImage 格式 |
| `doc-optimizer-v1.5.1-amd64.deb` | Linux x64 | Debian/Ubuntu 安装包 |
| `doc-optimizer-v1.5.1-x64.dmg` | macOS x64 | Intel Mac |
| `doc-optimizer-v1.5.1-arm64.dmg` | macOS ARM64 | Apple Silicon Mac |
| `doc-optimizer-portable.zip` | Windows 通用 | 便携版（免安装） |
| `backend_server.exe` | Windows | 后端服务（独立运行） |
| `doc-optimizer-cli.exe` | Windows | CLI 命令行工具 |

### 🐛 修复：AI 语义优化启用失败

- **AI 配置启用失效根因修复** — 前端以 `custom:<服务名>`（如 `custom:aliyun_qwen`）作为 DB 键保存配置，后端 `create_provider()` 注册表只认 `custom` 等类型名，导致 AI 语义分析 / AI 润色 / 结构分析在调用时抛 `Unknown AI provider` 而静默失败。现统一在 `ai/manager.py` 归一化 `custom:*` → `custom`，一处修复所有调用点
- **AI 结构分析修复** — 此前仅匹配 `provider="openai"` 的启用配置，用户启用 DeepSeek / custom 等其他服务商时结构分析永远被跳过；改为优先使用当前启用的 AI 配置
- **测试连接 / 获取模型修复** — 使用已保存密钥时按 `custom` 查询不到 `custom:*` 记录，现支持前缀宽松匹配（优先已启用配置）

### 🎯 项目介绍优化

- **gongwen-skill 曝光提升** — 独立发行版介绍由 README 底部「社区与友链」前置到项目介绍顶部醒目位置
- **官网首页 Banner** — 新增 gongwen-skill 高亮曝光条，直达 GitHub 仓库

### ✅ 测试

- 修复 9 个遗留测试缺陷（过时断言、动作支持集合与实际 `_ACTION_MAP` 脱节、缺失 pytest-asyncio 的异步标记、真实 API 测试硬编码密钥等）
- 全量测试：**100 passed, 2 skipped**（真实 API / E2E 测试在无外部服务时自动跳过）

### 📦 其他

- 版本号统一升级至 **1.5.1**（backend / frontend / website / 安装器 / CHANGELOG）
