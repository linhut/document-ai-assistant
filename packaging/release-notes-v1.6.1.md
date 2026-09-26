# v1.6.1 更新说明

## 本次版本包

| 包名 | 平台 | 说明 |
|------|------|------|
| `doc-optimizer-v1.6.1-win-x64.exe` | Windows x64 | NSIS 安装包 |
| `doc-optimizer-v1.6.1-win-arm64.exe` | Windows ARM64 | 信创 ARM 平台 |
| `doc-optimizer-v1.6.1-linux-x86_64.AppImage` | Linux x64 | AppImage 便携运行 |
| `doc-optimizer-v1.6.1-linux-x86_64.deb` | Linux x64 | Debian 系安装包 |
| `doc-optimizer-v1.6.1-mac-x64.dmg` | macOS x64 | DMG 安装包 |
| `doc-optimizer-v1.6.1-mac-arm64.dmg` | macOS ARM64 | Apple Silicon |
| `doc-optimizer-v1.6.1-portable.zip` | Windows | 免安装便携版 |
| `doc-optimizer-cli-v1.6.1` | 全平台 | 命令行版（新增版头/版记/页码注入） |

## 功能更新

- **CLI 版头注入**：`optimize` 子命令支持 `--header-config/--footer-config/--page-number-config`（JSON 文件）与 `--org-name/--doc-number/--signer` 便捷参数，命令行产出与桌面端行为一致
- **前端分包提速**：主 chunk 588KB → 195KB（-67%），react/ui/vendor 独立缓存，信创纯 Web 模式首屏加载更快
- **AI 配置引导**：Markdown 优化页 AI 润色/去 AI 味失败时，配置类错误（401/403/未配置）直接提供「去 AI 设置」跳转

## 架构与兼容性

- **依赖方向修正**：版头/版记/页码注入下沉至 `core/document/layout_injector.py`，消除 service→route 反向依赖，CLI/插件可复用核心版式能力
- **数据库迁移框架**：`PRAGMA user_version` + `_MIGRATIONS` 版本化迁移，旧库自动补列、幂等可重放
- **Python 3.14 兼容**：修复 `asyncio.get_event_loop()` 弃用告警（统一协程执行器，兼容 FastAPI/同步/CLI 三环境）
- **Pillow 14 兼容**：`get_flattened_data` 兼容分支，视觉回归脚本未来版本安全
- **CLI 逻辑修复**：`--apply-fixes` 改为 `--no-apply-fixes` 可关闭（原默认值无法关闭）

## 质量

- 后端全量测试 **187 passed / 3 skipped**；前端 ESLint 零告警、`tsc -b && vite build` 通过
- CLI 端到端验证通过（注入版头后文档可重解析）；数据库迁移三项场景（新库/重入/旧库补列）验证通过
- 多平台兼容：win32 依赖全部平台守卫 + 降级路径，Linux/macOS/信创路径解析与打包脚本维持既有支持
