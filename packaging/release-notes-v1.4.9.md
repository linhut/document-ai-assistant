# Release Notes — v1.4.9

> 发布日期：2026-06-30

## 🎯 本次重点

### 包名统一为英文
所有分发包的文件名已统一为英文格式，不再包含中文字符：

| 包名 | 平台 | 说明 |
|------|------|------|
| `doc-optimizer-v1.4.9-win-x64.exe` | Windows x64 | NSIS 安装包 |
| `doc-optimizer-v1.4.9-win-arm64.exe` | Windows ARM64 | 信创 ARM 平台 |
| `doc-optimizer-v1.4.9-x86_64.AppImage` | Linux x64 | AppImage 格式 |
| `doc-optimizer-v1.4.9-amd64.deb` | Linux x64 | deb 安装包 |
| `doc-optimizer-v1.4.9-x64.dmg` | macOS x64 | DMG 安装包 |
| `doc-optimizer-v1.4.9-arm64.dmg` | macOS ARM64 | Apple Silicon |
| `doc-optimizer-v1.4.9-portable.zip` | 全平台 | 便携版（无需安装） |

### 仓库清理
- 移除 Git 跟踪中的非必要文件（旧阶段报告、工具脚本、测试辅助文件等 40+ 文件）
- 重命名中文目录 `公文模板/` → `dotx_templates/`
- 新增 `.gitignore` 规则，防止 Office 临时文件、构建产物、本地脚本被意外入库
- 新增 pre-commit 钩子，自动检测中文路径和禁止提交的文件类型
- 完善 `CONTRIBUTING.md` 提交规范

## ⚠️ 注意

本次发布为项目清理优化版本，功能与 v1.4.8 一致，仅包名和仓库结构优化。
