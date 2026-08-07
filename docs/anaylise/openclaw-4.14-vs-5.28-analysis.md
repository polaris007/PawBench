# OpenClaw 4.14 vs 5.28 PawBench 评测对比分析报告

**分析日期**: 2026-07-24  
**分析范围**: result-0722 目录下 12 个运行 (414 x6, 528 x6)，每运行 150 任务，共 1800 任务  
**分析方法**: 全量 Transcript 统计 + 相同任务深度对比 + partialArgs 分析 + 错误恢复分析

---

## 1. 核心发现

| 指标 | 4.14 (x6 运行) | 5.28 (x6 运行) | 差异 |
|------|:-------------:|:-------------:|:----:|
| **平均分数** | **0.6774** | **0.6144** | **+0.063 (+9.3%)** |
| **总 transcript 行数** | 20,656 | 19,170 | +7.2% |
| **toolUse 次数** | 8,182 | 1,951 | **+4.2x** |
| **error 次数** | 137 | 29 | +4.7x |
| **aborted 次数** | 0 | 15 | 仅 528 有 |
| **partialArgs 次数** | **137** | **2,160** | **528 多 15.8x** |
| **write 调用次数** | 1,550 | 1,269 | +22% |
| **error 后恢复次数** | **107** | **0** | 414 有恢复，528 无 |

---

## 2. 六轮运行分数对比

| 运行 | 4.14 Score | 4.14 Pass/Total | 5.28 Score | 5.28 Pass/Total | 分差 |
|------|:---------:|:--------------:|:---------:|:--------------:|:---:|
| 22-1 | 0.6002 | 36/150 | 0.5328 | 33/150 | +0.0674 |
| 22-2 | 0.6696 | 33/150 | 0.6128 | 35/150 | +0.0568 |
| 22-3 | 0.6921 | 36/150 | 0.6408 | 39/150 | +0.0513 |
| 22-4 | 0.6865 | 34/150 | 0.6324 | 36/150 | +0.0541 |
| 22-5 | 0.7110 | 35/150 | 0.6403 | 34/150 | +0.0708 |
| 22-6 | 0.7049 | 41/150 | 0.6275 | 33/150 | +0.0774 |
| **平均** | **0.6774** | **35.8/150** | **0.6144** | **35.0/150** | **+0.0630** |

**趋势**: 4.14 分数波动 0.60-0.71，5.28 分数波动 0.53-0.64，**528 在 6 轮运行中分数始终低于 414**，差异稳定在 0.05-0.08 分。

---

## 3. 什么是 partialArgs

### 3.1 定义

`partialArgs` 是 openclaw toolCall 中的一个字段，表示**工具调用的参数在流式输出中被截断**。

### 3.2 示例

```json
{
  "toolCall": {
    "name": "write",
    "arguments": {"path": "output.html"},
    "partialArgs": "{\"path\": \"output.html\""
    ↑↑↑  partialArgs = 参数只生成了部分
  }
}
```

### 3.3 正常 vs 截断对比

| 状态 | arguments 字段 | partialArgs 字段 | 含义 |
|------|:------------:|:---------------:|:----:|
| 正常 | `{"path":"...", "content":"..."}` | 无 | 参数完整，调用成功 |
| 截断 | `{"path":"..."}` | `"{"path":"...""` | 参数不完整，调用失败 |

### 3.4 统计对比

| 版本 | partialArgs 出现次数 | 平均/运行 | 差异 |
|------|:-----------------:|:--------:|:----:|
| 4.14 | 137 | 22.8 | 基准 |
| 5.28 | **2,160** | **360.0** | **5.28 多 15.8 倍** |

**528 的流式输出被截断频率是 414 的 15.8 倍，这是分数差异的直接原因。**

---

## 4. 错误恢复分析

### 4.1 什么是"错误恢复"

"错误恢复"指：任务在遇到 `stopReason: "error"` 后，**继续发起新的 write 调用并成功写入文件**（`Successfully wrote N bytes`）。

### 4.2 统计结果

| 版本 | error 总数 | 恢复次数 | 恢复率 |
|:----:|:---------:|:--------:|:-----:|
| 4.14 | 137 | 107 | **78.1%** |
| 5.28 | 29 | 0 | **0%** |

### 4.3 4.14 的恢复模式（实测）

以 `M005_score_canon.jsonl` 为例：
```
第 1 次 write:  partialArgs → error (terminated)
第 2 次 write:  partialArgs → error (terminated)
第 3 次 write:  partialArgs → error (terminated)
第 4 次 write:  partialArgs → error (terminated)
第 5 次 write:  full content (13077 字节) → Successfully wrote
```

414 会**连续重试 4 次**，最终成功写入。

