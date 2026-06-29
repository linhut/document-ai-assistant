# 重构方案可行性分析报告

> **版本**: v1.0 | **日期**: 2026-06-28 | **状态**: 方案设计阶段（纯分析，无代码实现）

---

## 一、参考项目拆解分析

### 1.1 hehecat/gongwen 架构映射

| 参考项目模块 | 对应文件 | 我们项目可借鉴点 | 不可迁移部分 |
|-------------|----------|-----------------|-------------|
| **样式设置交互** | `SettingsModal.tsx` (~650行) | 参数分组策略、控件布局模式、字号标签格式 | 模板管理器(`TemplateManagerSection`)、项目信息区、捐赠区 |
| **字体选择组件** | `FontSelectField.tsx` | ComboBox 交互（下拉+自定义输入）、字体别名映射 | 自定义字体 hook(`useCustomFonts`) 我们已有 |
| **下拉组合框** | `useComboBox.ts` | 键盘导航、模糊搜索、点击外部关闭逻辑 | 无 |
| **配置状态管理** | `contexts/useDocumentConfig.ts` | `useReducer` + `deepMerge` + `localStorage` 持久化 | 我们已有相同模式(`useDocumentConfig.tsx`) |
| **渲染引擎** | `Preview.tsx` + `A4Page.tsx` + `A4Page.css` | CSS 变量体系、百分比边距、letter-spacing 微调、分页算法 | AST 数据结构、`DocumentFlow` 组件（我们用段落数组） |
| **分页算法** | `usePagination.ts` | DOM 度量 + 行边界切割 + 末页版记预留 | 需适配我们的 `DocParagraph[]` 数据格式 |
| **字号常量** | `types/documentConfig.ts` | `FONT_SIZE_PRESET_LABELS` 映射（初号/小初/一号...） | `cmToTwip`/`ptToHalfPoint`（Word 内部单位，我们不需要） |

### 1.2 样式交互模式适配成本评估

**低适配成本（可直接复用模式）**：
- `SelectField` / `NumberField` / `CheckboxField` / `TextField` 控件模式 — 通用 UI 原子组件，无业务耦合
- `settings-section` → `settings-section-title` → `settings-grid` 分组布局 — CSS class 驱动，易迁移
- `settings-section-toggle` 折叠面板 — 简单 `useState` 控制
- 字号标签 `formatFontSizeLabel()` — 纯函数，零成本迁移

**中等适配成本（需要改造）**：
- `FontSelectField` ComboBox — 需替换字体列表为我们项目的字体集（方正小标宋_GBK/仿宋_GB2312 等）
- CSS 变量体系 — 需从 `px` 单位改为 `mm`/`pt` 混合（我们用 mm 做边距、pt 做字号）
- `usePagination` 分页算法 — 需从 `DocumentNode[]` AST 适配到 `DocParagraph[]` 扁平数组

**高适配成本（不建议迁移）**：
- `cmToPagePercent` 百分比边距 — CSS 百分比 padding 是相对容器宽度，垂直方向不准确。我们项目验证过 mm 单位方案更可靠
- `letter-spacing` 微调使每行 28 字 — 需要精确测量字体宽度，不同系统字体渲染差异大，维护成本高

### 1.3 推荐借鉴策略

```
借鉴程度: ████████░░ 80%（样式交互层）
借鉴程度: ████░░░░░░ 40%（渲染机制层）
借鉴程度: ██░░░░░░░░ 20%（数据层）
```

**具体建议**：
1. **样式面板 UI 框架**：完全借鉴其分组布局、控件类型、折叠策略
2. **字号/字体常量**：直接迁移 `FONT_SIZE_PRESET_LABELS` 和 `FONT_OPTIONS`
3. **分页算法**：借鉴 DOM 度量思路，但用 mm 单位（不用百分比）
4. **CSS 渲染**：借鉴 CSS 变量思路，但用 mm 做边距（不用百分比）

---

## 二、双模块样式状态同步方案

### 2.1 问题定义

| 维度 | Module A (Markdown 优化) | Module B (A4 编排) |
|------|------------------------|-------------------|
| 样式配置范围 | 轻量子集（边距/标题/正文/页码/版头版记） | 完整参数（含特殊选项/高级设置/盖章） |
| 配置来源 | 用户手动调整 + 文种模板默认值 | 文档/模板导入 + 用户手动调整 |
| 实时性要求 | 编辑区输入 → 预览即时更新 | 参数调整 → 预览即时更新 |

