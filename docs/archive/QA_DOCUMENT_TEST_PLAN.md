# 文档格式质量测试计划 (QA Document Test Plan)

> 版本：v1.0
> 最后更新：2026-06-23
> 参考标准：GB/T 9704-2012 党政机关公文格式

---

## 一、测试目标

确保 Document Engine 生成的 .docx 文件：
1. 在 Microsoft Word 中打开格式正确
2. 在 WPS Office 中打开格式正确
3. 不出现 MS Gothic / MS Mincho 等替代字体
4. 符合 GB/T 9704-2012 公文格式标准

---

## 二、测试维度

### 2.1 字体测试 (Font Tests)

| 编号 | 测试项 | 验收标准 | 自动化 |
|------|--------|----------|--------|
| F-01 | eastAsia 属性存在 | 所有 rFonts 元素都有 eastAsia | ✅ |
| F-02 | 无 MS Gothic | document.xml 中不含 MS Gothic/Mincho | ✅ |
| F-03 | 标题字体正确 | 标题 eastAsia = 方正小标宋简体 | ✅ |
| F-04 | 正文字体正确 | 正文 eastAsia = 仿宋_GB2312 | ✅ |
| F-05 | 西文字体正确 | ascii/hAnsi = Times New Roman | ✅ |
| F-06 | cs 属性存在 | 所有 rFonts 都有 cs 属性 | ✅ |
| F-07 | docDefaults 字体 | styles.xml 的 docDefaults 设置了 eastAsia | ✅ |

### 2.2 样式测试 (Style Tests)

| 编号 | 测试项 | 验收标准 | 自动化 |
|------|--------|----------|--------|
| S-01 | styles.xml 存在 | .docx 包含 word/styles.xml | ✅ |
| S-02 | docDefaults 存在 | styles.xml 包含 w:docDefaults | ✅ |
| S-03 | Normal 样式 | styles.xml 包含 Normal 样式定义 | ✅ |
| S-04 | 样式字体正确 | 样式的 rFonts 也设置了 eastAsia | ✅ |

### 2.3 段落格式测试 (Layout Tests)

| 编号 | 测试项 | 验收标准 | 自动化 |
|------|--------|----------|--------|
| L-01 | 标题居中 | 标题段落 jc = center | ✅ |
| L-02 | 正文两端对齐 | 正文段落 jc = both | ✅ |
| L-03 | 首行缩进 | 正文段落 firstLine = 640 (2字符) | ✅ |
| L-04 | 行距固定值 | 正文段落 lineRule = exact | ✅ |
| L-05 | 落款右对齐 | 落款段落 jc = right | ✅ |

### 2.4 页面设置测试 (Page Tests)

| 编号 | 测试项 | 验收标准 | 自动化 |
|------|--------|----------|--------|
| P-01 | A4 纸张 | 210mm × 297mm | ✅ |
| P-02 | 上边距 | 37mm ± 2mm | ✅ |
| P-03 | 下边距 | 35mm ± 2mm | ✅ |
| P-04 | 左边距 | 28mm ± 2mm | ✅ |
| P-05 | 右边距 | 26mm ± 2mm | ✅ |

### 2.5 生成完整性测试 (Generation Tests)

| 编号 | 测试项 | 验收标准 | 自动化 |
|------|--------|----------|--------|
| G-01 | 模板非空 | 文件大小 > 2KB | ✅ |
| G-02 | 内容保留 | 优化后文本不丢失 | ✅ |
| G-03 | Roundtrip | parse → generate → parse 文本一致 | ✅ |
| G-04 | Word 打开 | 在 Word 2016+ 中打开无报错 | 手动 |
| G-05 | WPS 打开 | 在 WPS 2019+ 中打开无报错 | 手动 |

---

## 三、测试样本

### 每种公文类型需要：

| 文件 | 说明 |
|------|------|
| `test_{type}_original.docx` | 原始（格式不规范）文档 |
| `test_{type}_optimized.docx` | 优化后文档 |
| `test_{type}_reference.docx` | 标准参考文档（人工确认） |

### 覆盖的公文类型：

1. 通知 (notice)
2. 请示 (request)
3. 报告 (report)
4. 函 (letter)
5. 会议纪要 (meeting)
6. 决定 (decision)
7. 通告 (announcement)
8. 公告 (notice_public)

---

## 四、自动化验证工具

### document_validator

位于 `backend/core/document/validator.py`

调用方式：
```python
from core.document.validator import validate_document
result = validate_document("path/to/file.docx")
print(result.to_dict())
```

输出格式：
```json
{
    "font_errors": 0,
    "style_errors": 0,
    "layout_errors": 0,
    "page_errors": 0,
    "fallback_fonts": [],
    "total_errors": 0,
    "passed": true,
    "details": []
}
```

### 验收标准

| 指标 | 标准 |
|------|------|
| 生成文件 Word 打开成功率 | 100% |
| 字体异常数 | 0 |
| fallback_fonts | [] |
| 样式错误 | 0 |
| 页面设置错误 | 0 |

---

## 五、测试执行记录

### 2026-06-23 首轮自动化测试

| 测试 | 结果 | 说明 |
|------|------|------|
| 8 种模板生成 | ✅ | 全部生成成功 |
| 字体 XML 验证 | ✅ | eastAsia 正确写入 |
| MS Gothic 排除 | ✅ | 无 MS 系列字体 |
| 页面设置 | ✅ | A4 + 正确页边距 |
| Roundtrip 一致性 | ✅ | 文本不丢失 |
| Word 打开测试 | 🟡 | 待人工验证 |
| WPS 打开测试 | 🟡 | 待人工验证 |

---

## 六、已知问题

1. **方正小标宋简体**：需要系统安装此字体，否则 Word 使用 SimSun 显示（不是 MS Gothic，可接受）
2. **.dotx 生成**：python-docx 不直接支持 .dotx，通过重命名实现（功能正常）

---

## 七、持续集成

未来可集成到 CI 流程：
```bash
cd backend
pytest tests/document/test_document_quality.py -v
```

测试覆盖 22 个自动化用例，覆盖 F-01~F-07、S-01~S-04、L-01~L-05、P-01~P-05、G-01~G-03。
