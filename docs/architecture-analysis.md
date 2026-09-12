# 项目整体架构剖析与评估（分层 / 依赖 / 扩展性）

> 本文档基于源码依赖分析与代码走查（2026-09-11），仅做评估与建议，不涉及代码改动。
> 依赖证据来源：`file_dependencies` / 代码导入扫描 / codegraph 缓存（`.codegraph/codegraph.db`，195 文件 / 1858 节点）。

## 一、总体架构

```
┌─────────────────────────────────────────────────────────────┐
│ Electron Shell (frontend/electron/main.ts)                  │
│   生成/终止 Python 后端，健康检查 /api/health，托盘           │
├─────────────────────────────────────────────────────────────┤
│ React 19 SPA (HashRouter, file:// 协议)                     │
│   pages → api/client.ts(axios 拦截器自动解包) → REST :8765   │
├─────────────────────────────────────────────────────────────┤
│ FastAPI (backend/main.py) — 10 组路由：                     │
│   documents / check / optimize / ai / settings / templates  │
│   template_download / rules / office / auth / workspace     │
├─────────────────────────────────────────────────────────────┤
│ 领域层 backend/services → backend/core                      │
│   core/document  core/rules  core/template  core/optimize   │
│   ai(providers)   db(SQLAlchemy)   utils                    │
├─────────────────────────────────────────────────────────────┤
│ SQLite (WAL)  app.db   |   rules/official+ custom+ user     │
│ templates/official+ custom+ user                            │
└─────────────────────────────────────────────────────────────┘
```

**核心管线**（全程唯一数据载体 `DocumentModel`，Pydantic 中间表示）：

```
.docx → parser.parse_docx() → DocumentModel → RuleEngine.check/fix
      → DocumentModifier（唯一变更点）→ generator.generate_docx() → .docx
```

**关键不变量**（代码中已落实）：
- 解析/生成均只感知 `DocumentModel`，互不感知对方（模块间解耦）。
- `core.rules.fixer` 是规则修复的唯一入口，所有 `modify_*` 均来自 `core.document.modifier`。
- 字体四属性（ascii/hAnsi/eastAsia/cs）统一走 `font_utils.set_run_font()`（中文文档兼容性 P0 细节）。
- 本会话新增扩展点已并入既有不变量：`standard_ref`（证据链）、`semantic.py`（语义校验，注入 `RuleEngine.check/check_and_fix`）、`special_layout.py`（特殊版式，注入 `generate_docx`）。

## 二、分层评估

### 2.1 依赖方向抽查（USES / USED BY）

| 模块 | 依赖（USES） | 评估 |
|---|---|---|
| `core/rules/engine.py` | checker / fixer / loader / manager / semantic（全部 core.rules 内） | ✅ 内聚，子域内依赖 |
| `core/document/parser.py` | ai_structure_analyzer / font_utils / models / parser_format + db.models（懒加载） | ⚠️ 见 Q2 |
| `core/document/generator.py` | font_utils / special_layout + db.models（懒加载） | ⚠️ 见 Q2 |
| `services/document_service.py` | core(generator/parser/engine) + db + utils + **api.routes.optimize** | ❌ 见 Q1 |
| `backend/core` 全量扫描 `from db/api/services import` | 无顶层导入命中 | ✅ core 不含反向依赖（仅懒加载例外） |

### 2.2 发现的分层问题

- **Q1（中）service → route 反向依赖**：`document_service.optimize_document` 在函数内 `from api.routes.optimize import _inject_header_to_docx/_inject_footer_to_docx/_inject_page_number_to_docx`。版头/版记/页码注入是文档能力，应位于 `core/document`（modifier 或 generator），而非路由层。方向颠倒导致：核心能力无法被 CLI（wfp_cli）、office-plugin 复用，且 route 与 service 互相 import。
- **Q2（低）core 懒加载 db/ai**：`ai_structure_analyzer` 以 try/except 懒加载 db/ai（规避 ImportError 与冷启动）。可接受，但建议以 provider/回调接口取代直接 db 依赖，保持 core 纯净。
- **Q3（中）业务编排散落**：`optimize.py`（路由）直接构建并操作 `DocumentModel`、直接调用 `convert_markdown`/`load_rules_for_type`，绕过 service 层；规则「检查→修复→生成」之外的大量编排（版头注入、Markdown 转换、模板套用）耦合在路由内，可测试性与复用性受限。
- **Q4（低）大文件**：`generator.py` 936 行、`optimize.py` 1100+ 行、`checker.py` 625 行，函数级职责尚可，但文件级聚合适中偏大；扩展示例已证明可以**声明式**扩展（见第四节）。
- **Q5（信息）**：`file_dependencies` 中 frontend 文件出现在后端 USES，为工具的跨目录字符串匹配噪音，非真实依赖。