### 2.2 状态管理策略对比

| 方案 | 实现方式 | 优点 | 缺点 | 推荐度 |
|------|----------|------|------|--------|
| **A: 全局 Context** | 一个 `DocumentConfigProvider` 包裹整个应用 | 两模块天然共享；localStorage 持久化；代码最少 | 无关页面也会触发重渲染；配置来源冲突（A 改了 B 不知道） | ⭐⭐⭐ |
| **B: 独立 Context + 同步层** | 各自 Context，通过事件/URL 参数同步 | 解耦清晰；各自优化渲染 | 同步逻辑复杂；容易不一致 | ⭐⭐ |
| **C: Zustand/Jotai 外部 Store** | 轻量原子状态库 | 选择性订阅，无多余渲染；持久化插件成熟 | 引入新依赖；团队学习成本 | ⭐⭐⭐⭐ |

### 2.3 推荐方案：方案 A（全局 Context）+ 分层选择器

**理由**：
1. 项目当前已使用 `useDocumentConfig` Context 模式，无需引入新依赖
2. React 18 的 `useDeferredValue` + `useMemo` 可有效控制渲染范围
3. 配置来源冲突通过"初始化时合并、运行时独立"策略解决

**架构设计**：

```
<DocumentConfigProvider>           ← 全局唯一
  ├── ModuleA (Markdown优化)
  │     ├── useConfig() → 轻量子集选择器
  │     └── initFromTemplate(docType) → 文种模板初始化
  └── ModuleB (A4编排)
        ├── useConfig() → 完整选择器
        └── initFromDocument(docId) → 文档数据初始化
```

**选择器模式**（避免全量订阅）：
```typescript
// 轻量子集（Module A 使用）
const useLightConfig = () => {
  const { config, patch } = useDocumentConfig();
  return useMemo(() => ({
    margins: config.margins,
    title: config.title,
    body: config.body,
    pageNumber: config.pageNumber,
  }), [config.margins, config.title, config.body, config.pageNumber]);
};
```

**配置来源冲突解决**：
- Module A 初始化时：调用 `patch(templateDefaults)` 覆盖为文种默认值
- Module B 初始化时：调用 `patch(importedConfig)` 覆盖为导入文档值
- 用户手动调整：正常 `patch()`，两个模块即时同步

---

## 三、左侧空间 UX 设计

### 3.1 空间约束分析

左侧面板宽度建议 **320px**（参考项目 `SettingsModal` 宽度 90vw，max-width 800px，但那是弹窗。我们的侧边面板是内嵌式，320px 是合理值）。

需要容纳的内容（按优先级排序）：

| 优先级 | 内容 | 高度估算 | 折叠策略 |
|--------|------|----------|----------|
| P0 | 文档类型选择器 | 40px | 始终显示 |
| P0 | Markdown 编辑区 | ≥200px（可拉伸） | 始终显示，占主要空间 |
| P0 | 生成预览按钮 | 40px | 始终显示 |
| P1 | 页边距 | 80px | 始终显示 |
| P1 | 标题字体+字号 | 60px | 始终显示 |
| P1 | 正文字体+字号+行距 | 100px | 始终显示 |
| P2 | 页码设置 | 60px | 默认折叠 |
| P2 | 版头/版记 | 120px | 默认折叠 |
| P3 | 特殊选项 | 80px | 默认折叠 |
| P3 | 高级标题字体 | 180px | 默认折叠 |

### 3.2 推荐布局方案

```
┌──────────────────────────┐
│ [文档类型 ▼] [通知      ] │  ← P0: 40px，始终显示
├──────────────────────────┤
│                          │
│   Markdown 编辑区         │  ← P0: flex-1，自适应剩余空间
│   (textarea, 可拖拽调高)   │     最小 180px，最大 50vh
│                          │
├──────────────────────────┤
│ [✨ AI润色] [🔄 生成预览] │  ← P0: 40px，始终显示
├──────────────────────────┤
│ 页边距: 上3.7 下3.5 左2.8│  ← P1: 紧凑行，始终显示
│ 标题: 方正小标宋 22pt     │     每行一个参数，label+控件
│ 正文: 仿宋 16pt 行距29pt  │
├──────────────────────────┤
│ ▶ 页码设置               │  ← P2: 默认折叠
│ ▶ 版头/版记              │     点击展开显示子控件
│ ▶ 特殊选项               │
│ ▶ 高级标题字体            │  ← P3: 默认折叠
└──────────────────────────┘
```

