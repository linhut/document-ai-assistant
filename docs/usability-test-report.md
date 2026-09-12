# 可用性测试报告（API 全流程实测 + 页面体验评估 + 多平台运行评估）

> 测试日期：2026-09-12 | 环境：Windows（Git Bash / Python 3.14.5 / docx 1.2.0）
> 方法：`python scripts/usability_test.py`（纯标准库，可重复运行）＋ 代码走查 ＋ 本会话早前基准数据

## 一、API 全流程实测结果（14/14 通过）

| # | 步骤 | 结果 | 关键指标 |
|---|---|---|---|
| 1 | 后端启动 / 健康检查 | ✅ | boot 6.2s 内就绪；/api/health 16ms |
| 2 | 上传文档（27KB 会议记录） | ✅ | 0.25s，返回 doc_id |
| 3 | 格式检查 | ✅ | 160 issues（P0=25），0.37s |
| 4 | 检查结果含 standard_ref（证据链） | ✅ | 规则已携带 GB/T 9704 条款号 |
| 5 | 暗标合规检查 | ✅ | 毫秒级返回 issues 列表（命中片段脱敏） |
| 6 | 标准包列表 / 切换 / 停用 | ✅ | enterprise 包可用，切换即失效规则缓存 |
| 7 | AI 润色（无可用 Key） | ✅ | 优雅降级：返回错误消息，不崩溃 |
| 8 | 风格润色端点契约 | ✅ | 0.07s 返回 |
| 9 | PDF 导出（无转换器） | ✅ | 返回安装指引（LibreOffice/docx2pdf） |
| 10 | 优化全流程（清洗+修复+生成） | ✅ | 159 项修复；**cleaning 报告**随响应返回 |
| 11 | 优化输出可重解析 | ✅ | 84 段落结构完好 |
| 12 | A4 预览数据 | ✅ | 84 段落，0.23–1.36s |

**流程闭环**：上传 → 检查 → 查看（含标准条款）→ 优化 → 下载/预览 全部打通；
鉴权（Bearer Token）与健康检查豁免行为正常。

## 二、运行效率评估（结合本会话基准实测）

| 环节 | 实测 | 结论 |
|---|---|---|
| 27KB 文档全链路（解析+检查+生成） | 0.49s | 优秀 |
| 8.5MB 大文档全链路 | 0.83s | 优秀（规则检查毫秒级） |
| 规则检查（含语义校验） | 0.002–0.37s | 优秀 |
| 优化接口（清洗+159 修复+生成） | 0.40s | 优秀 |
| 后端启动 → 健康就绪 | < 6.5s（含依赖加载） | 可接受 |
| 前端产物 | JS 584KB / CSS 50KB（gzip 179KB） | 轻量；vite 提示 >500KB 可考虑分包（非阻塞） |

**结论**：核心链路无性能瓶颈；无需为性能重构。

## 三、使用体验评估（页面/流程维度）

### 3.1 本轮新能力的体验状态
| 能力 | 后端 | 前端展示 | 建议 |
|---|---|---|---|
| standard_ref 证据链 | ✅ 随检查结果返回 | 未展示 | 校审中心可加"标准条款"列（下一迭代） |
| 要素语义校验 CHK-S | ✅ 随检查返回 | 未区分 | 同上一并展示 |
| 清洗报告 cleaning | ✅ 随优化响应返回 | 未展示 | 优化完成提示可附"已清理 N 项" |
| 暗标合规 dark-bid | ✅ 端点就绪 | 未挂入口 | 校审中心加"暗标扫描"按钮 |
| AI 风格润色 /rewrite | ✅ 端点就绪 | 未挂入口 | Markdown 优化页可接入"去 AI 味" |
| 标准包切换 | ✅ 端点就绪 | 未挂入口 | 设置页可加下拉 |
| PDF 导出 | ✅ 端点就绪 | 未挂入口 | 下载区加"导出 PDF"（需装 LibreOffice） |
| 特殊版式（letter/formal/command） | ✅ 生成器支持 | 未暴露 | 模板生成页可选版式档案 |

