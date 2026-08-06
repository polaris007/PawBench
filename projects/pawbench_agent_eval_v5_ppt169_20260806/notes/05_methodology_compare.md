# 05 PawBench 方法论 × 主流范式对比 - 演讲备注

**时长建议**: 120 秒（新增方法论页，重点讲解）

**讲解要点**:
- 核心结论先行：PawBench 与主流"同源混合、交叉创新"。
- 与主流一致（同源）：
  - 确定性断言检查（automated 自动评分）= 最终状态评估 ①
  - LLM 评判 + Rubric 评分细则 = LLM-as-a-Judge ③
  - Docker 沙箱隔离、离线可复现 = 沙箱环境模拟 ⑥
  - 额外：以 transcript + 产物双重输入评分，兼顾过程信息与最终结果。
- PawBench 独特（差异化）：
  - Model × Harness × Task 交叉矩阵：主流评测把 Harness/Scaffold 当隐藏变量，PawBench 显式化为独立评测维度，9×3×150 交叉矩阵可定位真实瓶颈在模型还是框架。
  - hybrid 混合惩罚机制：自动分 < 0.75 时 LLM 分清零，防止跳过任务、空文件刷分。
  - 评分对框架中立、刻意不做轨迹对齐：区别于轨迹评估 ②，只依赖 transcript 与 workspace_path，多路径达成同样产物皆可得分。
- 结论：混合主流范式 + 交叉矩阵设计，使 PawBench 在完整 Agent 评测维度上更全面。

**过渡语**:
方法论讲清楚了，回到 PawBench 本身的优势。
