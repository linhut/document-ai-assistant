# WPS / Word 插件开发规划

> 版本：v2.0
> 更新时间：2026-06-23
> 项目：AI 公文智能优化助手

---

## 一、架构总览

```
┌─────────────────────────────────────────────────────┐
│                    用户界面层                          │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐ │
│  │ Word插件  │  │ WPS插件   │  │ Electron桌面端     │ │
│  └────┬─────┘  └────┬─────┘  └────────┬───────────┘ │
│       │              │                 │              │
│  ┌────┴──────────────┴─────────────────┴───────────┐ │
│  │         Office Bridge API (localhost:8765)       │ │
│  │              /api/office/*                       │ │
│  └────────────────────┬────────────────────────────┘ │
├───────────────────────┼──────────────────────────────┤
│                    核心引擎层                          │
│  ┌────────────────────┴────────────────────────────┐ │
│  │           Python Core Engine (唯一)              │ │
│  │  Document Engine │ Rule Engine │ AI Provider     │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

**核心原则：插件不包含业务逻辑，全部复用 Core Engine。**

---

## 二、Office Bridge API（已完成）

后端已实现 `/api/office/*` 端点：

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/office/health` | GET | 健康检查 |
| `/api/office/check` | POST | 检查文档（接收 base64） |
| `/api/office/fix` | POST | 一键修复（返回 base64） |
| `/api/office/ai-optimize` | POST | AI 优化 |
| `/api/office/templates` | GET | 获取模板列表 |
| `/api/office/apply-template` | POST | 应用模板样式 |
| `/api/office/generate-template` | POST | 生成 .docx/.dotx |

插件只需 HTTP 调用，无需实现任何规则或文档处理逻辑。

---

## 三、WPS 插件方案

### 3.1 技术栈

| 技术 | 用途 |
|------|------|
| WPS JS API | 插件接口 |
| JavaScript | 插件逻辑 |
| HTML/CSS | 侧边栏 UI |

### 3.2 插件结构

```
office-plugin/wps/
├── manifest.xml          # 插件声明
├── index.html            # 侧边栏入口
├── js/
│   ├── app.js            # 主逻辑
│   ├── api.js            # Bridge API 调用
│   └── wps-adapter.js    # WPS API 适配
├── css/
│   └── style.css
└── icons/
```

### 3.3 核心功能

| 功能 | WPS API | Bridge API |
|------|---------|------------|
| 读取当前文档 | `wps.ActiveDocument` | — |
| 发送检查 | — | `POST /api/office/check` |
| 显示结果 | TaskPane UI | JSON |
| 应用修复 | `wps.ActiveDocument` | `POST /api/office/fix` |
| 插入模板 | `wps.ActiveDocument.Range` | `GET /api/office/templates` |

### 3.4 关键代码示例

```javascript
// api.js — Bridge API 封装
const BRIDGE_URL = 'http://127.0.0.1:8765/api/office';

async function checkDocument(docBase64, docType) {
  const resp = await fetch(`${BRIDGE_URL}/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      document_base64: docBase64,
      document_type: docType,
    }),
  });
  return resp.json();
}

async function fixDocument(docBase64, docType) {
  const resp = await fetch(`${BRIDGE_URL}/fix`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      document_base64: docBase64,
      document_type: docType,
    }),
  });
  return resp.json(); // { document_base64, fixes_applied }
}
```

### 3.5 文档读写适配

```javascript
// wps-adapter.js
function getActiveDocumentBase64() {
  // WPS 方式获取文档二进制
  const doc = wps.ActiveDocument;
  const tempPath = doc.FullName;
  // 通过 WPS API 导出为 base64
  // 具体实现取决于 WPS JS API 版本
  return base64Content;
}

function applyFixedDocument(base64Content) {
  // 将修复后的文档写回
  // 可以新建文档或替换当前内容
}
```

---

## 四、Word Add-in 方案

### 4.1 技术栈

| 技术 | 用途 |
|------|------|
| Office.js | Word Add-in API |
| React | Task Pane UI |
| manifest.xml | Add-in 声明 |

### 4.2 插件结构

```
office-plugin/word/
├── manifest.xml
├── taskpane/
│   ├── index.html
│   ├── app.js
│   └── api.js
└── icons/
```

### 4.3 manifest.xml 要点

```xml
<OfficeApp xmlns="http://schemas.microsoft.com/office/appforoffice/1.1"
           xsi:type="TaskPaneApp">
  <Id>GUID</Id>
  <Version>1.0.0</Version>
  <ProviderName>AI公文助手</ProviderName>
  <DefaultLocale>zh-CN</DefaultLocale>
  <DisplayName DefaultValue="AI 公文智能优化助手"/>
  <Description DefaultValue="公文格式检查与优化"/>
  <Hosts>
    <Host Name="Document"/>
  </Hosts>
  <Requirements>
    <Sets>
      <Set Name="WordApi" MinVersion="1.3"/>
    </Sets>
  </Requirements>
</OfficeApp>
```

---

## 五、VBA 脚本方案（轻量级备选）

参考 `xkonglong/gw` 项目的 VBA 思路，提供一个不依赖插件的轻量方案：

```vba
' 公文格式化 VBA 脚本（示例）
Sub FormatOfficialDocument()
    ' 设置标题字体
    With Selection.Paragraphs(1).Range.Font
        .NameFarEast = "方正小标宋简体"
        .NameAscii = "Times New Roman"
        .Name = "Times New Roman"
        .Size = 22
    End With

    ' 设置正文格式
    ' ...

    MsgBox "格式化完成"
End Sub
```

可将 VBA 脚本作为模板的一部分提供，用户导入后即可使用。

---

## 六、开发路线

| 阶段 | 内容 | 周期 | 状态 |
|------|------|------|------|
| Phase 0 | Office Bridge API | — | ✅ 已完成 |
| Phase 1 | WPS 插件骨架 + 健康检查 | 1 周 | 📋 规划中 |
| Phase 2 | WPS 检查/修复功能 | 2 周 | 📋 规划中 |
| Phase 3 | Word Add-in 基础 | 2 周 | 📋 规划中 |
| Phase 4 | 测试 + 发布 | 1 周 | 📋 规划中 |

---

## 七、前置条件

| 条件 | 说明 |
|------|------|
| WPS 开发者账号 | 需注册 https://open.wps.cn |
| Office 365 开发者 | 可选，用于 Word Add-in |
| 本地服务运行 | 插件依赖 localhost:8765 |
| 字体安装 | 方正小标宋简体、仿宋_GB2312 |
