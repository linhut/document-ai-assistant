## v1.5.3 更新说明

> 发布日期：2026-09-03

### 本次版本包

| 包名 | 平台 | 说明 |
|------|------|------|
| `doc-optimizer-v1.5.3-win-x64.exe` | Windows x64 | NSIS 安装包 |
| `doc-optimizer-v1.5.3-win-arm64.exe` | Windows ARM64 | 信创 ARM 平台 |
| `doc-optimizer-v1.5.3-x86_64.AppImage` | Linux x64 | AppImage 格式 |
| `doc-optimizer-v1.5.3-amd64.deb` | Linux x64 | Debian/Ubuntu 安装包 |
| `doc-optimizer-v1.5.3-x64.dmg` | macOS x64 | Intel Mac |
| `doc-optimizer-v1.5.3-arm64.dmg` | macOS ARM64 | Apple Silicon Mac |
| `doc-optimizer-portable.zip` | Windows 通用 | 便携版（免安装） |
| `backend_server.exe` | Windows | 后端服务（独立运行） |
| `doc-optimizer-cli.exe` | Windows | CLI 命令行工具 |

### 🐛 修复：应用无法启动（1.5.2 回归）

> 1.5.2 版本安装后**无法正常打开应用**，本版本已修复。

- **根因**：`frontend/package.json` 误加 `"type": "module"`，导致 Electron 将 CommonJS 编译产物 `electron/dist/main.js` 按 ES Module 加载，主进程启动即报 `require is not defined`，表现为：应用无窗口、后端服务不启动、健康检查失败
- **修复**：移除 `"type": "module"`，恢复 Electron 标准加载方式；`eslint.config.js` 更名为 `eslint.config.mjs`（lint 配置仍为 ESM，功能不受影响）
- **验证**：打包产物冒烟测试通过——主进程正常、后端 `backend_server.exe` 拉起、`/api/health` 返回 `{"status":"ok","version":"1.5.3"}`、前端页面与全部 API 请求 200

### 🐛 修复：npm ci 依赖安装失败（ERESOLVE）

> 开发者 / CI 按源码执行 `npm ci` 时无法安装依赖，本版本已修复。

- **根因**：`eslint@10.x` 与 `eslint-plugin-react-hooks@5.2.0`（peer 最高支持 ESLint 9）冲突，报 `ERESOLVE could not resolve`
- **修复**：升级 `eslint-plugin-react-hooks` 至 **7.x**（peer 支持 ESLint 10），`npm ci` 恢复通过

### 🔧 改进

- 前端代码重构以满足 react-hooks 7.x 全部规则（immutability / set-state-in-effect / refs / static-components），不再关闭相关规则

### ✅ 测试与 CI

- `test_integration` 改用 `httpx`，消除未声明的 `requests` 测试依赖
- CI `backend-test` 补装 `pytest`
- 全量测试：**109 passed, 2 skipped**

### 🔧 其他

- 版本号统一升级至 **1.5.3**（backend / frontend / website / 安装器 / CHANGELOG）
