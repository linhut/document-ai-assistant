# 公文智能校审助手 — Word VBA 插件

## 功能

在 Microsoft Word 中直接使用公文格式校审功能，无需切换到桌面应用：

- **格式检查** — 根据 GB/T 9704 标准检查当前文档格式问题
- **一键优化** — 自动修复字体、字号、行距、缩进等格式问题
- **套用模板** — 选择公文类型模板，一键应用标准格式
- **14种公文类型** — 通知、请示、报告、函、批复、决定、意见等

## 系统要求

- Microsoft Word 2010 及以上版本（含 Office 365）
- 公文智能校审助手桌面应用已启动（后端服务运行在 `http://127.0.0.1:8765`）

## 安装步骤

### 方法一：通过 VBA 编辑器导入（推荐）

1. 打开 Word
2. 按 `Alt + F11` 打开 VBA 编辑器
3. 在左侧"工程资源管理器"中找到 `Normal` 或你的模板
4. 右键 → **导入文件**，依次导入：
   - `HttpHelper.bas` — HTTP 通信 + Base64 + JSON 工具
   - `OfficeBridgeAPI.bas` — API 业务封装
   - `RibbonCallbacks.bas` — 功能区回调处理
5. 关闭 VBA 编辑器
6. 将 `ribbon.xml` 通过 Custom UI Editor 嵌入到 `.dotm` 模板中
7. 重启 Word，功能区将出现"公文校审"选项卡

### 方法二：通过 .dotm 模板加载

1. 将所有 `.bas` 文件和 `ribbon.xml` 打包到一个 `.dotm` 模板文件中
2. 将该 `.dotm` 文件复制到 Word 启动目录：
   - `C:\Users\<用户名>\AppData\Roaming\Microsoft\Word\STARTUP\`
3. 重启 Word

### Custom UI Editor 使用

1. 下载 [Custom UI Editor](https://github.com/fernandreu/office-js/releases)
2. 打开目标 `.dotm` 文件
3. 点击 **Insert** → **Office 2010+ Custom UI Part**
4. 将 `ribbon.xml` 的内容粘贴进去
5. 保存并关闭

## 使用方法

1. 确保公文智能校审助手桌面应用已启动
2. 在 Word 中打开要校审的公文
3. 点击"公文校审"选项卡
4. 选择文档类型（默认为"通知"）
5. 点击"格式检查"查看问题，或直接点击"一键优化"自动修复

## 文件说明

| 文件 | 说明 |
|------|------|
| `HttpHelper.bas` | HTTP 请求、Base64 编解码、轻量 JSON 解析 |
| `OfficeBridgeAPI.bas` | 调用后端 `/api/office/*` 端点的业务函数 |
| `RibbonCallbacks.bas` | 功能区按钮点击事件处理 |
| `ribbon.xml` | 自定义功能区 UI 定义（XML） |

## 后端 API

插件通过以下 REST API 与后端通信：

| 端点 | 功能 |
|------|------|
| `GET /api/office/health` | 健康检查 |
| `POST /api/office/check` | 文档格式检查 |
| `POST /api/office/fix` | 文档自动修复 |
| `POST /api/office/apply-template` | 套用模板 |
| `GET /api/office/templates` | 获取模板列表 |
| `POST /api/office/generate-template` | 下载模板文件 |

## 常见问题

**Q: 点击按钮后提示"后端服务未启动"**
A: 请先启动公文智能校审助手桌面应用，确保 `http://127.0.0.1:8765` 可访问。

**Q: 检查/修复后文档没有变化**
A: 优化后的文档会直接替换当前文档内容。请检查文档是否已保存为 `.docx` 格式。

**Q: 宏被安全策略阻止**
A: 在 Word 中：文件 → 选项 → 信任中心 → 信任中心设置 → 宏设置 → 选择"启用所有宏"。
