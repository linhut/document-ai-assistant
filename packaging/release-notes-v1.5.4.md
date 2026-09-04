## v1.5.4 更新说明

> 发布日期：2026-09-04

### 本次版本包

| 包名 | 平台 | 说明 |
|------|------|------|
| `doc-optimizer-v1.5.4-win-x64.exe` | Windows x64 | NSIS 安装包 |
| `doc-optimizer-v1.5.4-win-arm64.exe` | Windows ARM64 | 信创 ARM 平台 |
| `doc-optimizer-v1.5.4-x86_64.AppImage` | Linux x64 | AppImage 格式 |
| `doc-optimizer-v1.5.4-amd64.deb` | Linux x64 | Debian/Ubuntu 安装包 |
| `doc-optimizer-v1.5.4-x64.dmg` | macOS x64 | Intel Mac |
| `doc-optimizer-v1.5.4-arm64.dmg` | macOS ARM64 | Apple Silicon Mac |
| `doc-optimizer-portable.zip` | Windows 通用 | 便携版（免安装） |
| `backend_server.exe` | Windows | 后端服务（独立运行） |
| `doc-optimizer-cli.exe` | Windows | CLI 命令行工具 |

### ✨ 新增：AI 模型一键删除

- AI 设置页「模型可用性监控」卡片中，每个已添加的 AI 模型行新增**删除按钮**（垃圾桶图标）
- 点击后二次确认（提示将同时删除已保存的 API Key），确认后调用后端删除接口，模型立即从监控列表移除
- 删除当前选中的服务商时同步重置表单（清空 API Key 状态、AI 开关）；删除任意模型后全局同步侧边栏/工作台 AI 状态

### 🐛 修复：`/api/settings/rule-types` 返回 500

- **根因**：`RuleEngine.available_types()` 为实例方法，`settings.py` 中却按类方法调用，触发 `missing 1 required positional argument: 'self'`
- **修复**：将 `available_types()` 改为 `@staticmethod`，类方法与实例调用均可用，并补充回归测试防止复发
- **验证**：修复后接口返回全部 22 种公文类型（200 OK）

### 🐛 修复：Electron 主进程 ESLint 错误

- `frontend/electron/main.ts` 中 3 处 ESLint 错误（`require()` 导入、2 处空 catch 块）已修复，`npm run lint` 全量通过（0 错误）

### ✅ 测试与验证

- 后端全量测试：**110 passed, 1 skipped**
- 前端生产构建（`tsc -b && vite build`）通过
- 全部只读 API 冒烟测试通过；文档核心链路（上传→检查→优化→下载）、Markdown 转换、模板预览、AI 配置管理均实测正常

### 📌 AI 服务说明

- 应用 AI 功能链路（配置管理、健康检测、连接重试、错误分类）经实测正常
- 当前已配置的两个外部 AI 服务商存在外部不可用情况：elysiver 中转站 `/chat/completions` 返回 **503**（服务商侧故障）、小米 token-plan API Key **401 失效**。建议在「AI 设置」页更新 API Key 或更换服务商后再使用 AI 分析/润色功能
