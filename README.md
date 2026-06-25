# AI 公文智能优化助手

<p align="center">
  <img src="https://img.shields.io/badge/AI-Document-orange?style=for-the-badge&logo=robot&logoColor=white" alt="AI Document">
  <img src="https://img.shields.io/badge/公文-GB%2FT%209704-blue?style=for-the-badge&logo=microsoftword&logoColor=white" alt="GB/T 9704">
</p>

<p align="center">
  <strong>Official Document AI Assistant</strong><br>
  基于 GB/T 9704 标准的公文格式智能检测与优化桌面应用
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.5-blue" alt="version">
  <img src="https://img.shields.io/badge/python-3.12+-green" alt="python">
  <img src="https://img.shields.io/badge/node-20+-green" alt="node">
  <img src="https://img.shields.io/badge/electron-35-blue" alt="electron">
  <img src="https://img.shields.io/badge/license-MIT-brightgreen" alt="license">
  <img src="https://img.shields.io/badge/tests-39%20passed-brightgreen" alt="tests">
  <img src="https://img.shields.io/github/stars/linhut/document-ai-assistant?style=social" alt="stars">
  <img src="https://img.shields.io/github/forks/linhut/document-ai-assistant?style=social" alt="forks">
</p>

<p align="center">
  <a href="#功能界面">功能界面</a> ·
  <a href="#功能特性">功能特性</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="#技术架构">技术架构</a> ·
  <a href="#ai-配置">AI 配置</a> ·
  <a href="#项目结构">项目结构</a> ·
  <a href="#开发日志">开发日志</a>
</p>
 
---

## 🖥 功能界面

<table>
  <tr>
    <td align="center"><b>工作台</b></td>
    <td align="center"><b>文档处理</b></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/617ad742-75a6-4a98-938b-cb27819fb1d9" alt="工作台" width="400"></td>
    <td><img src="https://github.com/user-attachments/assets/0cda25cd-707c-475c-b265-905b41984e43" alt="文档处理" width="400"></td>
  </tr>
  <tr>
    <td align="center"><b>校审中心</b></td>
    <td align="center"><b>模板中心</b></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/17b4843a-a74b-471a-bb50-a19b754eb47b" alt="校审中心" width="400"></td>
    <td><img src="https://github.com/user-attachments/assets/b98a7681-06c0-4ef9-b91d-fc6d7b2baa65" alt="模板中心" width="400"></td>
  </tr>
  <tr>
    <td align="center"><b>AI 配置</b></td>
    <td align="center"><b>关于</b></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/d18e8bf0-1c3d-4ace-a5bb-22c8f57aade7" alt="AI 配置" width="400"></td>
    <td>
      <img src="https://github.com/user-attachments/assets/11131fc8-13fc-4ba5-b41b-49d692a4e46a" alt="关于" width="400"><br>
      <img src="https://github.com/user-attachments/assets/28c057e1-fd2a-4352-9d08-38f7ea8e9b59" alt="关于-详情" width="400">
    </td>
  </tr>
</table>

---

## 📋 功能特性

- **格式检测** — 依据 GB/T 9704 标准自动检查公文格式（字体、字号、缩进、行距、页边距等），190 条检查规则
- **智能修复** — 一键自动修复格式问题，180 条修复规则，生成优化后的 .docx 文档
- **AI 深度分析** — 接入大模型进行语义级分析，按 22 种文种定制检查规则，发现规则引擎无法识别的问题
- **22 种文种** — 支持通知、报告、请示、会议纪要、决定、决议、函、通报等全部法定公文文种
- **多 AI 服务商** — 支持 DeepSeek、通义千问、智谱、Moonshot、MiniMax、腾讯混元、豆包等 23+ 服务商
- **AI 建议应用** — AI 发现的问题可勾选后一键应用到文档
- **模板管理** — 内置官方模板 + 自定义模板，支持三级优先级合并
- **本地运行** — 数据不离开本机，API Key 加密存储

---


### 方式一：一键启动（Windows）

双击 `启动应用.bat`，自动安装依赖并启动。

### 方式二：手动启动

```bash
# 1. 克隆仓库
git clone https://github.com/linhut/document-ai-assistant.git
cd document-ai-assistant

# 2. 启动后端
cd backend
pip install -r requirements.txt
python main.py

# 3. 启动前端（新终端）
cd frontend
npm install
npm run electron:dev
```

