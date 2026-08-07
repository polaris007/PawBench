# OpenClaw 5.28 partialArgs 问题分析报告

## 问题现象

5.28 的 transcript 文件中，`toolCall` 对象**同时包含 `arguments` 和 `partialArgs` 字段**：

```json
{
  "type": "toolCall",
  "name": "write",
  "arguments": {"path": "output.html"},
  "partialArgs": "{\"path\": \"output.html\"}"
}
```

而 4.14 的 transcript 中**只有 `arguments` 字段**，没有 `partialArgs`。

## 根本原因

### 5.28 代码 bug - 忘记删除 `partialArgs`

**位置**: `src/agents/openai-transport-stream.ts` 第 2511-2513 行

```typescript
// 5.28 的代码
if (currentBlock.type === "toolCall") {
  currentBlock.arguments = parseStreamingJson(currentBlock.partialArgs);
  // ❌ 缺少：delete currentBlock.partialArgs;
}
```

**对比 4.14 的正确实现**：

位置：`src/agents/openai-transport-stream.ts` 第 1034-1041 行

```typescript
// 4.14 的代码
if (currentBlock.type === "toolCall") {
  currentBlock.arguments = parseStreamingJson(currentBlock.partialArgs);
  const completed = {
    ...currentBlock,
    arguments: parseStreamingJson(currentBlock.partialArgs),
  };
  output.content[blockIndex()] = completed;  // ← 创建新对象，自然不包含 partialArgs
}
```

**4.14 通过创建新对象的方式隐式删除了 `partialArgs`，而 5.28 直接修改原对象但忘记删除。**

### 5.28 还有一处删除逻辑（但不完整）

位置：`src/llm/providers/openai-completions.ts` 第 438 行

```typescript
// 在 catch 块中
for (const block of output.content) {
  delete (block as { partialArgs?: string }).partialArgs;
}
```

但这**只在错误处理时执行**，正常流程不执行！

## 影响

### 1. Transcript 文件包含冗余字段

`partialArgs` 是流式解析时的临时缓冲区（scratch buffer），用于：
1. 累积流式 JSON 字符串片段
2. 解析为完整的 `arguments` 对象后就应该删除

5.28 没有删除它，导致 transcript 文件中包含冗余数据。

### 2. **不影响功能**

重要的是：`partialArgs` **不影响功能**，它只是：
- `arguments` 的 JSON 字符串表示
- 内容完全冗余
- 不会被 OpenClaw 使用

### 3. 与 write 失败无关

你观察到的 "write 操作没有 toolResult" 问题**不是由 `partialArgs` 引起的**。

write 失败的原因需要另外分析（可能是 LLM 输出被截断、网络超时等）。

## 修复建议

在 `src/agents/openai-transport-stream.ts` 的 `finishCurrentBlock` 函数中添加删除逻辑：

```typescript
if (currentBlock.type === "toolCall") {
  currentBlock.arguments = parseStreamingJson(currentBlock.partialArgs);
  delete currentBlock.partialArgs;  // ← 添加这行
}
```

同样需要在 `finishAllToolCallBlocks` 函数中添加：

```typescript
const finishAllToolCallBlocks = () => {
  for (const block of toolCallBlocksByIndex.values()) {
    block.arguments = parseStreamingJson(block.partialArgs);
    delete block.partialArgs;  // ← 添加这行
  }
};
```

## 验证

修复后，新的 transcript 文件应该不再包含 `partialArgs` 字段。

## 额外发现

### Write 成功率对比

| 版本 | write toolCalls | 成功 (有 toolResult) | 无响应 | 成功率 |
|:-----|:---------------:|:--------------------:|:------:|:------:|
| **5.28** | 173 | 15 | 5 | **8.7%** |
| **4.14** | 272 | 196 | 76 | **72.1%** |

**5.28 的 write 成功率显著低于 4.14**，这是另一个需要调查的问题。

### Write 无响应的可能原因

1. **LLM 输出被截断** - 模型生成到一半就停止了
2. **网络超时** - 请求 LLM 时超时
3. **Stream 提前结束** - 没有收到完整的 response

建议检查：
- 5.28 的 timeout 配置
- LLM 响应的完整性
- Stream handler 的错误处理