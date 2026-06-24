# 项目架构设计报告

> AI 公文智能优化助手（Official Document AI Assistant）
> 编制日期：2026-06-22
> 版本：v0.1.0-alpha
> 作者：Jose AI - www.linhut.cn

---

## 一、项目概述

**目标产品**：一款 Windows 桌面应用，用户安装后可一键完成公文格式检测、排版优化、错别字检查和 AI 辅助润色。

**核心价值**：将公文格式审查从人工逐行比对升级为自动化规则引擎 + AI 辅助，大幅降低公文出错率。

---

## 二、当前环境扫描结果

| 组件 | 状态 | 版本 |
|------|------|------|
| Python | ✅ 已安装 | 3.14.5 |
| pip | ✅ 已安装 | 26.1.1 |
| Node.js | ✅ 已安装 | v24.14.0 |
| npm | ✅ 已安装 | 11.9.0 |
| python-docx | ❌ 未安装 | — |
| LibreOffice | ❌ 未安装 | — |
| Git | ✅ 已安装 | 空仓库 master 分支 |
| 项目文件 | ❌ 无任何文件 | — |

**环境风险**：Python 3.14 为最新版本，部分第三方库兼容性需验证。建议优先测试 python-docx、FastAPI、uvicorn、pydantic 等核心依赖在 3.14 下的安装情况。

---

## 三、技术选型

### 3.1 前端（Electron + React）

| 技术 | 版本 | 用途 |
|------|------|------|
| Electron | 35.x | 桌面壳，管理窗口、IPC、打包 |
| React | 19.x | UI 框架 |
| TypeScript | 5.x | 类型安全 |
| Vite | 6.x | 构建工具，HMR 开发体验 |
| TailwindCSS | 4.x | 原子化样式 |
| shadcn/ui | latest | 组件库（基于 Radix UI） |
| Lucide React | latest | 图标库 |
| Zustand | 5.x | 状态管理（轻量） |

### 3.2 后端（Python Core Engine）

| 技术 | 用途 |
|------|------|
| Python 3.12+ | 核心运行时 |
| FastAPI | 本地 HTTP 服务，供 Electron 调用 |
| uvicorn | ASGI 服务器 |
| python-docx | Word 文档读写 |
| PyYAML | 规则配置解析 |
| pydantic | 数据模型校验 |
| cryptography | API Key 加密存储 |
| SQLAlchemy + SQLite | 本地数据持久化 |
| LibreOffice headless | docx -> PDF 转换（可选） |

### 3.3 打包方案

| 组件 | 方案 |
|------|------|
| 前端 | electron-builder → setup.exe |
| 后端 | PyInstaller → 单个 .exe 或目录 |
| 集成 | Electron 启动时自动 spawn Python 后端进程 |

---

## 四、项目目录结构