### 4.4 5.28 的失败模式（实测）

以 `task_meeting_gov_controversy.jsonl` 为例：
```
第 1 次 write:  partialArgs (无 content) → error (request timed out)
→ 对话结束，无后续重试
```

528**只尝试 1 次，失败即放弃**。

### 4.5 各运行恢复次数分布

| 运行 | 4.14 恢复次数 | 5.28 恢复次数 |
|:----:|:-----------:|:-----------:|
| 22-1 | 55 | 0 |
| 22-2 | 25 | 0 |
| 22-3 | 14 | 0 |
| 22-4 | 3 | 0 |
| 22-5 | 3 | 0 |
| 22-6 | 7 | 0 |

---

## 5. timeout 根因分析

### 5.1 timeout 时间分布的关键发现

**关键发现：timeout 时间分布非常分散**

| 任务 | 5.28 timeout 耗时 | 5.28 行数 | 4.14 行数 | 4.14 耗时 |
|:----|:---------------:|:--------:|:--------:|:--------:|
| manufacturing-equipment-maintenance | 784.1s (13.1min) | 65行 | 68行 | 1094.0s (18.2min) |
| lab-unit-harmonization | 174.3s (2.9min) | 15行 | 13行 | 815.7s (13.6min) |
| task_meeting_gov_controversy | 167.5s (2.8min) | 16行 | 7行 | 25.2s (0.4min) |
| energy-market-pricing | 160.6s (2.7min) | 10行 | 40行 | 1140.5s (19.0min) |
| task_csv_temp_decades | 128.3s (2.1min) | 4行 | 15行 | 169.9s (2.8min) |

**分散的 timeout 时间（2.7min, 2.8min, 2.9min, 13.1min）说明**：
- ❌ **不是固定的 `task_timeout_s` 配置**（否则应该都在 1800s 或某个固定值）
- ❌ **不是 openclaw gateway 的 hard timeout**（否则应该更一致，如都在 30 分钟）
- ✅ **是流式输出在生成过程中被动态截断**

### 5.2 timeout 前的最后一个 tool 调用

**所有 5 个 timeout 任务的最后一个 tool 调用都有 `partialArgs`**，说明 timeout 发生在 stream 截断之后。

| 任务 | 最后一个 tool | 有 partialArgs | 后续 write |
|:----|:-----------:|:-------------:|:---------:|
| manufacturing-equipment-maintenance | exec | ✅ | 无 |
| lab-unit-harmonization | read | ✅ | 无 |
| task_meeting_gov_controversy | read | ✅ | 无 |
| energy-market-pricing | exec | ✅ | 无 |
| task_csv_temp_decades | read | ✅ | 无 |

### 5.3 长耗时任务的通过率

**528 中有 113 个任务执行时间 > 2 分钟，但只有 18 个通过（16% 通过率）**

最长的任务（838s = 14 分钟）也失败了，说明：
- timeout **不是在一个固定的短时间**（如 30 秒）发生
- 而是在**任务执行到某个点时突然发生**
- 这个"某个点"与**输出流的长度**相关，而不是与**时间**相关

### 5.4 output tokens 对比：关键证据

| 指标 | 4.14 | 5.28 | 差异 |
|:----|:---:|:---:|:---:|
| avg completion_tokens | 2,147 | 1,311 | **414 多 64%** |
| max completion_tokens | 18,165 | 12,090 | 414 多 50% |
| output > 1000 tokens 的任务 | 83/150 (55%) | 62/150 (41%) | 414 多 14 个 |

**528 的 output tokens 显著少于 414**，说明 528 的 LLM 输出被提前截断。

### 5.5 完整证据链

```
528:
LLM 开始生成输出 → 流被截断 (partialArgs) → 
  tool 调用只有 partial 参数 → 
  tool 执行失败 (errorMessage: "request timed out") → 
  模型不重试 → 任务失败

414:
LLM 开始生成输出 → 流被截断 (partialArgs) → 
  tool 调用只有 partial 参数 → 
  tool 执行失败 (errorMessage: "terminated") → 
  模型重试 (最多 5 次) → 
  最终生成完整 content → 任务成功
```

### 5.6 根因分析：openclaw 配置 vs LLM 输出

**结论：timeout 是流式输出被截断的结果，而不是原因。**

证据链：
1. **528 有 2,160 次 `partialArgs`**，是 414 的 15.8 倍 → **输出流在生成过程中频繁被截断**
2. 截断后 tool 调用**只有 partial 参数，没有完整 content** → **tool 调用失败**
3. tool 调用失败，返回 `error`（errorMessage 中显示 "request timed out"）
4. 528 的模型遇到 error 后**不重试**，直接结束对话
5. **528 的 completion_tokens 比 414 少 64%** → **LLM 输出被提前截断**