### 3.3 关键交互细节

1. **编辑区高度可拖拽**：底部拖拽条，最小 180px，最大 50vh
2. **折叠动画**：`max-height` + `overflow: hidden` + CSS transition（200ms）
3. **P1 参数区域**：每行一个参数，label 60px 左对齐 + 控件 flex-1，字号选择器显示 `16pt（三号）`
4. **生成预览按钮**：粘贴内容后高亮，空内容时 disabled
5. **滚动隔离**：P0 区域（类型+编辑区+按钮）固定，P1-P3 区域独立滚动

---

## 四、"一键优化 Markdown" 行为重定义

### 4.1 问题分析

Module B（A4 编排）没有文本输入框，但保留了"一键优化 Markdown"按钮。需要定义：**没有 Markdown 源文本时，这个按钮做什么？**

### 4.2 三种可行方案

| 方案 | 行为描述 | 优点 | 缺点 | 推荐度 |
|------|----------|------|------|--------|
| **A: 弹出导入对话框** | 点击按钮 → 弹出 Modal → 粘贴 Markdown + 选文种 → 确认 → 触发上游 `markdown-to-preview` API | 功能完整；不依赖 Module A | Modal 内再有输入框，体验割裂；与 Module A 功能重复 | ⭐⭐ |
| **B: 剪贴板读取** | 点击按钮 → 读取剪贴板 → 自动检测是否为 Markdown → 如果是则直接转换预览 | 一键操作，体验最流畅 | 剪贴板可能为空/非 Markdown；需要浏览器权限；用户不知道剪贴板里是什么 | ⭐ |
| **C: 跳转 Module A + 回调** | 点击按钮 → `useNavigate('/document/markdown')` → Module A 完成后通过 URL 参数或全局状态回传结果 → Module B 自动加载预览 | 职责清晰；不重复造轮子；用户体验连贯 | 需要定义跨页面数据传递机制；页面跳转有延迟 | ⭐⭐⭐⭐ |
| **D: 移除按钮** | Module B 不需要此按钮，Markdown 优化只在 Module A 中进行 | 最简洁；无歧义 | 功能入口减少 | ⭐⭐⭐ |

### 4.3 推荐方案：C + D 组合

**具体设计**：
1. Module B **移除**"一键优化 Markdown"按钮
2. Module A 生成预览后，提供"发送到 A4 编排"按钮
3. 点击后导航到 Module B，通过 URL 参数 `?from=markdown&data=xxx` 传递预览数据
4. Module B 检测到 `from=markdown` 参数时，自动加载数据

**数据传递机制**：
```
Module A: handleGenerate() → 生成 paragraphs + tables
         → 存入 sessionStorage('markdown_preview_data')
         → navigate('/document/enhanced-preview?from=markdown')

Module B: useEffect 检测 searchParams.get('from') === 'markdown'
         → 从 sessionStorage 读取数据
         → setParagraphs(data.paragraphs)
         → setTables(data.tables)
         → 清除 sessionStorage
```

---

## 五、盖章功能技术选型

### 5.1 需求拆解

- 用户上传透明底 PNG 印章图片
- 指定盖章页码（默认最后一页）
- 预览中显示印章位置
- 下载 .docx 时印章嵌入文档
- 打印时印章位置准确

### 5.2 技术方案对比

| 方案 | 实现原理 | 打印精度 | docx 嵌入 | 复杂度 | 推荐度 |
|------|----------|----------|-----------|--------|--------|
| **A: CSS Overlay** | 绝对定位 `<img>` 覆盖在 A4 页面上 | ⚠️ 中等 — CSS 打印时 `position: absolute` 可能偏移 | ❌ 需后端额外处理 | 低 | ⭐⭐ |
| **B: Canvas 合成** | 将 A4 内容 + 印章绘制到 Canvas | ✅ 高 — Canvas 像素级控制 | ❌ 需转图片再嵌入 | 高 | ⭐ |
| **C: python-docx 直接嵌入** | 前端传 PNG + 页码 → 后端用 python-docx 的 `add_picture()` 嵌入 | ✅ 高 — Word 原生图片定位 | ✅ 原生支持 | 中 | ⭐⭐⭐⭐ |
| **D: CSS + 后端混合** | 预览用 CSS Overlay；下载时后端 python-docx 嵌入 | 预览：⚠️ 中等 / 下载：✅ 高 | ✅ | 中 | ⭐⭐⭐⭐⭐ |

