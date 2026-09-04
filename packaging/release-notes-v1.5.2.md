<!--
  (c) 2026 Jose AI (https://www.linhut.cn)
  https://github.com/linhut/document-ai-assistant
  Licensed under the MIT License. See the LICENSE file for details.
-->

## v1.5.2 更新说明

> 发布日期：2026-08-19

### 本次版本包

| 包名 | 平台 | 说明 |
|------|------|------|
| `doc-optimizer-v1.5.2-win-x64.exe` | Windows x64 | NSIS 安装包 |
| `doc-optimizer-v1.5.2-win-arm64.exe` | Windows ARM64 | 信创 ARM 平台 |
| `doc-optimizer-v1.5.2-x86_64.AppImage` | Linux x64 | AppImage 格式 |
| `doc-optimizer-v1.5.2-amd64.deb` | Linux x64 | Debian/Ubuntu 安装包 |
| `doc-optimizer-v1.5.2-x64.dmg` | macOS x64 | Intel Mac |
| `doc-optimizer-v1.5.2-arm64.dmg` | macOS ARM64 | Apple Silicon Mac |
| `doc-optimizer-portable.zip` | Windows 通用 | 便携版（免安装） |
| `backend_server.exe` | Windows | 后端服务（独立运行） |
| `doc-optimizer-cli.exe` | Windows | CLI 命令行工具 |

### ✨ 新增

- **AI 配置删除** — AI 配置页面新增「删除配置」按钮：
  - 彻底删除已添加的服务商配置（含加密存储的 API Key）
  - 删除前二次确认，防止误操作
  - 删除启用中的配置后，AI 服务自动回到未启用状态
  - 同步清理模型健康检测缓存，状态列表不再残留已删除的服务商

### 🔧 其他

- 版本号统一升级至 **1.5.2**（backend / frontend / website / 安装器 / CHANGELOG）
