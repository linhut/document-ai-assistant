# Phase 5 开发计划

**阶段名称**：AI Integration（AI 集成）  
**预计时间**：2-3 天  
**目标**：集成多家 AI 服务，提供智能优化建议

---

## 🎯 目标

### 核心功能
1. **AI Provider 接口** - 统一的 AI 调用抽象
2. **多家 AI 支持** - OpenAI、DeepSeek、Claude、通义千问等
3. **错别字检测** - AI 辅助识别错别字
4. **表达优化** - AI 提供表达改进建议
5. **内容审查** - 检查逻辑性和完整性

---

## 📋 实施计划
注意AI功能和格式转换功能要分离，如果不进行AI的能力配置也要可用
### Step 1: AI Provider 基础架构（1 小时）
**文件**：
- `backend/ai/base.py` - 抽象基类（已存在）
- `backend/ai/manager.py` - Provider 管理器（已存在）

**任务**：
- [x] 检查现有架构
- [ ] 完善 BaseAIProvider 接口
- [ ] 实现 AIProviderManager

### Step 2: 实现 OpenAI Provider（30 分钟）
**文件**：`backend/ai/providers/openai_provider.py`

**功能**：
- [ ] 初始化 OpenAI 客户端
- [ ] 实现 analyze_document() 方法
- [ ] 实现 detect_typos() 方法
- [ ] 实现 suggest_improvements() 方法
- [ ] 错误处理和重试机制

### Step 3: 实现 DeepSeek Provider（30 分钟）
**文件**：`backend/ai/providers/deepseek_provider.py`

**功能**：
- [ ] 兼容 OpenAI API 格式
- [ ] 自定义 base_url
- [ ] 实现核心方法


### Step 4: 实现自定义 Provider（30 分钟）
**文件**：`backend/ai/providers/custom_provider.py`

**功能**：
- [ ] 支持任意兼容 OpenAI API 的服务
- [ ] 动态 base_url 和 model
- [ ] 灵活配置

### Step 5: API 集成（30 分钟）
**文件**：`backend/api/routes/ai.py`

**端点**：
- [ ] POST /api/ai/analyze - AI 分析文档
- [ ] POST /api/ai/detect-typos - 检测错别字
- [ ] POST /api/ai/suggest - 优化建议

### Step 6: 配置管理（30 分钟）
**文件**：
- `backend/services/ai_config_service.py`
- `backend/db/models.py` - AIConfig 表

**功能**：
- [ ] 保存 AI 配置
- [ ] 加密存储 API Key
- [ ] 配置验证

### Step 7: 前端集成（30 分钟）
**文件**：`frontend/src/pages/AISettings.tsx`

**功能**：
- [ ] 真实保存配置到后端
- [ ] 真实测试连接
- [ ] 自定义 API 获取模型列表

### Step 8: 测试（30 分钟）
**文件**：`tests/backend/test_ai_integration.py`

**测试**：
- [ ] AI Provider 单元测试
- [ ] API 端点测试
- [ ] 集成测试

---

## 🔧 技术设计

### AI Provider 接口
```python
class BaseAIProvider(ABC):
    @abstractmethod
    async def analyze_document(
        self, 
        content: str, 
        doc_type: str
    ) -> dict:
        """分析文档内容"""
        pass
    
    @abstractmethod
    async def detect_typos(
        self, 
        text: str
    ) -> list[dict]:
        """检测错别字"""
        pass
    
    @abstractmethod
    async def suggest_improvements(
        self, 
        text: str
    ) -> list[dict]:
        """提供优化建议"""
        pass
```

### Prompt 设计
```python
ANALYZE_PROMPT = """
你是一个公文格式专家。请分析以下{doc_type}文档，检查：
1. 格式规范性
2. 表达准确性
3. 逻辑完整性

文档内容：
{content}

请返回 JSON 格式的分析结果。
"""
```

---

## ⚠️ 注意事项

### 1. API Key 安全
- 使用 cryptography 加密存储
- 不在日志中输出
- 前端不暴露完整 Key

### 2. 成本控制
- 限制单次请求长度
- 实现请求缓存
- 用户配额管理

### 3. 错误处理
- 网络超时重试
- API 限流处理
- 降级方案（不影响核心功能）

---

## 📊 验收标准

### 功能验收
- [ ] 用户可以配置至少 3 种 AI Provider
- [ ] AI 分析返回有意义的建议
- [ ] 错别字检测准确率 > 80%
- [ ] API 响应时间 < 5 秒

### 质量验收
- [ ] 所有单元测试通过
- [ ] API 端点测试通过
- [ ] 错误处理完善
- [ ] 日志记录完整

---

## 🚀 开始 Phase 5

准备就绪！立即开始 AI Integration 开发。
