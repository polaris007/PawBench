# PawBench 数据集分类体系

PawBench 共 150 个任务，每个任务从多个维度进行标注。下面是完整的分类体系及各维度的任务分布。

## 6 子数据集（Sources）

每个任务来源于以下 6 个数据集之一：

| 数据集 | 任务数 | 说明 |
|--------|-------|------|
| claweval | 52 | 通用 Agent 评测任务 |
| qwenclawbench | 29 | Qwen Claw 框架评测集 |
| pinchbench | 23 | 生产力场景任务 |
| qwenpawbench | 21 | Qwen Paw 框架评测集 |
| skillsbench | 15 | 技能编排场景 |
| wildclawbench | 10 | 实际复杂场景 |

## 7 能力维度（Capabilities）

每个任务可标注多个能力标签：

| 能力 | 任务数 | 说明 |
|------|-------|------|
| Tool_Use | 149 | 工具使用（文件、API、浏览器等） |
| Planning | 91 | 任务规划与拆解 |
| Logic_Reasoning | 89 | 逻辑推理 |
| Self_Verification | 59 | 自我验证与纠错 |
| Code_Manipulation | 35 | 代码编写与修改 |
| Math_Computation | 34 | 数学计算 |
| Skill_Use | 17 | 技能调用与组合 |

## 3 Agent Harness

Agent Harness 是连接模型与环境的执行框架，负责工具调用、工作流编排等：

| Harness | 版本 | 说明 |
|---------|------|------|
| QwenPaw | v1.1.3 | Qwen 团队的 Paw 框架 |
| OpenClaw | v2026.4.24 | 开源 Claw 框架 |
| Hermes | v2026.4.23 | Hermes 框架 |

Benchmark 采用 **Model × Harness 矩阵**设计，同一组 150 个任务在所有组合上运行，分离模型能力与框架能力的贡献。

## 复杂度（Complexity）

| 级别 | 任务数 |
|------|-------|
| L3（高） | 109 |
| L2（中） | 29 |
| L1（低） | 12 |

## 模态（Modality）

| 模态 | 任务数 |
|------|-------|
| text（纯文本） | 124 |
| multimodal（多模态） | 26 |

多模态通道：image（26 个任务涉及图片输入）。

## 环境（Environment）

| 环境 | 任务数 |
|------|-------|
| closed（封闭） | 129 |
| open（开放） | 21 |

## 场景（一级分类，Scenario Top）

| 场景 | 任务数 |
|------|-------|
| Office_Productivity | 30 |
| Software_Engineering | 25 |
| Safety_Alignment | 19 |
| Automation_Platform | 19 |
| Data_Analytics | 18 |
| Content_Creation | 15 |
| Information_Retrieval | 10 |
| Knowledge | 5 |
| Manufacturing_Engineering | 5 |
| Finance_Investment | 3 |
| Legal | 1 |

## 评分方式（Grading Type）

| 类型 | 任务数 | 说明 |
|------|-------|------|
| hybrid（混合） | 120 | 自动化检查 + LLM Judge 双重评分；自动分 < 0.75 时整体清零 |
| automated（自动） | 15 | 仅 Python grade() 自动化评分 |
| llm_judge（LLM 评分） | 15 | 仅 LLM Judge 评分 |
