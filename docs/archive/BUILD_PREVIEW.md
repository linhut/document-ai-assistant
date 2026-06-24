# Preview EXE 构建指南

> 版本：v1.4.0-rc1
> 构建时间：2026-06-23

---

## 构建环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Node.js | 18+ | 前端构建 |
| npm | 9+ | 包管理 |
| Python | 3.10+ | 后端运行时 |
| Windows | 10/11 | 目标平台 |

## 构建步骤

### 1. 安装前端依赖

```bash
cd frontend
npm install
```

### 2. 安装后端 Python 依赖

```bash
cd backend
pip install -r requirements.txt
# 或
pip install fastapi uvicorn python-docx pydantic pyyaml sqlalchemy httpx aiofiles python-multipart cryptography
```

### 3. 构建 Preview EXE

```bash
cd frontend
npm run electron:build:preview
```

输出位置：`frontend/release/`

### 4. 手动运行（开发模式）

```bash
# 终端1：启动后端
cd backend
python main.py

# 终端2：启动 Electron 开发模式
cd frontend
npm run electron:dev
```

---

## 已知限制

1. **Python 依赖**：打包时 Python 依赖不会自动包含，用户需安装 Python 和依赖包
2. **字体**：方正小标宋简体需要系统安装，否则回退到 SimSun
3. **.dotx**：通过重命名 .docx 生成，功能正常但非标准方式
4. **AI 功能**：需要网络连接或本地 Ollama 服务

---

## 运行方式

1. 确保 Python 3.10+ 已安装并在 PATH 中
2. 确保后端依赖已安装
3. 运行 EXE 文件
4. 应用将自动启动 Python 后端并加载前端界面

---

## 文件结构

```
release/
├── AI公文智能优化助手 Setup 1.0.0.exe  # 安装包
├── win-unpacked/                        # 解压版本
│   ├── AI公文智能优化助手.exe
│   ├── resources/
│   │   ├── backend/                     # Python 后端
│   │   └── dist/                        # 前端静态文件
│   └── ...
└── ...
```

## 附带字体

项目 `TTF/` 目录包含公文标准字体：

| 字体文件 | 用途 |
|----------|------|
| `方正小标宋简.TTF` | 公文标题 |
| `仿宋_GB2312.ttf` | 公文正文 |
| `楷体_GB2312.TTF` | 公文小标题 |

**重要**：目标机器需安装这些字体，否则 Word 使用回退字体（SimSun，非 MS Gothic，可接受）。

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 后端启动超时 | 检查 Python 是否安装：`python --version` |
| 端口 8765 被占用 | 关闭占用进程或修改 `backend/config.py` 中的端口 |
| 页面空白 | 检查日志：`%APPDATA%/ai-doc-assistant/logs/electron.log` |
| 字体显示异常 | 安装方正小标宋简体、仿宋_GB2312 字体 |
