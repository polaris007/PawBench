# 03 主流 Agent 评测方案对比 - 演讲备注

**时长建议**: 90 秒

**讲解要点**:
- 横向对比 9 个主流方案：PawBench、WildClawBench、SkillsBench、PinchBench、AgentBench、GAIA、SWE-bench、DeepEval、Promptfoo。
- 关键维度：定位、评测对象、完整 Agent 覆盖、内网部署能力、扩展能力、资料生态。
- 观察：完整 Agent 评测和内网部署往往不可兼得 —— 学术 Benchmark（GAIA/AgentBench）依赖公网，纯评测框架（DeepEval/Promptfoo）不提供 Agent 任务体系。
- PawBench 在完整 Agent、内网部署、扩展能力三项同时满星。
- 评分说明：内网部署 = 内网可运行 + 公网依赖度的综合评价。
- 数据来源：各项目公开文档及 GitHub 仓库，截至 2025 年 7 月。

**过渡语**:
这个表比的是"谁来评"，下一页我们看"怎么评"—— 主流的评测方法论。