### 5.3 推荐方案：D（CSS Overlay + python-docx 嵌入）

**预览阶段**（纯前端）：
```
用户上传 PNG → 存入 state（base64）
→ 在指定页 A4Page 组件中渲染：
  <img src={stampBase64} style={{
    position: 'absolute',
    right: 'Xmm', bottom: 'Ymm',
    width: '40mm', height: '40mm',
    opacity: 0.85,
    pointerEvents: 'none',
  }} />
```

**下载阶段**（前端传参 + 后端处理）：
```
前端: POST /api/optimize/preview-download
      body: { paragraphs, tables, page_setup, stamp: { image_base64, page_number, x_mm, y_mm } }

后端: python-docx → add_picture(stamp_path, left=Cm(x), top=Cm(y), width=Cm(4), height=Cm(4))
      → 根据 page_number 定位到对应页面的段落位置
```

**打印位置偏移风险评估**：
- **CSS Overlay 风险**：`position: absolute` 在 `@media print` 中依赖包含块的定位。我们的 A4 容器是 `position: relative`，问题不大。但浏览器打印缩放（如"适合页面"）会导致偏移。**缓解措施**：打印时固定 `@media print { .a4-page { transform: none !important; } }`
- **python-docx 嵌入风险**：Word 的 `add_picture` 使用绝对定位（`Cm` 单位），与页面边距精确对齐。**风险极低**。

---

## 六、风险清单

### 6.1 高风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| **字体加载失败** | 预览字体与实际 Word 字体不一致，用户误判排版效果 | 高（方正小标宋等非系统字体） | 1. 预览用 CSS `@font-face` 加载本地 TTF；2. 字体不存在时 fallback 到 SimSun；3. 关于页提供字体下载 |
| **分页断裂** | 段落被切割在两页之间，文字不完整 | 中（DOM 度量精度依赖渲染引擎） | 1. 参考项目"行边界切割"算法；2. 末页版记预留空间迭代算法（max 10 次）；3. 超大段落不切割，整段推入下一页 |
| **双模块状态不一致** | Module A 修改样式后 Module B 未同步，或反之 | 中（Context 更新是同步的，但页面切换时可能丢失未保存状态） | 1. `localStorage` 持久化（已有）；2. 页面切换时从 localStorage 恢复；3. 避免两个页面同时打开（路由互斥） |

### 6.2 中风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| **参考项目样式交互水土不服** | ComboBox 控件在我们的 UI 体系（TailwindCSS + Radix）中风格不统一 | 中 | 1. 只借鉴交互逻辑（键盘导航、模糊搜索），不借鉴 CSS class；2. 用我们的 `Select`/`Input` 原子组件重新实现 |
| **CSS 百分比边距 vs mm 边距** | 参考项目用百分比，我们用 mm，混合使用可能导致不一致 | 低（我们已验证 mm 方案可行） | 统一使用 mm 单位，不引入百分比方案 |
| **盖章 PNG 透明度** | 用户上传非透明底 PNG，印章遮挡正文 | 中 | 1. 上传时检测图片是否有 alpha 通道；2. 无 alpha 时提示用户；3. 预览时默认 85% 透明度 |
| **Markdown 编辑区空间不足** | 左侧 320px 要容纳编辑器 + 样式控件，编辑区被压缩 | 中 | 1. 编辑区高度可拖拽；2. 样式控件默认折叠；3. 编辑区支持全屏模式 |

### 6.3 低风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| **文种模板默认值与 GB/T 9704 不一致** | 某些文种的 YAML 规则中缺少 page_setup 或格式定义 | 低（_common.yaml 已定义完整默认值） | 三层合并机制确保 _common.yaml 兜底 |
| **打印时分页丢失** | 浏览器打印不识别我们的 JS 分页 | 低（用户主要下载 .docx，不直接浏览器打印） | 提供"导出 PDF"功能作为打印替代 |
| **sessionStorage 容量限制** | 大文档的 paragraphs + tables 数据超过 5MB | 极低（单文档一般 < 100KB） | 数据超限时提示用户直接在 Module A 下载 |

---