### 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | >= 3.12 | [下载地址](https://python.org) |
| Node.js | >= 20 | [下载地址](https://nodejs.org) |

### 构建桌面安装包

```bash
cd frontend
npm run electron:build:preview
# 输出: frontend/release/*.exe
```

---

## 🏗 技术架构

```
Electron Shell
  ├── React 19 + TypeScript + Vite + TailwindCSS + Radix UI
  └── FastAPI Backend (Python 3.12+)
        ├── Document Pipeline: Parse → Check → Fix → Generate
        ├── Rule Engine: 190 条检查 + 180 条修复 (YAML 配置)
        ├── AI Provider: 23+ 服务商 (Strategy 模式)
        └── SQLite: 文档、检查结果、AI 配置（加密存储）
```

| 类别 | 技术 |
|------|------|
| 前端框架 | React 19 + TypeScript + Vite |
| UI 组件 | Radix UI + TailwindCSS |
| 桌面壳 | Electron 35 |
| 后端框架 | FastAPI (Python 3.12+) |
| 文档处理 | python-docx |
| 数据存储 | SQLite + SQLAlchemy |
| AI 接入 | OpenAI 兼容协议 (Strategy 模式) |

---

## 🤖 AI 配置

在应用内「AI 配置」页面选择服务商并填入 API Key，支持：

| 服务商 | 默认模型 | 说明 |
|---|---|---|
| DeepSeek | deepseek-chat | 国产首选，性价比高 |
| 阿里云百炼 | qwen-turbo | 通义千问系列 |
| 智谱 AI | glm-4-flash | GLM 系列 |
| Moonshot | moonshot-v1-8k | Kimi 长上下文 |
| 豆包 / 火山方舟 | doubao-1.5-pro | 字节跳动 |
| MiniMax | MiniMax-Text-01 | 海螺 AI |
| 腾讯混元 | hunyuan-lite | 腾讯 |
| OpenRouter | openai/gpt-4o-mini | 聚合 100+ 模型 |
| Ollama | qwen2.5:7b | 本地模型，无需联网 |
| 自定义 | — | 任意 OpenAI 兼容接口 |

---

## 📂 项目结构

```
├── backend/                 # Python 后端
│   ├── api/routes/          # FastAPI 路由
│   ├── core/document/       # 文档处理（解析、生成、修改）
│   ├── core/rules/          # 规则引擎（加载、检查、修复）
│   ├── ai/                  # AI Provider 架构
│   └── db/                  # 数据模型
├── frontend/                # Electron + React 前端
│   ├── electron/            # Electron 主进程
│   └── src/                 # React 应用
├── rules/official/          # 22 种文种 YAML 规则
├── templates/               # 公文模板
├── tests/                   # 39 个自动化测试
└── docs/                    # 文档
```

---

## 📊 与同类工具对比

| 维度 | 本项目 | AIPoliDoc | 小恐龙公文助手 |
|---|---|---|---|
| AI 分析 | ✅ 23+ 服务商 | ✅ 仅 DeepSeek | ❌ 无 |
| 规则检查 | ✅ 190 条规则 | ❌ 无 | ❌ 无 |
| 文种覆盖 | 22 种法定文种 | 学术论文为主 | 通用公文 |
| 独立运行 | ✅ 桌面应用 | ✅ 桌面应用 | ❌ 需 Word |
| 开源 | ✅ MIT | ✅ MIT | ❌ 闭源 |
| 自动修复 | ✅ 180 条修复规则 | ❌ | ✅ 格式化 |
| AI 建议应用 | ✅ 勾选应用 | ❌ | ❌ |
| 测试覆盖 | ✅ 39 个测试 | ❌ | ❌ |

---

## ❓ FAQ

**Q: 启动后提示"无法连接到后端服务"？**
A: 确认后端已运行（终端显示 `Uvicorn running on http://127.0.0.1:8765`）。如果端口被占用，运行 `python main.py --force`。

**Q: AI 分析报错 429（限流）？**
A: API 请求频率超限，系统会自动重试（最多 5 次）。等待 1-2 分钟后重试，或切换到其他 AI 服务商。

**Q: 优化后的文档字体不对？**
A: 请确保系统安装了公文字体（仿宋_GB2312、黑体、楷体_GB2312、方正小标宋简体）。TTF 目录下有字体文件，双击安装即可。

**Q: 如何添加自定义规则？**
A: 在「规则管理」页面可以查看和编辑规则。自定义规则保存在 `data/user_rules/`，优先级高于官方规则。

**Q: 支持 .doc 格式吗？**
A: 目前仅支持 .docx 格式。.doc 文件请先用 Word 另存为 .docx。

---

## 📝 开发日志

详见 [CHANGELOG.md](./CHANGELOG.md)

---

## 📄 许可证

[MIT License](./LICENSE)
