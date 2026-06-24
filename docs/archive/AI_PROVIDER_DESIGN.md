# AI Provider 设计文档

> 最后更新：2026-06-23

---

## 一、架构

```
AI Settings UI
  ↓
/api/ai/* endpoints
  ↓
ai/manager.py (registry + factory)
  ↓
ai/providers/*.py (具体实现)
```

## 二、支持的 Provider

| Provider | 类名 | 默认 Base URL | 默认模型 |
|----------|------|---------------|----------|
| openai | OpenAIProvider | https://api.openai.com/v1 | gpt-4o-mini |
| deepseek | DeepSeekProvider | https://api.deepseek.com/v1 | deepseek-chat |
| claude | ClaudeProvider | https://api.anthropic.com | claude-sonnet-4-20250514 |
| ollama | OllamaProvider | http://localhost:11434/v1 | qwen2.5:7b |
| custom | CustomProvider | (用户指定) | (用户指定) |

## 三、内置默认服务

```
Base URL: https://cpa.linhut.cn/v1
API Key:  加密存储，前端脱敏显示
Model:    gpt-4o-mini
```

当用户未配置任何 Provider 时，自动使用此默认服务。

## 四、API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/ai/providers` | GET | 列出可用 Provider + 默认配置 |
| `/api/ai/config` | POST | 保存配置（API Key 加密） |
| `/api/ai/config/{provider}` | GET | 获取配置（Key 脱敏） |
| `/api/ai/test` | POST | 测试连接（分类错误信息） |
| `/api/ai/models` | POST | 获取可用模型列表 |
| `/api/ai/default` | GET | 获取默认配置 |
| `/api/ai/analyze/{doc_id}` | POST | AI 分析文档 |

## 五、错误分类

| 错误类型 | error_type | 用户提示 |
|----------|------------|----------|
| 认证失败 | auth | API Key 无效或已过期 |
| 访问被拒 | permission | 访问被拒绝，请检查 API Key 权限 |
| 端点不存在 | endpoint | API 端点不存在，请检查 Base URL |
| 连接超时 | timeout | 连接超时，请检查网络或 Base URL |
| 网络不可达 | network | 无法连接到服务器 |
| 配置错误 | config | Provider 配置不正确 |

## 六、安全设计

- API Key 存储：Fernet 加密，存入 SQLite
- 前端显示：`sk-xxxx****xxxx` 脱敏
- 传输：仅 localhost，不暴露外部端口

## 七、AI 调用原则

**AI 禁止直接修改 .docx 文件。**

```
DocumentModel → AI 分析 → JSON 结果 → Modifier → Generator → .docx
```

AI 只负责分析和建议，修改由 Document Modifier 执行。
