# OpenClaw 5.28 流式响应截断问题根本原因分析

## 问题确认

**5.28 的流式响应处理确实有 bug**，导致 LLM 输出被提前截断。

### 数据对比

| 指标 | 4.14 | 5.28 |
|:-----|:----:|:----:|
| **terminated 错误** | 76 | 0 |
| **timeout 错误** | 0 | 5 |
| **提前终止（无 toolResult）** | 2 | 38 |
| **write 成功率** | 72.1% | 8.7% |
| **正常结束 (toolUse/stop)** | 73 | 2 |

## 根本原因

### 1. 5.28 缺少 `terminated` 错误的重试机制

**4.14 的处理流程**：
```
LLM 返回 terminated → 捕获错误 → 自动重试 → 成功
```

示例（01_Productivity_Flow_task_6_calendar_scheduling）：
```
行 1: write 调用 → terminated 错误
  ↓
行 2: 重试 exec mkdir (成功)
  ↓  
行 3: 重试 write → terminated 错误
  ↓
行 4+: 继续重试直到成功
```

**5.28 的问题**：
- 没有 `terminated` 错误（0 次）
- 但流被提前截断（38 次）
- **没有错误捕获，没有重试**
- transcript 突然结束

### 2. 5.28 的 stream handler 有 bug

**位置**: `src/llm/providers/openai-completions.ts`

**问题 1**: `mapStopReason` 函数签名错误

```typescript
// 5.28 line 1108
function mapStopReason(reason: string): {...}  // ← reason 是 string，不是 string | null
```

但代码里有：
```typescript
// line 1112
if (reason === null) {  // ← 这个检查永远不会成立！
  return { stopReason: "stop" };
}
```

**当 LLM 返回 `finish_reason: null` 时**，TypeScript 会把 `null` 转成字符串 `"null"`，导致：
- `mapStopReason("null")` 进入 `default` 分支
- 返回 `{ stopReason: "error", errorMessage: "Provider finish_reason: null" }`
- **但实际上 5.28 连这个错误都没有捕获**

**问题 2**: `hasFinishReason` 检查不够严格

```typescript
// line 314-320
if (choice.finish_reason) {  // ← 只有 finish_reason 存在时才设置
  const finishReasonResult = mapStopReason(choice.finish_reason);
  output.stopReason = finishReasonResult.stopReason;
  hasFinishReason = true;  // ← 只有这里设置为 true
}

// line 428-430
if (!hasFinishReason) {
  throw new Error("Stream ended without finish_reason");
}
```

**问题**：如果流提前结束（网络问题、LLM 侧截断），`hasFinishReason` 是 `false`，会抛出错误。但这个错误被 catch 块捕获后：
```typescript
// line 434-450
} catch (error) {
  // 删除 partialArgs
  output.stopReason = "error";
  output.errorMessage = error.message;
  stream.push({ type: "error", ... });  // ← 发送错误事件
  stream.end();  // ← 结束流
  // ❌ 没有重试逻辑！
}
```

### 3. 4.14 的重试机制在哪里？

**4.14 的重试不在 stream handler 中，而在上层**：

位置：`src/agents/pi-embedded-runner/run/attempt.stop-reason-recovery.ts`

```typescript
// 检查是否需要重试
if (output.stopReason === "error" || output.stopReason === "terminated") {
  // 触发重试逻辑
  await retryTurn();
}
```

**5.28 缺少这个重试检查**，或者重试逻辑没有正确处理 `stream ended without finish_reason` 的情况。

## 验证方法

### 1. 检查 5.28 的重试逻辑

位置：`src/agents/embedded-agent-runner/run/attempt.stop-reason-recovery.ts`

对比 4.14 的相同文件，看是否有以下检查：
```typescript
if (message.stopReason === "error" && message.errorMessage?.includes("finish_reason")) {
  // 应该重试
}
```

### 2. 修复 mapStopReason 函数

```typescript
// 5.28 src/llm/providers/openai-completions.ts line 1108
function mapStopReason(reason: string | null): {  // ← 添加 | null
  stopReason: StopReason;
  errorMessage?: string;
} {
  if (reason === null || reason === "null") {  // ← 处理 null 和 "null"
    return { stopReason: "stop" };
  }
  // ...
}
```

### 3. 添加流提前结束的恢复逻辑

在 `stream ended without finish_reason` 错误时：
1. 记录详细的诊断信息
2. 触发自动重试
3. 或者至少保存已接收的部分数据

## 结论

**5.28 的流式响应处理确实有 bug**：

1. **类型签名错误**：`mapStopReason(reason: string)` 应该是 `(reason: string | null)`
2. **缺少重试机制**：stream handler 抛出错误后没有触发上层重试
3. **过早判断流结束**：可能在 LLM 还在生成时就关闭了连接

**建议优先检查**：
1. `src/agents/embedded-agent-runner/run/attempt.stop-reason-recovery.ts` - 重试逻辑
2. `src/llm/providers/openai-completions.ts` - mapStopReason 函数
3. `src/agents/openai-transport-stream.ts` - 对比 4.14 的相同文件