### 3.2 既有体验问题（Known Gaps 复核）
- 工作台已为真实 API 数据（✅ 已修复，CLAUDE.md 已更新）
- TemplateRules 保存仍未实现（维持）
- API 调用模式已部分统一（✅ 本轮 Sidebar/Workspace/RightPanel 迁移 zustand 全局状态）
- 导航：已无 window.location.href 页面跳转（仅 error-boundary 的 HashRouter 兼容写法保留）

### 3.3 交互评分
- 主流程（上传→检查→优化→下载）顺畅度：4.5/5
- 反馈完整性（错误消息可读、降级提示明确）：4/5
- 新能力可发现性（前端入口未全挂）：3/5（下一迭代补齐）

## 四、多平台运行可用性检查

### 4.1 静态检查（已完成）
- 本轮新增/修改代码全部使用 `pathlib` 与标准库，无 `os.system`、无 `win32`/`WindowsError` 硬编码（已扫描确认）
- 双平台脚本齐备：`skill/scripts/install.sh`（macOS/Linux）+ `install.ps1`（Windows）
- 跨平台工具函数：`services/pdf_export.find_libreoffice` 覆盖 Windows 常见安装路径与 PATH；渲染链路 PIL/PyMuPDF 跨平台

### 4.2 平台矩阵
| 功能 | Windows（已实测） | Linux / macOS（静态评估） | 注意事项 |
|---|---|---|---|
| 核心引擎（解析/检查/修复/生成） | ✅ | ✅ | 纯 Python + OXML，无平台依赖 |
| 特殊版式（OXML 双线/预留） | ✅ | ✅ | Word/WPS 兼容性由字体四属性保证 |
| PDF 导出 | 指引降级 | 需 `apt install libreoffice-writer`（CI 已配置） | LIBREOFFICE_PATH 可覆盖 |
| 视觉回归 | 生成+哈希 ✅ | 渲染需 LO + PyMuPDF | workflow 设 continue-on-error |
| SKILL 安装 | install.ps1 | install.sh（符号链接） | 平台目录路径随版本变化，SKILL_DIRS 可覆盖 |
| 打包模式 | PyInstaller exe ✅ | AppImage/deb | config.py 已处理 sys.frozen 路径 |
| 字体 | TTF 随包 | 同左 | 缺字体时生成器警告/拒绝替代 |

### 4.3 未在本机验证项（如实说明）
- macOS 实际启动、Linux 实际渲染比对、PyInstaller 打包产物在 Windows 之外的运行——需在对应环境执行 `npm run electron:build:linux*` 与 `pytest tests/` 复验。

## 五、发现的问题与建议

| 级别 | 问题 | 建议 |
|---|---|---|
| P1 | 调试过程遗留的 8766 端口孤儿进程（本会话早期 bash 超时遗留） | 随仓库瘦身一并清理（#17） |
| P1 | AI 润色依赖外部服务，无 Key 时仅返回消息 | 前端在无 Key 时引导用户跳转 AI 设置 |
| P2 | PDF 导出依赖本机 LibreOffice | README/About 页说明安装方式，或打包时附安装提示 |
| P2 | 新能力前端入口未全部挂接 | 下一迭代：校审中心加条款列/暗标扫描；设置页加标准包下拉 |
| P2 | vite 提示单 chunk >500KB | 后续可按路由 code-split |

## 六、结论

- **可用性评分：4.3/5**（主流程稳定、性能优秀、降级优雅；新能力前端入口待补）。
- **多平台就绪度：Windows 已验证 ✅，Linux/macOS 静态评估通过，需目标环境复验**。
- 可用性测试脚本已入库（`scripts/usability_test.py`），可随时复跑。
