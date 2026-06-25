# Office 插件生态 + 样式模板中心 设计文档

## 1. 总体架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户界面层                              │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────────┐ │
│  │ Word插件  │  │ WPS插件   │  │ Electron桌面端         │ │
│  └────┬─────┘  └────┬─────┘  └────────┬───────────────┘ │
│       │              │                 │                  │
│  ┌────┴──────────────┴─────────────────┴───────────────┐ │
│  │              Plugin Bridge (HTTP REST)               │ │
│  └────────────────────┬────────────────────────────────┘ │
├───────────────────────┼──────────────────────────────────┤
│                    服务层                                  │
│  ┌────────────────────┴────────────────────────────────┐ │
│  │              FastAPI Backend (localhost:8765)         │ │
│  │  ┌──────────┐ ┌───────────┐ ┌────────────────────┐  │ │
│  │  │ Document │ │   Rule    │ │   Template Center  │  │ │
│  │  │ Engine   │ │  Engine   │ │   (新增)            │  │ │
│  │  └──────────┘ └───────────┘ └────────────────────┘  │ │
│  │  ┌──────────┐ ┌───────────┐ ┌────────────────────┐  │ │
│  │  │   AI     │ │  Style    │ │   Office Bridge    │  │ │
│  │  │ Provider │ │ Generator │ │   API (新增)        │  │ │
│  │  └──────────┘ └───────────┘ └────────────────────┘  │ │
│  └─────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────┤
│                    核心引擎层                              │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Python Core Engine (唯一业务逻辑源)                 │  │
│  │  • Document Parser / Generator / Modifier          │  │
│  │  • Font Utils (eastAsia/ascii/hAnsi/cs)            │  │
│  │  • Rule Checker / Fixer / Manager                  │  │
│  │  • AI Provider (OpenAI/DeepSeek/Custom)            │  │
│  │  • Template Style Generator (新增)                  │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

**核心原则：本地核心引擎唯一，所有界面共享同一后端。**

## 2. Plugin Bridge 设计

Office 插件（Word/WPS）通过 HTTP REST 与本地后端通信。

### 2.1 通信协议

```
Office Add-in ──HTTP──→ localhost:8765/api/office/...
```

所有 Office 插件共用同一套 API，无需各自实现业务逻辑。

### 2.2 Bridge API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/office/health` | GET | 健康检查 |
| `/api/office/check` | POST | 检查当前文档 |
| `/api/office/fix` | POST | 一键格式规范 |
| `/api/office/ai-optimize` | POST | AI 优化 |
| `/api/office/templates` | GET | 获取模板列表 |
| `/api/office/apply-template` | POST | 应用模板样式 |
| `/api/office/generate-template` | POST | 生成 dotx 模板文件 |

### 2.3 数据流

```
Word/WPS 用户操作
    ↓
Add-in Task Pane (JavaScript)
    ↓ HTTP POST (document base64 + action)
Bridge API (FastAPI)
    ↓
Python Core Engine
    ↓ 返回结果
Bridge API
    ↓ JSON response
Add-in Task Pane → 显示结果 / 应用修改
```

## 3. 样式模板中心

### 3.1 模板 YAML 规范

```yaml
# template.yaml
name: "通知模板"
type: notice
version: "1.0"
author: "官方"
standard: "GB/T 9704-2012"

page:
  size: A4
  width_mm: 210
  height_mm: 297
  margins:
    top: 3.7cm
    bottom: 3.5cm
    left: 2.8cm
    right: 2.6cm

styles:
  title:
    font_east_asia: "方正小标宋简体"
    font_latin: "Times New Roman"
    size: 22pt
    bold: false
    alignment: center
    space_after: 20pt

  body:
    font_east_asia: "仿宋_GB2312"
    font_latin: "Times New Roman"
    size: 16pt
    alignment: justify
    line_spacing: 28.95pt
    first_line_indent: 2em

  subtitle:
    font_east_asia: "楷体_GB2312"
    font_latin: "Times New Roman"
    size: 16pt
    bold: true

  signature:
    font_east_asia: "仿宋_GB2312"
    size: 16pt
    alignment: right

  date:
    font_east_asia: "仿宋_GB2312"
    size: 16pt
    alignment: right
    format: "YYYY年MM月DD日"

watermark:
  enabled: false
```

### 3.2 模板目录结构

```
templates/
├── official/          # 官方模板（只读）
│   ├── notice.yaml
│   ├── request.yaml
│   └── ...
├── custom/            # 单位模板
└── user/              # 用户模板
```

### 3.3 模板产物

| 产物 | 格式 | 用途 |
|------|------|------|
| `.docx` | Word 文档 | 预填充内容的模板文档 |
| `.dotx` | Word 模板 | 安装到 Word/WPS 模板库 |
| `.yaml` | 规则文件 | 导入导出 |

## 4. Style Generator

将 YAML 模板转换为 Word 模板（.dotx）：

```
template.yaml
    ↓ parse
StyleConfig (Pydantic model)
    ↓ generate
python-docx Document
    ↓ save as .dotx
.dotx file
```

关键点：
- 所有字体必须通过 `font_utils.set_run_font()` 设置
- 样式写入 Word 样式库（而非内联格式）
- 用户新建文档时自动继承样式

## 5. Office 插件技术选型

### 5.1 Word Add-in
- **技术**: Office.js API + React Task Pane
- **打包**: manifest.xml + webpack bundle
- **安装**: 旁加载（sideload）或组织部署

### 5.2 WPS Add-in
- **技术**: WPS JS API（兼容 Office.js）
- **差异**: manifest.xml 格式略有不同
- **适配**: bridge 层统一，插件层各自适配

### 5.3 共用 Bridge
- 两个插件共享 `/api/office/*` 端点
- 文档内容通过 base64 传输
- 返回结果通过 JSON

## 6. 实施路线

### Phase 1（本次 — 已完成）
- [x] 架构设计文档
- [x] Template Center 后端 (`core/template/style_manager.py`, `generator.py`)
- [x] Style Generator（.docx + .dotx 生成）
- [x] Bridge API (`office-plugin/bridge/local_api.py`)
- [x] 前端模板中心增强（样式下载/安装按钮）
- [x] 8 个官方样式模板 YAML
- [x] 样式模板 API 端点 (`/api/templates/styles/...`)

### Phase 2（后续）
- [ ] Word Add-in manifest.xml + Task Pane
- [ ] WPS Add-in 适配
- [ ] Electron 菜单集成
- [ ] Task Pane UI
- [ ] 实机测试

### Phase 3（未来）
- [ ] 模板市场（在线分享）
- [ ] 批量文档处理
- [ ] 模板版本管理