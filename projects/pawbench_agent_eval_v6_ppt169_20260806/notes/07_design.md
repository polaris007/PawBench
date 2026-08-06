# 07 PawBench 能力与评测设计 - 演讲备注

**时长建议**: 90 秒

**讲解要点**:
- 核心设计理念：Agent 表现 = f(Model, Harness)。Model 决定能力上限，Harness 决定稳定落地，两者独立评测才能发现真实瓶颈。
- 三步评测流程：① 选择模型与 Harness 组合 → ② Docker 沙箱隔离运行（严格超时与重试，确保可复现）→ ③ 自动 + LLM 双重评分。
- 七种原子能力诊断：Tool_Use（工具调用与编排）、Skill_Use（Skill 发现与执行）、Code_Manipulation（代码操作与修复）、Logic_Reasoning（逻辑推理）、Planning（多步任务规划）、Math_Computation（数学计算）、Self_Verification（自我验证与纠错）。
- 评分模式：automated（确定性断言检查）、llm_judge（语义评估）、hybrid（混合）。
- 覆盖场景：办公协同、软件工程、数据分析、信息检索、自动化脚本；任务复杂度 L1/L2/L3。
- 规模：9 模型 × 3 Harness × 150 任务 = 4,050 个评测单元。

**过渡语**:
设计落地后的官方评测结果，下一页看评分矩阵。
