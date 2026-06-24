# AI 公文智能优化助手

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
</p>

---

## 功能特性

- **格式检测** — 依据 GB/T 9704 标准自动检查公文格式（字体、字号、缩进、行距、页边距等）
- **智能修复** — 一键自动修复格式问题，生成优化后的 .docx 文档
- **AI 深度分析** — 接入大模型进行语义级分析，发现规则引擎无法识别的问题
- **22 种文种** — 支持通知、报告、请示、会议纪要、决定、决议等全部法定公文文种
- **多 AI 服务商** — 支持 DeepSeek、通义千问、智谱、Moonshot、MiniMax、腾讯混元、豆包等 23+ 服务商
- **模板管理** — 内置官方模板 + 自定义模板，支持三级优先级合并
- **本地运行** — 数据不离开本机，API Key 加密存储

## 技术架构

```
Electron Shell
  ├── React 19 + TypeScript + Vite + TailwindCSS
  └── FastAPI Backend (Python 3.12+)
        ├── Document Pipeline: Parse → Check → Fix → Generate
        ├── Rule Engine: YAML rules (3-tier merge: official < custom < user)
        ├── AI Provider: Strategy pattern (OpenAI/Claude/Custom compatible)
        └── SQLite: documents, check results, AI configs
```
## 功能界面

### 工作台
<img width="1681" height="1082" alt="image" src="https://github.com/user-attachments/assets/617ad742-75a6-4a98-938b-cb27819fb1d9" />

### 文档处理
<img width="1681" height="1082" alt="image" src="https://github.com/user-attachments/assets/0cda25cd-707c-475c-b265-905b41984e43" />

### 校审中心
<img width="1681" height="1082" alt="image" src="https://github.com/user-attachments/assets/17b4843a-a74b-471a-bb50-a19b754eb47b" />

### 模板中心
<img width="1681" height="1082" alt="image" src="https://github.com/user-attachments/assets/b98a7681-06c0-4ef9-b91d-fc6d7b2baa65" />

### AI配置
<img width="1681" height="1082" alt="image" src="https://github.com/user-attachments/assets/d18e8bf0-1c3d-4ace-a5bb-22c8f57aade7" />

### 关于
<img width="1681" height="1082" alt="image" src="https://github.com/user-attachments/assets/11131fc8-13fc-4ba5-b41b-49d692a4e46a" />
<img width="1681" height="1082" alt="image" src="https://github.com/user-attachments/assets/28c057e1-fd2a-4352-9d08-38f7ea8e9b59" />


## 快速开始

### 环境要求

- Node.js >= 20
- Python >= 3.12

### 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/document-ai-assistant.git
cd document-ai-assistant

# 2. 启动后端
cd backend
pip install -r requirements.txt
python main.py
# 后端运行在 http://127.0.0.1:8765

# 3. 启动前端（新终端）
cd frontend
npm install
npm run electron:dev
```

### 构建桌面应用

```bash
cd frontend
npm run electron:build:preview
# 输出: frontend/release/*.exe (NSIS 安装包)
```

## 项目结构

```
├── backend/                 # Python 后端
│   ├── api/routes/          # FastAPI 路由 (documents, check, optimize, ai, rules)
│   ├── core/document/       # 文档处理核心 (parser, generator, modifier)
│   ├── core/rules/          # 规则引擎 (loader, checker, fixer, engine)
│   ├── ai/                  # AI Provider 架构
│   ├── db/                  # SQLAlchemy 数据模型
│   └── services/            # 业务逻辑层
├── frontend/                # Electron + React 前端
│   ├── electron/            # Electron 主进程 + preload
│   ├── src/pages/           # 页面组件
│   ├── src/components/ui/   # Radix UI 基础组件
│   └── src/api/             # API 客户端
├── rules/official/          # 22 种文种 YAML 规则文件
├── templates/               # 官方公文模板
├── TTF/                     # 公文字体文件
└── tests/                   # 测试用例
```

## AI 配置

在应用内「AI 配置」页面选择服务商并填入 API Key，支持：

| 服务商 | 说明 |
|---|---|
| DeepSeek | deepseek-chat / deepseek-v3 |
| 阿里云百炼 | qwen-turbo / qwen-max |
| 智谱 AI | glm-4-flash / glm-4 |
| Moonshot | moonshot-v1-8k / moonshot-v1-128k |
| 豆包 / 火山方舟 | doubao 系列 |
| OpenRouter | 聚合 100+ 模型 |
| Ollama | 本地模型 |
| 自定义 | 任意 OpenAI 兼容接口 |

## 开发日志

详见 [CHANGELOG.md](./CHANGELOG.md)

## 许可证

[MIT License](./LICENSE)
