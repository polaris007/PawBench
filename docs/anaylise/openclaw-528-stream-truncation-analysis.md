# OpenClaw 5.28 LLM 输出提前终止问题分析

## 问题现象

5.28 的 transcript 文件中，大量 assistant 消息**没有正常结束**：

| 指标 | 4.14 | 5.28 |
|:-----|:----:|:----:|
| **正常结束 (toolUse/stop)** | 73 | 2 |
| **提前终止 (有 toolCall 但无 toolResult)** | 2 | **38** |
| **超时错误** | 0 | 5 |
| **其他错误** | 18 | 1 |

**5.28 有 38 次提前终止，而 4.14 只有 2 次！**

## 根本原因

### 1. LLM 输出流被截断

**关键证据**：

示例任务：`03_Social_Interaction_task_1_meeting_negotiation`

**5.28 transcript**: 7 行
**4.14 transcript**: 11 行

5.28 的最后一条消息：
```json
{
  "role": "assistant",
  "content": [
    {"type": "toolCall", "name": "write", "arguments": {"path": "output/results.md"}}
  ]
  // ❌ 缺少：stopReason, usage, timestamp 等字段
}
```

**这说明**：
- LLM 正在生成 toolCall
- 生成到一半时，输出流被截断
- OpenClaw 没有收到完整的响应

### 2. 不是超时问题

之前的分析显示只有 5 次明确的 "timeout" 错误，但有 38 次提前终止。

**提前终止的特征**：
- `stopReason` 为空
- `errorMessage` 为空
- `usage` 字段缺失
- 消息突然结束，没有正常 closing

### 3. 可能的原因

#### A. OpenAI SDK 的流式读取问题

5.28 可能使用了不同的 OpenAI SDK 版本或配置，导致：
- 流式响应 buffer 大小不足
- 过早判断流结束
- 网络波动时没有重试

#### B. HTTP 连接提前关闭

检查点：
- 5.28 的 HTTP keep-alive 设置
- TCP 连接超时配置
- 是否有代理层截断长连接

#### C. LLM 侧的问题

可能性：
- LLM 生成速度太快，超过了 OpenClaw 的读取速度
- Token 缓冲区溢出
- 流式解析逻辑有 bug

## 对比 4.14

4.14 的优势：
- **更稳定的流式处理**：73 次正常结束 vs 5.28 的 2 次
- **更少的截断**：2 次提前终止 vs 5.28 的 38 次
- **没有超时**：0 次超时 vs 5.28 的 5 次

## 需要调查的代码

### 5.28 源码位置

`D:\WorkPlace\github\openclaw528`

关键文件：
1. `src/llm/providers/openai-completions.ts` - OpenAI 流式处理
2. `src/agents/openai-transport-stream.ts` - 传输层流处理
3. `src/gateway/openai-http.ts` - HTTP 客户端配置

### 对比点

1. **Stream 读取逻辑**
   - 4.14: `src/agents/openai-transport-stream.ts`
   - 5.28: `src/llm/providers/openai-completions.ts`

2. **HTTP 超时配置**
   - 检查 `timeout`、`maxRetries` 等设置

3. **OpenAI SDK 版本**
   - 对比 `package.json` 中的 `openai` 依赖版本

## 验证方法

1. **对比 stream 处理代码**
   - 找出 4.14 和 5.28 的差异
   - 特别关注 `finish_reason` 处理逻辑

2. **增加日志**
   - 记录每个 chunk 的接收情况
   - 记录流结束的原因

3. **重现测试**
   - 使用相同的任务和模型
   - 对比 4.14 和 5.28 的行为

## 初步结论

**主要问题不是超时配置，而是 5.28 的流式响应处理有 bug**，导致：
1. LLM 输出被提前截断
2. transcript 文件不完整
3. write 等操作没有 toolResult

需要深入对比 4.14 和 5.28 的 stream handler 代码。