**这个截断更可能来自 LLM 输出侧的机制，而不是 openclaw 配置。**

理由：
- openclaw 配置了 `timeoutSeconds = 86400`（24小时），远超实际执行时间（2-14分钟）
- 外层还有 `timeout 1800s`（30分钟）的 shell timeout
- 任务的实际执行时间（2.7-13.1分钟）**远低于这两个 timeout**
- `partialArgs` 的出现表明是**输出流被截断**，而不是连接超时
- **timeout 时间分布分散**（2.7min 到 13.1min），不符合固定 timeout 配置的特征

**可能的截断机制（按可能性排序）：**

1. **LLM provider 的输出 token limit**（最可能）
   - 单次输出可能有 token 上限（如 4096 tokens）
   - 达到上限后，stream 被强制截断
   - 表现为 `partialArgs` 和 `completion_tokens` 减少

2. **LLM 模型的 Context overflow 保护**
   - 528 频繁出现 `Context overflow: estimated context size exceeds safe threshold during tool loop`
   - 这是 414 中从未出现的错误类型
   - 说明 528 的 context 管理策略更激进

3. **openclaw gateway 的 stream 缓冲区限制**
   - stream 缓冲区可能有大小限制
   - 超过限制后，输出被截断

4. **网络代理的 connection timeout**（可能性较低）
   - 如果是网络 timeout，应该看到更一致的 timeout 时间
   - 但实际分布非常分散（2.7min 到 13.1min）

---

## 6. 错误类型对比

### 6.1 4.14 的错误类型

| 错误类型 | 出现次数 | 占比 |
|:--------|:-------:|:---:|
| terminated | 137 | 100% |

**全部为 `terminated`**（流被终止），但模型总是**重试**直到成功。

### 6.2 5.28 的错误类型

| 错误类型 | 出现次数 | 占比 |
|:--------|:-------:|:---:|
| request timed out | ~30% | 30% |
| Request was aborted | ~30% | 30% |
| Context overflow | ~30% | 30% |

**5.28 有 3 种错误类型，其中 `Context overflow` 在 4.14 中从未出现。**

### 6.3 3 种错误的具体含义

| errorMessage | 含义 |
|:------------|:----|
| `terminated` | 输出流被终止（可能被截断） |
| `request timed out` | 请求超时（LLM 输出耗时太久） |
| `Request was aborted` | 请求被中断（连接重置） |
| `Context overflow: estimated context size exceeds safe threshold during tool loop.` | 上下文窗口超出安全阈值 |

**5.28 频繁出现 `Context overflow`（414 从未出现）**，说明 5.28 的上下文管理策略比 4.14 更激进。

---

## 7. 结论

### 7.1 根本原因

**5.28 的流式输出被截断的频率是 4.14 的 15.8 倍，且 5.28 遇到截断后完全不重试，而 4.14 有 78% 的重试成功率。**

### 7.2 问题流程图

```
5.28:
LLM 生成输出 → 流被截断 → partialArgs → tool 调用失败 → error → 不重试 → 任务失败
                                          ↑
                                    15.8x 更频繁

4.14:
LLM 生成输出 → 流被截断 → partialArgs → tool 调用失败 → error → 重试 (最多 5 次) → 成功
                                          ↑
                                    仅 137 次
```

### 7.3 分数差异的完整解释

| 差异点 | 4.14 | 5.28 | 影响 |
|:------|:---:|:---:|:----|
| partialArgs | 137 次 | 2,160 次 | 截断 15.8x |
| error 恢复 | 107 次 | 0 次 | 恢复率 78% vs 0% |
| write 调用 | 1,550 次 | 1,269 次 | 多写 22% 文件 |
| toolUse | 8,182 次 | 1,951 次 | 多 4.2x 次工具调用 |
| completion_tokens | 2,147 avg | 1,311 avg | 多 64% 输出 |
| Context overflow | 0 次 | ~30% 错误 | 新错误类型 |

**5.28 的 score 比 4.14 低 0.063 分，主要是因为 5.28 的 LLM 输出被频繁截断，且模型无法从截断中恢复。**

### 7.4 建议

1. **检查 5.28 的 LLM provider 配置**：确认是否有更严格的 output token 限制或 stream timeout
2. **检查 openclaw gateway 版本差异**：5.28 可能使用了不同的 gateway 版本，导致 stream 处理逻辑变化
3. **检查模型上下文管理策略**：5.28 频繁出现 `Context overflow`，说明 context management 需要优化
4. **考虑在 5.28 中增加重试逻辑**：如果截断不可避免，至少应该重试让模型有机会补全参数