## 七、字号选择器强制 UI 规范

### 7.1 参考项目当前格式分析

**hehecat/gongwen 当前格式**：`16（三号）` — 数值在前，中文号在括号内

```typescript
// 参考项目 types/documentConfig.ts
const FONT_SIZE_PRESET_LABELS = new Map<number, string>([
  [42, '初号'], [36, '小初'], [26, '一号'], [24, '小一'],
  [22, '二号'], [18, '小二'], [16, '三号'], [15, '小三'],
  [14, '四号'], [12, '小四'], [10.5, '五号'], [9, '小五'],
]);

export function formatFontSizeLabel(value: number): string {
  const presetName = FONT_SIZE_PRESET_LABELS.get(value);
  return presetName ? `${value}（${presetName}）` : String(value);
}
// 输出示例: "16（三号）", "22（二号）", "15"（非标准值无中文号）
```

**我们的强制格式**：`三号 (16pt)` — 中文号在前，磅值在半角括号内

### 7.2 改造成本评估

| 维度 | 评估 |
|------|------|
| **组件级改动** | 仅需修改 `formatFontSizeLabel()` 一个纯函数，零业务耦合 |
| **影响范围** | 所有 `<select>` 字号下拉控件（Module A 样式区 + Module B 格式选项卡 + 高级设置标题字体） |
| **适配成本** | **极低** — 函数签名不变，仅调整返回值模板字符串 |
| **回归风险** | **无** — 下拉选项的 `value` 仍为数字（`16`），仅 `label` 显示格式变化 |

### 7.3 完整公文常用字号映射表（硬编码常量）

以下为 GB/T 9704 及公文排版常用字号的完整映射，作为后续开发的权威常量依据：

| 中文字号 | 磅值 (pt) | 毫米 (mm) | 公文用途 |
|----------|-----------|-----------|----------|
| **初号** | 42pt | 14.82mm | 特大标题（极少用） |
| **小初** | 36pt | 12.70mm | 文件封面标题 |
| **一号** | 26pt | 9.17mm | — |
| **小一** | 24pt | 8.47mm | — |
| **二号** | 22pt | 7.76mm | **公文标题**（GB/T 9704 标准） |
| **小二** | 18pt | 6.35mm | — |
| **三号** | 16pt | 5.64mm | **正文/一级/二级/三级标题**（GB/T 9704 标准） |
| **小三** | 15pt | 5.29mm | — |
| **四号** | 14pt | 4.94mm | **页码/版记/抄送**（GB/T 9704 标准） |
| **小四** | 12pt | 4.23mm | 附件说明、表格注释 |
| **五号** | 10.5pt | 3.70mm | 脚注、参考文献 |
| **小五** | 9pt | 3.18mm | — |
| **六号** | 7.5pt | 2.65mm | — |
| **小六** | 6.5pt | 2.29mm | — |
| **七号** | 5.5pt | 1.94mm | — |
| **八号** | 5pt | 1.76mm | — |

**GB/T 9704 标准字号速查**：

| 元素 | 字号 | 格式标签 |
|------|------|----------|
| 公文标题 | 二号 | `二号 (22pt)` |
| 正文 | 三号 | `三号 (16pt)` |
| 一级标题 | 三号 | `三号 (16pt)` |
| 二级标题 | 三号 | `三号 (16pt)` |
| 三级标题 | 三号 | `三号 (16pt)` |
| 页码 | 四号 | `四号 (14pt)` |
| 版记（抄送/印发） | 四号 | `四号 (14pt)` |
| 附件说明 | 四号 | `四号 (14pt)` |

**硬编码常量定义**（供后续开发直接使用）：

```typescript
// 格式: [磅值, 中文字号名称]
const FONT_SIZE_PRESETS: [number, string][] = [
  [42,   '初号'],
  [36,   '小初'],
  [26,   '一号'],
  [24,   '小一'],
  [22,   '二号'],
  [18,   '小二'],
  [16,   '三号'],
  [15,   '小三'],
  [14,   '四号'],
  [12,   '小四'],
  [10.5, '五号'],
  [9,    '小五'],
  [7.5,  '六号'],
  [6.5,  '小六'],
  [5.5,  '七号'],
  [5,    '八号'],
];

// 强制格式: "三号 (16pt)"
function formatFontSizeLabel(pt: number): string {
  const preset = FONT_SIZE_PRESETS.find(([v]) => v === pt);
  return preset ? `${preset[1]} (${pt}pt)` : `${pt}pt`;
}
```

