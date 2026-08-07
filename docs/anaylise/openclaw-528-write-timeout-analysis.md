# OpenClaw 5.28 "Write 没有 toolResult" 问题分析报告

## 问题现象

5.28 的 transcript 文件中，大量 write 操作**没有对应的 toolResult**：

| 版本 | write 总数 | 有 toolResult | 无 toolResult | 成功率 |
|:-----|:----------:|:-------------:|:-------------:|:------:|
| **5.28** | 173 | 15 (8.7%) | 158 (91.3%) | **8.7%** |
| **4.14** | 272 | 196 (72.1%) | 76 (27.9%) | **72.1%** |

## 根本原因

### 1. LLM 请求超时

**5.28 有 5 次明确的 "request timed out" 错误**，而 4.14 有 0 次。

示例（energy-market-pricing 任务最后一行）：

```json
{
  "stopReason": "error",
  "errorMessage": "request timed out",
  "timestamp": 1784721743653
}
```

**超时导致**：
- LLM 响应流被强制终止
- transcript 文件突然结束
- 没有后续 toolResult 记录

### 2. 超时发生在 write 操作时

分析显示，超时通常发生在：
- **长文本生成**：write 操作包含大量 content 时
- **复杂任务**：需要长时间推理的任务
- **网络延迟**：LLM API 响应慢

示例（manufacturing-equipment-maintenance）：

```
行 -2 (最后):
  toolCall: write - args={'path': '/app/.../analyze_reflow.py'}
  stopReason: error
  errorMessage: request timed out
```

### 3. 5.28 的超时配置可能更激进

需要检查：
- 5.28 的 HTTP timeout 设置
- LLM 客户端的 timeout 配置
- 是否有额外的超时层（如代理、网关）

## 影响

### 1. Transcript 不完整

- write 操作已发送，但不知道结果
- 无法确认文件是否成功写入
- 后续对话无法继续（因为缺少 toolResult）

### 2. 任务失败

超时后，agent 无法：
- 确认 write 是否成功
- 继续执行后续步骤
- 完成任务目标

## 对比 4.14

4.14 的优势：
- **超时更少**：0 次 vs 5 次
- **write 成功率更高**：72.1% vs 8.7%
- **更稳定的流式处理**

## 建议修复

### 1. 检查超时配置

对比 4.14 和 5.28 的以下配置：
- HTTP 客户端 timeout
- LLM API timeout
- Stream 读取 timeout

位置可能在：
- `src/gateway/openai-http.ts`
- `src/llm/providers/openai-completions.ts`
- `src/agents/openai-transport-stream.ts`

### 2. 增加超时时间

对于长文本 write 操作，考虑：
- 增加 timeout 阈值
- 使用动态 timeout（基于 content 长度）
- 添加重试逻辑

### 3. 改进错误处理

当前问题：
- 超时时没有保存部分结果
- transcript 突然结束，没有错误标记

建议：
- 在超时时添加错误标记
- 保存已接收的部分数据
- 允许恢复或重试

## 验证方法

1. **增加 timeout** 后重新运行相同任务
2. **监控网络延迟**，确认是否是网络问题
3. **对比 LLM 响应时间**，确认 5.28 是否真的更慢

## 相关文件

- 5.28 源码：`D:\WorkPlace\github\openclaw528`
- 4.14 源码：`D:\WorkPlace\github\openclaw414`
- 超时配置可能位置：
  - `src/gateway/openai-http.ts`
  - `src/llm/providers/openai-completions.ts`
  - `src/agents/openai-transport-stream.ts`