`
official-document-ai-assistant/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── PROJECT_STATUS.md
├── .gitignore
├── docs/
│   └── architecture-report.md        # 本文件
│
├── frontend/                          # Electron + React 前端
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── electron-builder.yml
│   ├── electron/
│   │   ├── main.ts                   # Electron 主进程
│   │   ├── preload.ts                # 预加载脚本（IPC 桥接）
│   │   └── ipc-handlers.ts           # IPC 事件处理
│   └── src/
│       ├── main.tsx                  # React 入口
│       ├── App.tsx                   # 根组件
│       ├── components/
│       │   ├── ui/                   # shadcn/ui 组件
│       │   ├── FileDropZone.tsx       # 拖拽上传区
│       │   ├── DocumentPreview.tsx    # 文档预览
│       │   ├── CheckResultList.tsx    # 检查结果列表
│       │   ├── IssueCard.tsx          # 单条问题卡片
│       │   ├── ProgressBar.tsx        # 任务进度
│       │   └── AISuggestionPanel.tsx  # AI 建议面板
│       ├── pages/
│       │   ├── Home.tsx              # 首页/上传页
│       │   ├── CheckCenter.tsx       # 校审中心
│       │   ├── Optimize.tsx          # 优化结果页
│       │   └── Settings.tsx          # 设置页
│       ├── stores/
│       │   ├── document-store.ts     # 文档状态
│       │   └── settings-store.ts     # 设置状态
│       ├── services/
│       │   └── api.ts                # 调用 Python 后端的 HTTP 客户端
│       ├── types/
│       │   └── index.ts              # 共享类型定义
│       └── styles/
│           └── globals.css
│
├── backend/                           # Python Core Engine
│   ├── pyproject.toml                # 项目配置与依赖
│   ├── requirements.txt              # pip 依赖锁定
│   ├── main.py                       # FastAPI 入口
│   ├── config.py                     # 全局配置
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── document/
│   │   │   ├── __init__.py
│   │   │   ├── parser.py             # docx -> Document JSON Model
│   │   │   ├── generator.py          # Document JSON Model -> docx
│   │   │   ├── models.py             # Pydantic 数据模型
│   │   │   └── converter.py          # 格式转换（docx->PDF等）
│   │   │
│   │   ├── rules/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py             # 规则引擎主逻辑
│   │   │   ├── checker.py            # 格式检查器
│   │   │   ├── fixer.py              # 自动修复器
│   │   │   └── loader.py             # YAML 规则加载器
│   │   │
│   │   └── optimize/
│   │       ├── __init__.py
│   │       ├── detector.py           # 问题检测器
│   │       └── modifier.py           # 文档修改器
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── base.py                   # AIProvider 抽象基类
│   │   ├── manager.py                # AI 调用管理器
│   │   └── providers/
│   │       ├── __init__.py
│   │       ├── openai_provider.py
│   │       ├── claude_provider.py
│   │       ├── gemini_provider.py
│   │       ├── deepseek_provider.py
│   │       ├── tongyi_provider.py    # 通义千问
│   │       ├── zhipu_provider.py     # 智谱
│   │       ├── ollama_provider.py
│   │       └── custom_provider.py    # 自定义 OpenAI 兼容 API
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── documents.py          # 文档 CRUD
│   │   │   ├── check.py              # 格式检查
│   │   │   ├── optimize.py           # 优化执行
│   │   │   ├── ai.py                 # AI 分析
│   │   │   └── settings.py           # 配置管理
│   │   └── schemas/
│   │       ├── __init__.py
│   │       └── api_models.py         # 请求/响应 Pydantic 模型
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py               # SQLAlchemy 引擎/会话
│   │   ├── models.py                 # ORM 模型
│   │   └── migrations/               # Alembic 迁移
│   │
│   └── utils/
│       ├── __init__.py
│       ├── crypto.py                 # API Key 加解密
│       ├── logger.py                 # 日志配置
│       └── file_utils.py             # 文件工具
│
├── rules/                             # 公文规则配置（YAML）
│   └── official/
│       ├── _common.yaml              # 公共基础规则
│       ├── notice.yaml               # 通知
│       ├── request.yaml              # 请示
│       ├── report.yaml               # 报告
│       ├── letter.yaml               # 函
│       ├── meeting.yaml              # 会议纪要
│       ├── decision.yaml             # 决定
│       ├── announcement.yaml         # 通告
│       └── notice_public.yaml        # 公告
│
├── tests/
│   ├── conftest.py
│   ├── backend/
│   │   ├── test_parser.py
│   │   ├── test_rules_engine.py
│   │   ├── test_checker.py
│   │   ├── test_fixer.py
│   │   ├── test_ai_providers.py
│   │   └── test_api_routes.py
│   └── fixtures/
│       ├── sample_notice.docx
│       ├── sample_request.docx
│       └── expected_output/
│
└── scripts/
    ├── build-backend.py               # PyInstaller 打包脚本
    └── dev-start.py                   # 开发环境启动脚本
`

---

## 五、模块划分与职责

### 5.1 Document Engine（文档引擎）

**职责**：将 .docx 文件解析为中间 JSON 模型，以及将 JSON 模型还原为 .docx。

**核心设计原则**：绝不直接修改 Word 对象。所有操作在 JSON 模型上进行。

**数据流**：
`
.docx → Parser → DocumentModel (JSON)
DocumentModel → Modifier → DocumentModel (JSON)
DocumentModel → Generator → .docx
`