## 三、依赖评估

- **无循环依赖**：core 内子域（document ↔ rules）通过 `DocumentModel` 单向协作；db/service/api 不反向进入 core 顶层导入。
- **变更点收敛**：`DocumentModifier` 是模型唯一变更点；checker/fixer 通过规则字典驱动，无业务硬编码。
- **顺风依赖**：api → services → core → (models/utils)；新模块（semantic / special_layout / standard_refs）均被上层单向引用，未破坏方向。
- **风险点**：Q1 的 route↔service 互相引用是小环的隐患；一旦在 route 内新增对 service 的同步状态依赖，即形成真环，建议尽早下沉 `_inject_*` 函数。

## 四、扩展性评估

### 4.1 强扩展点（声明式，已验证本会话实操）

| 扩展维度 | 机制 | 新增一项的成本 |
|---|---|---|
| 新增检查规则 | rules YAML（3 层合并）+ 可选 `standard_ref` 覆盖 | 1 个 YAML 条目，无需改代码 |
| 新增文种 | `rules/official/<type>.yaml` + 模板 | 1 YAML + 1 模板文件 |
| 标准条款映射 | `standard_refs.FIELD_REF_MAP` 前缀表 | 1 行映射 |
| 语义校验 | `semantic.SEMANTIC_RULES` 登记表 | 1 条目 + 1 个 check 函数 |
| 特殊版式 | `layout_profile` + `special_layout` 分支 | 1 profile 分支 + OXML 函数 |
| AI 服务商 | `ai/providers` 子类 + `manager.create_provider` 注册 | 1 文件 |
| 模板优先级 | 官方 < 自定义 < 用户 三层深合并 | 放入对应目录即可 |

### 4.2 弱扩展点（需要重构才能低成本扩展）

1. **编排层固化**：检查/优化/版头注入的业务流绑定在 `document_service` + `optimize.py` 路由；新增一种「处理模式」（如暗标合规、保持版式编辑）需要复制流程。
2. **AI 触发分散**：结构分析由 parser 触发、语义分析由 service 触发、健康检测独立线程——策略分散，缺少统一的 AI 编排层。
3. **前端无全局状态**：各页面 `useState` 自管，跨页状态（AI 启用、模型健康）靠事件桥接；多页一致性问题已在 Known Gaps 记录。
4. **无 schema 迁移框架**：SQLite 靠 `init_db` + 手写 `_ensure_column` 增量补列；后续字段增多建议引入轻量迁移。

## 五、结论与建议

- **总体评价**：核心架构（DocumentModel 中间表示 + 规则驱动 + 单一变更点）是健康的，依赖方向基本正确，本会话以极低成本完成了 4 类声明式扩展，验证了扩展性。
- **优先改进（后续演进依据）**：
  1. 把 `_inject_header/footer/page_number_*` 从 `api/routes/optimize.py` 下沉到 `core/document`（消除 Q1 反向依赖）；
  2. 将 optimize 路由中的编排逻辑抽为 `services/optimize_service.py`（吸收 Q3）；
  3. core 对 db 的懒加载改为注入式（吸收 Q2）；
  4. 前端引入轻量全局状态（已列入 P2-14 执行项）。
- **结论**：分层 3.5/5（方向正确、局部倒挂）、依赖 4/5（无环、个别软耦合）、扩展性 4.5/5（声明式扩展是最大资产）。