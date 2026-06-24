# API 测试指南

## ✅ 后端 API 正常工作

我已经测试过，后端 API 是正常工作的。

---

## 🧪 测试方法

### 方法 1：使用浏览器

在浏览器中直接访问以下地址：

```
✅ http://127.0.0.1:8765/api/health
✅ http://127.0.0.1:8765/api/documents/
✅ http://127.0.0.1:8765/docs (FastAPI 自动文档)
```

### 方法 2：使用命令行

```bash
# 健康检查
curl http://127.0.0.1:8765/api/health

# 文档列表
curl http://127.0.0.1:8765/api/documents/
```

---

## ⚠️ 常见错误

### 错误 1：404 Not Found

**原因**：路径不完整

❌ 错误：`http://127.0.0.1:8765/api/documents`  
✅ 正确：`http://127.0.0.1:8765/api/documents/` （注意最后的斜杠）

### 错误 2：连接被拒绝

**原因**：后端未启动

**解决**：
```bash
cd backend
python main.py
```

### 错误 3：CORS 错误

**原因**：前端从不同端口访问后端

**说明**：已配置 CORS，允许所有来源

---

## 📍 可用的 API 端点

### 1. 健康检查
```
GET http://127.0.0.1:8765/api/health
```

**响应**：
```json
{"status":"ok","version":"0.1.0"}
```

---

### 2. 文档列表
```
GET http://127.0.0.1:8765/api/documents/
```

**响应**：
```json
[
  {
    "id": 1,
    "filename": "test.docx",
    "file_path": "...",
    "document_type": "notice",
    "status": "uploaded",
    ...
  }
]
```

---

### 3. 上传文档
```
POST http://127.0.0.1:8765/api/documents/upload
Content-Type: multipart/form-data

file: [选择 .docx 文件]
```

---

### 4. 格式检查
```
POST http://127.0.0.1:8765/api/check/{doc_id}
Content-Type: application/json

{
  "document_type": "notice"
}
```

---

### 5. 获取检查结果
```
GET http://127.0.0.1:8765/api/check/{doc_id}/results
```

---

### 6. 一键优化
```
POST http://127.0.0.1:8765/api/optimize/{doc_id}
Content-Type: application/json

{
  "document_type": "notice",
  "apply_fixes": true
}
```

---

## 🔍 FastAPI 自动文档

访问：**http://127.0.0.1:8765/docs**

这里可以：
- 查看所有 API 端点
- 在线测试 API
- 查看请求/响应格式

---

## 🎯 前端如何调用

前端已经配置了 API 代理，会自动转发到后端：

```typescript
// 前端代码
import { apiClient } from '@/api/client';

// 调用示例
const documents = await apiClient.get('/api/documents/');
```

**Vite 配置的代理**：
```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8765',
      changeOrigin: true,
    },
  },
}
```

---

## ✅ 测试清单

- [ ] 访问 http://127.0.0.1:8765/api/health
- [ ] 访问 http://127.0.0.1:8765/api/documents/
- [ ] 访问 http://127.0.0.1:8765/docs
- [ ] 在 Swagger UI 中测试上传文档
- [ ] 前端页面能正常加载

---

## 🐛 如果仍然遇到问题

请提供以下信息：

1. **访问的完整 URL**
2. **浏览器返回的完整错误信息**
3. **后端控制台的日志输出**
4. **浏览器开发者工具的 Network 截图**

这样我可以精确定位问题！

---

## 💡 小贴士

1. **路径末尾的斜杠很重要**：`/api/documents/` vs `/api/documents`
2. **使用 FastAPI 文档测试**：http://127.0.0.1:8765/docs
3. **检查后端是否在运行**：`curl http://127.0.0.1:8765/api/health`
4. **查看详细日志**：后端控制台会显示所有请求

---

**当前测试结果**：
- ✅ 健康检查接口正常
- ✅ 文档列表接口正常
- ✅ 已有 2 条测试数据

如需帮助，请告诉我具体的错误信息！
