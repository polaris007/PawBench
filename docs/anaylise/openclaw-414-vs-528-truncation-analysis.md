# OpenClaw 4.14 vs 5.28 LLM 回复截断分析

## 1. 截断发生的位置

### 4.14 的 partialArgs 分布
- 总计：123 次 partialArgs / 10,023 toolCalls = **1.23%**
- 主要发生在：write toolCall (占绝大多数)

### 5.28 的 partialArgs 分布
- 总计：979 次 partialArgs / 5,665 toolCalls = **17.28%**
- 发生在各种 toolCall 类型：read, exec, write, update_plan, web_fetch 等

## 2. 截断模式分析

### 关键发现
1. **5.28 的截断发生在所有 toolCall 类型**，不仅仅是 write
2. **4.14 的截断主要发生在 write**，其他工具类型很少
3. **5.28 截断频率是 4.14 的 14 倍** (17.28% vs 1.23%)

### stopReason 分析
从日志看，partialArgs 出现时：
- stopReason 通常是 "toolUse"（正常工具调用完成）
- 但 args 被截断了，说明 LLM 输出流在传输过程中被截断

## 3. 具体任务对比 (3 个示例)

### 任务 1: simpo-code-reproduction
**5.28 文件位置**: 
  `D:\WorkPlace\github\PawBench\evalresults\result-0722\20260722_191110\pawbench\qwen35-397b-vision-nothink\oc-528-22-1\transcripts\simpo-code-reproduction.jsonl`

**4.14 文件位置**: 
  `D:\WorkPlace\github\PawBench\evalresults\result-0722\20260722_171744\pawbench\qwen35-397b-vision-nothink\oc-414-22-1\transcripts\simpo-code-reproduction.jsonl`

**对比**:
- 5.28: 108 行，49 次 partialArgs (45.4%)
- 4.14: 74 行，0 次 partialArgs (0%)
- 截断工具：update_plan, read, web_fetch

**截断示例 (5.28 行 2)**:
```json
{
  "toolCall": {
    "toolName": "update_plan",
    "arguments": {"plan": [...]},
    "partialArgs": "{\"plan\": [{\"step\": \"Explore project structure..."
  }
}
```

---

### 任务 2: manufacturing-equipment-maintenance
**5.28 文件位置**: 
  `D:\WorkPlace\github\PawBench\evalresults\result-0722\20260722_191110\pawbench\qwen35-397b-vision-nothink\oc-528-22-1\transcripts\manufacturing-equipment-maintenance.jsonl`

**4.14 文件位置**: 
  `D:\WorkPlace\github\PawBench\evalresults\result-0722\20260722_171744\pawbench\qwen35-397b-vision-nothink\oc-414-22-1\transcripts\manufacturing-equipment-maintenance.jsonl`

**对比**:
- 5.28: 65 行，30 次 partialArgs (46.2%)
- 4.14: 68 行，1 次 partialArgs (1.5%)
- 截断工具：exec, read

**截断示例 (5.28 行 5)**:
```json
{
  "toolCall": {
    "toolName": "exec",
    "arguments": {"command": "cd /app/working/workspaces/default/data && python3 -c \"import PyPDF2; pdf = PyPDF2.PdfReader('handbook.pdf'); text = '\\n'.join([page.extract_text() for page in pdf.pages]); print(text)"},
    "partialArgs": "{\"command\": \"cd /app/working/workspaces/default/data && python3 -c \\\"import PyPDF2; pdf = PyPDF2.PdfReader('handbook.pdf'); text = '\\\\n'.join([page.ex"
  }
}
```

---

### 任务 3: M075_doc_extraction_spatial_leaderboard
**5.28 文件位置**: 
  `D:\WorkPlace\github\PawBench\evalresults\result-0722\20260722_191110\pawbench\qwen35-397b-vision-nothink\oc-528-22-1\transcripts\M075_doc_extraction_spatial_leaderboard.jsonl`

**4.14 文件位置**: 
  `D:\WorkPlace\github\PawBench\evalresults\result-0722\20260722_171744\pawbench\qwen35-397b-vision-nothink\oc-414-22-1\transcripts\M075_doc_extraction_spatial_leaderboard.jsonl`

**对比**:
- 5.28: 55 行，26 次 partialArgs (47.3%)
- 4.14: 37 行，0 次 partialArgs (0%)
- 截断工具：read, exec

**截断示例 (5.28 行 2)**:
```json
{
  "toolCall": {
    "toolName": "read",
    "arguments": {"path": "fixtures/2512.17495v2.pdf"},
    "partialArgs": "{\"path\": \"fixtures/2512.17495v2.pdf\""
  }
}
```

---

## 4. 截断的 args 内容特征

所有 partialArgs 都是**完整的 JSON 对象被截断**，例如：
- 完整：`{"path": "file.txt", "offset": 100}`
- 截断：`{"path": "file.txt", "off`

**截断点特征**:
- 总是在 JSON 字符串中间截断
- 没有完整的闭合括号
- args 对象被截断，但 toolCall 仍然被提交

## 5. 结论

### 截断发生在哪里？
1. **LLM 输出流生成阶段** - 在 openclaw 接收到完整响应之前
2. **影响所有 toolCall 类型** - 不只是 write，包括 read, exec, update_plan, web_fetch
3. **5.28 的流式响应机制有问题** - 比 4.14 更容易丢失数据

### 为什么 5.28 更严重？
- 5.28 可能有**更激进的超时机制**或**更小的缓冲区**
- 5.28 的**流式解析逻辑有缺陷**，导致数据包丢失
- 5.28 的**网络请求处理**可能有问题（长响应被截断）

### 建议调查方向
1. 检查 openclaw 5.28 的**HTTP 客户端超时设置**
2. 检查**流式响应缓冲区大小**
3. 检查**LLM API 调用的重试逻辑**
4. 对比 4.14 和 5.28 的**网络请求/响应处理代码差异**