# RC1 执行计划

> 版本：v1.4.0-rc1
> 执行时间：2026-06-23

---

## 修复项清单

| # | 问题 | 优先级 | 文件 | 修复内容 | 状态 |
|---|------|--------|------|----------|------|
| 1 | Electron preload路径错误 | P0 | `electron/main.ts` | 修正 `__dirname/preload.js` 路径，添加日志和错误处理 | ✅ |
| 2 | API地址硬编码 | P0 | `api/client.ts` | 统一封装，支持 Electron/开发/生产三种模式 | ✅ |
| 3 | CheckCenter硬编码URL | P0 | `CheckCenter.tsx` | 改用 `downloadFile()` 辅助函数 | ✅ |
| 4 | Templates硬编码URL | P0 | `Templates.tsx` | 3处fetch改用 `downloadFile()` | ✅ |
| 5 | AI设置缺Provider | P1 | `AISettings.tsx` | 添加 Claude/Ollama + 获取模型按钮 | ✅ |
| 6 | Sidebar版本过时 | P1 | `Sidebar.tsx` | v1.1.0 → v1.4.0 | ✅ |
| 7 | 后端API版本过时 | P1 | `main.py` | 0.1.0 → 1.4.0 | ✅ |
| 8 | 默认AI配置 | P1 | `AISettings.tsx` | 默认地址改为 cpa.linhut.cn | ✅ |
| 9 | Electron构建脚本 | P1 | `package.json` | 添加 `electron:build:preview` | ✅ |

## 测试项清单

| # | 测试 | 方法 | 状态 |
|---|------|------|------|
| 1 | 后端启动 | `python backend/main.py` | 待执行 |
| 2 | 前端构建 | `cd frontend && npm run build` | 待执行 |
| 3 | Electron TS编译 | `npm run electron:compile` | 待执行 |
| 4 | API连通性 | 访问 /api/health | 待执行 |
| 5 | 文档上传+检查 | 前端操作 | 待执行 |
| 6 | 模板下载 | 前端操作 | 待执行 |
| 7 | AI配置 | 前端操作 | 待执行 |
| 8 | 文档质量验证 | validator.py | 待执行 |

## 风险项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Python未安装 | Electron无法启动后端 | main.ts 添加错误提示 |
| 端口8765被占用 | 后端启动失败 | 检测+错误提示 |
| electron-builder版本 | 打包可能失败 | 使用 --publish=never |
| 字体缺失 | 文档显示异常 | font_utils 有回退机制 |

## 构建流程

```
1. cd frontend
2. npm install
3. npm run electron:build:preview
4. 输出：frontend/release/AI公文智能优化助手 Setup 1.0.0.exe
```