### 7.4 非标准磅值降级展示方案

当用户手动输入非标准值（如 15.5pt、20pt、17pt）时，有三种降级策略：

| 策略 | 展示效果 | 优点 | 缺点 | 推荐度 |
|------|----------|------|------|--------|
| **A: 仅显示 pt 值** | `15.5pt` | 简单准确 | 丢失中文号信息，用户不知道对应几号字 | ⭐⭐ |
| **B: 显示"自定义"标签** | `自定义 (15.5pt)` | 明确告知用户这是非标准值 | "自定义"三字占空间，下拉选项宽度不一致 | ⭐⭐⭐ |
| **C: 自动吸附最近标准字号** | `小三 (15pt)`（15.5pt → 吸附到 15pt） | 始终显示中文号；引导用户使用标准值 | 改变用户输入值，可能引起困惑；边界值吸附方向需定义 | ⭐⭐ |

### 7.5 推荐方案：A + B 混合

**具体规则**：

1. **标准值**（精确匹配 `FONT_SIZE_PRESETS` 中的磅值）→ 显示 `三号 (16pt)`
2. **非标准值** → 显示 `15.5pt`（仅 pt 值，不加"自定义"前缀）
3. **下拉选项**：只列出标准字号，不提供非标准选项
4. **手动输入**：`<input type="number">` 允许输入任意值，失焦后按上述规则展示
5. **提示信息**：输入框下方小字提示"常用：三号(16pt) 二号(22pt) 四号(14pt)"

**理由**：
- 不自动吸附（尊重用户意图）
- 不加"自定义"前缀（简洁）
- 下拉只列标准值（引导规范）
- 手动输入允许自由（灵活）

**UI 交互流程**：
```
┌─────────────────────────────────┐
│ 字号: [三号 (16pt)        ▼]   │  ← 下拉只列标准值
│       ┌───────────────────┐     │
│       │ 二号 (22pt)       │     │
│       │ 三号 (16pt) ←当前 │     │
│       │ 四号 (14pt)       │     │
│       │ 小四 (12pt)       │     │
│       │ ...               │     │
│       └───────────────────┘     │
│ 常用：三号(16pt) 二号(22pt)     │  ← 提示信息
└─────────────────────────────────┘

用户手动输入 15.5:
┌─────────────────────────────────┐
│ 字号: [15.5pt             ▼]   │  ← 非标准值仅显示 pt
│ 常用：三号(16pt) 二号(22pt)     │
└─────────────────────────────────┘
```

---

## 八、总结与推荐执行顺序

### 推荐执行顺序

```
Phase 1: 基础架构（2天）
  ├── 1.1 升级 useDocumentConfig — 新增 special/advanced/pageNumber 配置
  ├── 1.2 创建 gb-t-9704.ts 常量文件（字号标签、字体选项）
  └── 1.3 创建 A4PageRenderer 统一组件（CSS 变量 + mm 边距）

Phase 2: Module B 升级（2天）
  ├── 2.1 EnhancedA4Preview 重构 — 使用 A4PageRenderer
  ├── 2.2 样式面板重构 — 借鉴参考项目分组布局
  ├── 2.3 特殊选项/高级设置折叠面板
  └── 2.4 移除文本输入，改为纯预览+参数调整

Phase 3: Module A 新建（2天）
  ├── 3.1 MarkdownOptimize 页面 — 左编辑+右预览
  ├── 3.2 文档类型选择器（从模板 API 动态加载）
  ├── 3.3 轻量样式面板（P1 参数 + 折叠 P2/P3）
  └── 3.4 "发送到 A4 编排"跨页面数据传递

Phase 4: 增强功能（1天）
  ├── 4.1 盖章功能（CSS Overlay + 后端 python-docx 嵌入）
  ├── 4.2 关于页版本更新检测
  └── 4.3 全局字号标签统一
```

**总工期估算**: 7 个工作日

### 关键决策点（需用户确认）

1. **状态管理方案**：推荐方案 A（全局 Context），是否接受？
2. **"一键优化 Markdown"按钮**：推荐移除 + "发送到 A4 编排"，是否接受？
3. **盖章方案**：推荐 CSS Overlay + python-docx 混合，是否接受？
4. **左侧面板宽度**：320px，是否合适？
