# PawBench 简介 — 精简版（PPT 素材，1-2页）

---

## 一句话定位

**PawBench** 是阿里通义实验室 AgentScope 团队开源的 **Model × Harness 交叉评测基准**，用于量化评估智能体系统（模型 + 运行框架 + 任务）的综合表现。

核心公式：`Agent 表现 = f(Model, Harness)`

---

## 为什么要用 PawBench

| 痛点 | PawBench 的解法 |
|---|---|
| 升级模型/Agent 后效果"感觉好了一点"，无法量化 | 150 道标准化任务 + 自动评分，跑完出分，可对比 |
| 任务失败了，不知道是模型不行还是框架不行 | Model × Harness 交叉矩阵 + 切片分析，精准定位瓶颈 |
| 缺乏内网可用的评测平台 | 开源 + Docker 沙箱，完全私有化部署，数据不出网 |

---

## 评测了什么

| 维度 | 具体内容 |
|---|---|
| **150 道任务** | 来自 6 个高质量 Agent 评测集 |
| **7 大原子能力** | Tool_Use、Skill_Use、Code_Manipulation、Logic_Reasoning、Planning、Math_Computation、Self_Verification |
| **5 大应用场景** | 办公协同、软件工程、数据分析、信息检索、自动化脚本等 |
| **2 种评分模式** | 自动化评分（确定性检查）+ LLM Judge（语义评估） |
| **3 个复杂度等级** | L1（1-2步）、L2（3-5步）、L3（5步以上含分支） |

---

## 评测流程（三步）

```
选择模型 + Harness  →  Docker 沙箱隔离运行  →  自动 + LLM 双重评分
```

支持 QwenPaw、OpenClaw、Hermes 三个主流 Agent Harness，以及 OpenAI 兼容 API 的任意模型。

---

## 对我们的价值

1. **量化升级效果**：每次 Agent/LLM 升级后跑一遍，数据说话
2. **精准定位短板**：切片分析可知具体哪个能力、哪个场景在退化
3. **内网安全运行**：Docker 隔离，任务数据可改造为离线，不需要公网
4. **低成本集成**：基于 OpenJudge 生态，可自定义任务和 Judge

---

## 参考链接

- 项目主页：https://github.com/agentscope-ai/PawBench
- 在线榜单：https://agentscope-ai.github.io/PawBench/
- 数据来源：9 个模型 × 3 个 Harness × 150 任务 = 4,050 个评测单元