**DocumentModel 结构**（Pydantic）：
`python
class DocumentModel:
    metadata: DocumentMetadata      # 标题、作者、日期等元数据
    page_setup: PageSetup           # 纸张、页边距
    sections: list[Section]         # 文档节
    paragraphs: list[Paragraph]     # 段落列表
    tables: list[Table]             # 表格
    headers: list[HeaderFooter]     # 页眉
    footers: list[HeaderFooter]     # 页脚

class Paragraph:
    index: int                      # 段落序号
    text: str                       # 纯文本
    style_name: str                 # 样式名
    runs: list[Run]                 # 文本片段（含格式）
    level: int | None               # 标题层级
    is_heading: bool

class Run:
    text: str
    font_name: str | None
    font_size_pt: float | None
    bold: bool | None
    italic: bool | None
    color: str | None
`

### 5.2 Rule Engine（规则引擎）

**职责**：加载 YAML 规则文件，对 DocumentModel 执行格式检查和自动修复。

**设计原则**：规则配置驱动，禁止硬编码。每个公文类型对应一个 YAML 文件。

**YAML 规则结构**：
`yaml
template_name: "通知"
document_type: notice

page_setup:
  paper_size: A4
  margins:
    top: 3.7cm
    bottom: 3.5cm
    left: 2.8cm
    right: 2.6cm

title:
  font: "方正小标宋简体"
  font_fallback: "SimSun"
  size: 22pt
  align: center
  bold: false
  spacing_after: 20pt

body:
  font: "仿宋_GB2312"
  font_fallback: "FangSong"
  size: 16pt           # 三号
  line_spacing: 28.95pt # 固定值28磅
  first_line_indent: 2em
  align: justify

signature:
  font: "仿宋_GB2312"
  size: 16pt
  align: right

date:
  font: "仿宋_GB2312"
  size: 16pt
  format: "YYYY年MM月DD日"
  align: right

check_rules:
  - id: CHK-001
    name: "标题字体检查"
    severity: P0
    field: title.font
    expected: "方正小标宋简体"
    message: "标题应使用方正小标宋简体"

  - id: CHK-002
    name: "正文字号检查"
    severity: P0
    field: body.size
    expected: 16pt
    message: "正文应使用三号字体(16pt)"

fix_rules:
  - id: FIX-001
    ref_check: CHK-001
    action: set_font
    target: title
    value: "方正小标宋简体"
`

### 5.3 AI Provider（AI 服务层）

**职责**：提供统一的 AI 分析接口，支持多家大模型厂商。

**抽象接口**：
`python
class AIProvider(ABC):
    @abstractmethod
    async def analyze(self, document: DocumentModel) -> AIAnalysisResult:
        """分析文档，返回问题列表"""

    @abstractmethod
    async def proofread(self, text: str) -> list[ProofreadIssue]:
        """校对文本，返回错别字/标点问题"""

    @abstractmethod
    async def rewrite(self, text: str, context: str) -> str:
        """改写文本，返回优化建议"""
`

**AI 返回格式**（统一）：
`json
{
  "issues": [
    {
      "type": "format_error | typo | expression | logic",
      "severity": "P0 | P1 | P2",
      "position": "paragraph:3,run:2",
      "before": "原文",
      "after": "建议修改",
      "reason": "修改原因说明"
    }
  ]
}
`

**配置存储**：API Key 使用 Fernet 对称加密，密钥派生自机器标识 + 用户密码（可选）。配置保存至 SQLite i_config 表。

### 5.4 API Layer（FastAPI 路由层）

**路由设计**：

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /api/documents/upload | 上传文档 |
| GET | /api/documents/{id} | 获取文档信息 |
| POST | /api/check/{doc_id} | 执行格式检查 |
| GET | /api/check/{doc_id}/results | 获取检查结果 |
| POST | /api/optimize/{doc_id} | 执行自动优化 |
| GET | /api/optimize/{doc_id}/download | 下载优化后文档 |
| POST | /api/ai/analyze | AI 分析文档 |
| POST | /api/ai/proofread | AI 校对 |
| GET | /api/settings/ai | 获取 AI 配置 |
| PUT | /api/settings/ai | 更新 AI 配置 |
| POST | /api/settings/ai/test | 测试 AI 连接 |

