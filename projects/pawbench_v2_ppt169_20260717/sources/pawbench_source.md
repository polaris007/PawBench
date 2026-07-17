# pawbench_intro_20260717_112821

- Source: `pawbench_intro_20260717_112821.pptx`
- Total slides: 5

## Slide 1

PawBench

Agent 评测新范式 — Model × Harness 交叉评测基准

阿里通义实验室 AgentScope 团队 | 2025

### Speaker Notes

- 欢迎来到 PawBench 介绍。今天我们将了解 Agent 评测的新范式：一个同时评估模型和运行框架的交叉评测基准。
- PawBench 由阿里通义实验室 AgentScope 团队开发，专注于解决企业部署 Agent 系统时遇到的评测难题。

## Slide 2

01

为什么需要 Agent 评测

升级效果无法量化

从模型升级到 Agent 框架迭代，效果好坏

依赖 cherry-pick 案例，难以形成决策依据

失败归因困难

任务失败了，不知道是模型能力不足、

Harness 调度问题还是工具调用失败

现有方案局限

通用 LLM 榜单不测工具调用；学术 Benchmark

依赖公网无法内网部署，自建测试无统一标准

### Speaker Notes

- 首先我们看为什么需要 Agent 评测。
- 当前有三个核心痛点：第一，升级效果无法量化，每次模型或框架升级后，效果好坏难以客观判断；第二，失败归因困难，任务出问题了很难定位责任方；第三，现有方案有各自的局限，通用榜单不测 Agent 能力，学术 Benchmark 又依赖公网。
- 这三个问题共同指向一个需求：需要一个标准化、可复现、内网可用的 Agent 评测方案。

## Slide 3

02

主流 Agent 评测方案对比

工具

定位

评测对象

完整Agent

内网运行

扩展能力

PawBench

Agent Benchmark 平台

Agent Runtime + Model + Task

★★★★★

★★★★★

★★★★★

OpenJudge

Agent 评测框架

Judge / Score / Reward

★★★★★

★★★★★

★★★★★

WildClawBench

长流程 Agent 数据集

长流程 Agent

★★★★★

★★★

★★★★

AgentBench

学术 Benchmark

LLM-as-Agent

★★

★★★★

★★★

GAIA

通用 Agent Benchmark

通用 Agent

★★★

★★

★★

SWE-bench

代码修复 Benchmark

Code Agent

★★★

★★★★

★★★

关键发现：PawBench 是唯一同时评估 Model + Harness + Task 完整 Agent 系统的评测平台

### Speaker Notes

- 这是目前主流 Agent 评测方案的对比。
- PawBench 定位为完整的 Agent Benchmark 平台，评测对象覆盖 Agent 运行时、模型和任务三个层面。相比之下，AgentBench 更偏底层的 LLM 评测，SWE-bench 只覆盖代码修复场景。
- 在完整 Agent 系统评估、内网运行能力和扩展性这三个关键维度上，PawBench 都获得了五星评价。

## Slide 4

03

PawBench 核心特性

交叉评测矩阵

三步入式评测

七维能力诊断

9 模型 × 3 Harness × 150 任务

Step 1: 选择模型与 Harness

7 大原子能力切片分析

= 4,050 个评测单元

Step 2: Docker 沙箱隔离运行

Tool_Use — 工具调用

精准定位瓶颈在模型还是框架

每个任务在独立容器中执行

Skill_Use — Skill 发现与执行

workspace 文件按需挂载

支持 3 个主流 Harness：

Code_Manipulation — 代码操作

严格超时与重试机制

QwenPaw（默认 baseline）

Logic_Reasoning — 逻辑推理

Step 3: 自动 + LLM 双重评分

OpenClaw（通用开源 Runtime）

Planning — 任务规划

Automated: Python grade() 断言检查

Hermes（社区对照组）

Math_Computation — 数学计算

LLM Judge: 语义评估

Harness 极差可达 11.5 分，

Hybrid: 自动分 < 0.75 时清零

Self_Verification — 自我验证

接近一次大模型版本升级的收益

5 大应用场景打标

3 个复杂度等级 (L1-L3)

### Speaker Notes

- PawBench 的核心特性体现在三个方面。
- 第一是交叉评测矩阵。9个模型、3个 Harness、150个任务组成 4050 个评测单元，可以精准定位瓶颈到底在模型还是框架。
- 第二是三步入式评测流程。选择模型和 Harness 后，在 Docker 沙箱中隔离运行，然后通过自动化评分和 LLM 评判的双重机制确保评测结果的可靠性。
- 第三是七维原子能力诊断。从 Tool_Use 到 Self_Verification，覆盖 Agent 核心能力的方方面面，支持按场景、模态、复杂度等多维度切片分析。

## Slide 5

04

为什么选择 PawBench

唯一交叉评测平台

集成路径

同时评估 Model + Harness + Task，适合既自研 Agent 又调优模型的团队

Harness 差距量化 — 发现实际部署中的瓶颈

Phase 1 — 部署环境（2周）

Docker 部署，跑通全量 150 任务

开源生态 + 可扩展

Phase 2 — 适配内网（2周）

基于 OpenJudge 生态，可自定义任务和 Judge

改造依赖公网的任务，自定义 20-30 道

阿里通义实验室持续维护，社区活跃

Phase 3 — 持续优化

嵌入迭代流程，切片分析推动持续改进

企业就绪

Docker 内网部署，数据不出网

可集成到 CI 流水线，每次发布自动回归

github.com/agentscope-ai/PawBench

### Speaker Notes

- 总结来看，选择 PawBench 的三个理由。
- 第一，它是目前唯一能同时评估模型和 Harness 的评测平台，适合我们既自研 Agent 又调优模型的场景。
- 第二，基于 OpenJudge 开源生态，可扩展性强，可以根据业务需求自定义任务和评判逻辑。
- 第三，企业级就绪，Docker 内网部署保障数据安全，可集成到 CI 流水线实现自动化回归测试。
- 集成路径分为三个阶段：两周部署环境，两周适配内网，后续持续优化。
