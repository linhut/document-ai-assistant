# v1.6.0 更新说明

## 本次版本包

| 包名 | 平台 | 说明 |
|------|------|------|
| `doc-optimizer-v1.6.0-win-x64.exe` | Windows x64 | NSIS 安装包 |
| `doc-optimizer-v1.6.0-win-arm64.exe` | Windows ARM64 | 信创 ARM 平台 |
| `doc-optimizer-v1.6.0-linux-x86_64.AppImage` | Linux x64 | AppImage 便携运行 |
| `doc-optimizer-v1.6.0-linux-x86_64.deb` | Linux x64 | Debian 系安装包 |
| `doc-optimizer-v1.6.0-mac-x64.dmg` | macOS x64 | DMG 安装包 |
| `doc-optimizer-v1.6.0-mac-arm64.dmg` | macOS ARM64 | Apple Silicon |
| `doc-optimizer-v1.6.0-portable.zip` | Windows | 免安装便携版 |
| `doc-optimizer-cli-v1.6.0` | 全平台 | 命令行版 |

## 功能更新

- **标准证据链**：检查结果携带 GB/T 9704-2012 条款号（standard_ref），自动生成 22 文种规则证据矩阵
- **要素语义校验**：文号、成文日期、发文机关署名语义级检查（CHK-S 系列）
- **特殊版式**：信函红色双线、命令式间距、红头预印套打预留、联合行文机关标志
- **公文写作风格库**：22 文种画像 + 去 AI 味规则，新增 /api/ai/rewrite，Markdown 优化页一键"去 AI 味"
- **暗标合规检查**：身份证/手机号/邮箱/银行卡脱敏扫描，校审中心一键触发
- **标准包机制**：官方 < 标准包 < 自定义 < 用户 四层规则，设置页可切换
- **PDF 双输出**：LibreOffice/docx2pdf 最佳努力转换，校审中心一键导出
- **格式清洗**：全角空格/连续空格/空行清理并入优化流程，优化响应返回清洗报告
- **保持版式编辑**：AI 修改内容时 run 级保留原有格式
- **视觉回归**：黄金样本 + 感知哈希，CI 自动比对
- **SKILL 发行版**：skill/ 目录 + 双平台安装脚本，可安装到 9 个 AI Agent 平台
- **前端体验**：zustand 全局状态、条款列展示、暗标扫描面板、标准包下拉、导出 PDF

## 质量

- 后端全量测试 187 passed / 3 skipped；前端 build + ESLint 通过
- 可用性测试 14/14 通过（scripts/usability_test.py 可复跑）
- 代码级跨平台检查通过（Linux/macOS 实机复验项见 docs/platform-compat-check.md）
