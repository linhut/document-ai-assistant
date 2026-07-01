## v1.5.0 更新说明

### 本次版本包

| 包名 | 平台 | 说明 |
|------|------|------|
| `doc-optimizer-v1.5.0-win-x64.exe` | Windows x64 | NSIS 安装包 |
| `doc-optimizer-v1.5.0-win-arm64.exe` | Windows ARM64 | 信创 ARM 平台 |
| `doc-optimizer-v1.5.0-x86_64.AppImage` | Linux x64 | AppImage 格式 |
| `doc-optimizer-v1.5.0-amd64.deb` | Linux x64 | Debian/Ubuntu 安装包 |
| `doc-optimizer-v1.5.0-x64.dmg` | macOS x64 | Intel Mac |
| `doc-optimizer-v1.5.0-arm64.dmg` | macOS ARM64 | Apple Silicon Mac |
| `doc-optimizer-portable.zip` | Windows 通用 | 便携版（免安装） |
| `backend_server.exe` | Windows | 后端服务（独立运行） |
| `doc-optimizer-cli.exe` | Windows | CLI 命令行工具 |

### 版记（末页）—— 完全符合 GB/T 9704-2012

- **分隔线**：上下两条 0.35mm 黑色实线，与版心等宽
- **抄送机关**：左空一字 + 悬挂缩进（回行与冒号后首字对齐），3号仿宋（16pt）
- **印发机关与印发日期**：同一行，左空一字 + 右空一字，左右两端对齐
- **版记换页逻辑**：末页剩余空间不足 30mm 时自动分页

### 页码

- **字体**：4号半角宋体阿拉伯数字（14pt）
- **格式**：一字线 — {PAGE} —，数字与一字线之间保留半字空格
- **奇偶页不同**：奇数页（右页）居右空一字，偶数页（左页）居左空一字
- **位置**：页码顶端距版心下边缘 7mm
- **单面打印**：支持居中模式

### 版头

- **发文机关标志**：方正小标宋简体 30pt 红色
- **发文字号+签发人**：同行左右两端对齐（发文号左、签发人右），16pt 仿宋

### 模板规则

- **模板规则保存功能**：支持前端编辑并保存检查规则
- **规则保存 API**：PUT /api/templates/{template_id}/rules

### SQLite 优化

- 启用 WAL 模式，提升并发读写性能
- 连接池配置（pool_size=5, max_overflow=10）
- SQLITE_BUSY 自动重试（指数退避）

### 其他改进

- 数据库定期备份机制
- 文件锁机制（多文档并发处理）
- 认证 Token 自动获取（前端启动时自动同步）
- 页码奇偶页设置（前端传参归一化 + settings.xml 文档级开关）
- CI 流程：添加 ruff（Python 代码检查）和 ESLint（前端代码检查）
- Release 流程：body_path 自动降级（文件不存在时生成默认说明）
- 表格定位修复：preview-download 保留 insert_after_index
- 解析/生成快照测试
- 关于页面：GitHub 版本检测提醒
