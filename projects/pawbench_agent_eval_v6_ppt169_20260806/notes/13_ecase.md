# 13 实战评测案例 - 演讲备注

**时长建议**: 90 秒

**讲解要点**:
- 这是我们用 PawBench 做的真实评测：同一 LLM（QWen35-397b）下，OpenClaw 框架从 4.14 升级到 5.28，得分从 68.1 / 66.0 / 70.3（平均 0.6774）降到 60.3 / 61.2 / 59.7（平均 0.6144），平均分下降 6.3 分。
- 关键差异：5.28 的 partialArgs 截断次数高达 2,160（4.14 仅 137，约 15.8 倍）；4.14 错误后能重试恢复 107 次，5.28 恢复 0 次。
- 根因：5.28 架构调整后，LLM 流截断的 tool call 不重试——官方 PR openclaw/openclaw #87571 确认这是已知架构缺陷（truncated tool call 落入 terminal error，不触发重试级联）。
- 错误类型：timed out / aborted / Context overflow 各约 30%，其中 Context overflow 在 4.14 从未出现。
- 结论：版本升级未必带来收益，PawBench 让「Agent 框架迭代」效果可量化、可归因。

**过渡语**:
这个案例说明，框架升级是好是坏不能凭感觉——最后我们总结一下 PawBench 的核心价值。