### 5.5 Electron Shell（桌面壳层）

**进程模型**：
- **Main Process**：管理窗口、系统托盘、启动/停止 Python 后端
- **Renderer Process**：React 应用，通过 preload.ts 中的安全 IPC 桥与主进程通信
- **Python Backend**：独立子进程，通过 HTTP 与前端通信（localhost 随机端口）

**IPC 事件**：
- pp:start-backend → 启动 Python 进程
- pp:stop-backend → 停止 Python 进程
- pp:get-backend-url → 获取后端地址
- dialog:open-file → 打开文件选择对话框
- dialog:save-file → 保存文件对话框

---

## 六、数据模型（SQLite）

### 6.1 ER 图概览

`
documents (1) ──→ (N) document_versions
documents (1) ──→ (N) check_results
ai_config (独立)
rules (独立)
`

### 6.2 表结构

**documents**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| filename | TEXT NOT NULL | 原始文件名 |
| file_path | TEXT NOT NULL | 存储路径 |
| file_hash | TEXT NOT NULL | SHA-256 哈希 |
| document_type | TEXT | 公文类型（notice/request/...）|
| status | TEXT DEFAULT 'uploaded' | uploaded/checking/checked/optimized |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**document_versions**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| document_id | INTEGER FK → documents.id | 所属文档 |
| version | INTEGER | 版本号 |
| file_path | TEXT NOT NULL | 版本文件路径 |
| change_summary | TEXT | 变更摘要 |
| created_at | DATETIME | 创建时间 |

**check_results**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| document_id | INTEGER FK → documents.id | 所属文档 |
| check_type | TEXT | format/typo/expression/logic |
| severity | TEXT | P0/P1/P2 |
| rule_id | TEXT | 规则编号 |
| location | TEXT | 位置描述 |
| original_text | TEXT | 原文 |
| suggested_fix | TEXT | 建议修改 |
| reason | TEXT | 原因说明 |
| status | TEXT DEFAULT 'pending' | pending/accepted/dismissed |
| created_at | DATETIME | 创建时间 |

**ai_config**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| provider | TEXT NOT NULL | 供应商标识 |
| api_key_encrypted | TEXT | 加密后的 API Key |
| base_url | TEXT | API 地址 |
| model | TEXT | 模型名称 |
| extra_params | TEXT | JSON 格式附加参数 |
| is_active | BOOLEAN DEFAULT false | 是否启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**rules**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| rule_id | TEXT NOT NULL UNIQUE | 规则编号（如 CHK-001）|
| name | TEXT NOT NULL | 规则名称 |
| document_type | TEXT | 适用公文类型 |
| severity | TEXT | P0/P1/P2 |
| rule_content | TEXT | JSON 格式规则定义 |
| is_enabled | BOOLEAN DEFAULT true | 是否启用 |
| created_at | DATETIME | 创建时间 |

---

## 七、开发路线

### Phase 1：基础骨架（当前阶段）
- [x] 环境扫描
- [ ] 项目目录结构创建
- [ ] 开源文件生成（README/LICENSE/CONTRIBUTING/CHANGELOG/PROJECT_STATUS）
- [ ] Python 后端骨架（FastAPI + SQLite）
- [ ] Electron 前端骨架（Vite + React + TypeScript）
- [ ] 前后端联通验证

### Phase 2：文档引擎
- [ ] Document JSON Model（Pydantic 数据模型）
- [ ] docx Parser（python-docx 解析）
- [ ] docx Generator（python-docx 生成）
- [ ] 解析/生成单元测试

### Phase 3：规则引擎
- [ ] YAML 规则加载器
- [ ] 公共基础规则（_common.yaml）
- [ ] 通知模板规则（notice.yaml）
- [ ] 格式检查器（Checker）
- [ ] 自动修复器（Fixer）
- [ ] 检查结果 API + 前端展示

### Phase 4：校审中心
- [ ] 检查结果 UI（类似 IDE 问题面板）
- [ ] P0/P1/P2 分级显示
- [ ] 单条问题的"应用修改"/"忽略"交互
- [ ] 一键全部修复

### Phase 5：AI 集成
- [ ] AIProvider 抽象基类
- [ ] OpenAI / DeepSeek Provider 实现
- [ ] AI 配置页面（前端）
- [ ] API Key 加密存储
- [ ] AI 分析 → 规则引擎执行 → 文档生成 完整链路

### Phase 6：剩余公文模板
- [ ] 请示（request.yaml）
- [ ] 报告（report.yaml）
- [ ] 函（letter.yaml）
- [ ] 会议纪要（meeting.yaml）
- [ ] 决定（decision.yaml）
- [ ] 通告（announcement.yaml）
- [ ] 公告（notice_public.yaml）

### Phase 7：打包与发布
- [ ] PyInstaller 打包 Python 后端
- [ ] electron-builder 打包前端
- [ ] 集成测试
- [ ] setup.exe 生成与验证

---

## 八、风险分析

### 8.1 高风险

| 风险 | 影响 | 缓解措施 |
|------|------|------|
| Python 3.14 兼容性 | 部分库可能不支持 3.14 | 降级至 3.12 如遇兼容问题；先验证核心依赖安装 |
| LibreOffice 未安装 | PDF 转换功能不可用 | PDF 转换设为可选功能；提供安装引导 |
| 字体兼容性 | 公文要求的特殊字体（方正小标宋等）可能未安装 | 检测字体可用性，提供 fallback 字体映射 |
| python-docx 样式限制 | 复杂样式（艺术字、分栏等）解析不完整 | MVP 阶段聚焦常见样式；记录已知限制 |

### 8.2 中风险

| 风险 | 影响 | 缓解措施 |
|------|------|------|
| Electron 打包体积 | 整体包体可能较大（Python runtime + LibreOffice） | PyInstaller onefile 模式；考虑按需下载 |
| AI API 稳定性 | 第三方 API 不可用 | 实现重试、超时、降级（纯规则引擎可用）|
| 公文规范差异 | 各地/各级机关规范可能不同 | 规则 YAML 可由用户自定义扩展 |

### 8.3 低风险

| 风险 | 影响 | 缓解措施 |
|------|------|------|
| 前端框架升级 | React/Electron 版本迭代 | 锁定版本，定期评估升级 |
| 数据库迁移 | SQLite -> PostgreSQL 切换 | 使用 SQLAlchemy ORM 抽象 |

---

## 九、关键技术决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 前后端通信方式 | HTTP REST（localhost） | 简单可靠；无需 IPC 复杂序列化 |
| 状态管理 | Zustand | 轻量、TypeScript 友好、无需 boilerplate |
| 规则存储 | YAML 文件 + SQLite 双写 | YAML 便于版本管理和编辑；SQLite 便于查询 |
| AI 接口设计 | 统一返回 JSON issues 数组 | 所有 Provider 返回格式一致，下游无感知 |
| 数据库 ORM | SQLAlchemy | 成熟稳定，未来迁移 PostgreSQL 成本低 |
| 打包策略 | Electron-builder + PyInstaller | 业界标准方案，社区支持好 |

---

## 十、待确认事项

1. **Python 版本**：当前环境为 3.14，需确认核心依赖（python-docx, FastAPI, pydantic, SQLAlchemy）是否兼容。若不兼容，需安装 3.12。
2. **LibreOffice 安装**：当前未安装。是否需要在 Phase 1 安装？还是推迟到 Phase 7？
3. **公文规范参考**：是否有具体的 GB/T 9704-2012 或最新版本作为规则制定依据？
4. **AI Provider 优先级**：第一批实现哪些 Provider？建议 DeepSeek + OpenAI 兼容接口。
5. **项目命名**：npm package name 和 PyPI package name 的正式命名？
6. **LICENSE 类型**：MIT / Apache 2.0 / 其他？

---

*报告完毕。等待确认后进入 Phase 1 开发。*
