# PawBench 简介 — 详细版（PPT 素材，5页以上）

---

## 第1页：背景与痛点

### 为什么需要 Agent 评测

当前公司内部已部署私有化 OpenClaw、OpenCode 等多款智能体，在模型升级（如从 qwen3.6-plus 升级到 qwen3.7-max）或 Agent 框架迭代时，团队面临几个核心问题：

1. **升级效果无法量化**：缺少标准化评测集，效果好坏靠 cherry-pick 案例判定，难以形成决策依据
2. **失败归因困难**：任务失败了，不知道是模型能力不足、Harness 框架调度问题、工具调用失败，还是任务描述模糊
3. **缺乏可复现性**：不同时间、不同人评估同一模型，结论不一致

### 现有 Benchmark 的局限

| 方案 | 局限 |
|---|---|
| 通用 LLM 榜单（MMLU、GSM8K 等） | 只测知识/推理，不测工具调用、多步编排等 Agent 核心能力 |
| AgentBench、GAIA 等学术 Benchmark | 依赖公网环境，部分任务不可复现，不适合内网私有化 |
| SWE-bench | 仅覆盖代码修复，不覆盖通用办公、信息检索等场景 |
| 自建 Ad-hoc 测试 | 无统一标准，对比不严谨，维护成本高 |

---

## 第2页：PawBench 是什么

### 核心定位

PawBench 是阿里通义实验室 AgentScope 团队开发的开源 **Model × Harness 交叉评测基准**，专门用于评估完整 AI Agent 系统的综合表现。

### 核心公式

```
Agent 表现 = f(Model, Harness)
```

- **Model**：基座大模型，决定能力上限
- **Harness**：智能体运行框架（Agent Runtime），决定能力能否稳定落地

两者结合才能反映真实部署效果。

### 三维评测矩阵

```
    9 个模型 × 3 个 Harness × 150 道任务 = 4,050 个评测单元
```

- **9 个模型**：claude-opus-4.6、deepseek-v4-pro、qwen3.7-max、qwen3.6-max-preview、qwen3.6-plus、qwen3.6-27b、glm-5.1、kimi-k2.6、qwen3.6-35b-a3b
- **3 个 Harness**：QwenPaw（默认 baseline）、OpenClaw（通用开源 Agent Runtime）、Hermes（社区对照组）
- **2 种模态**：纯文本 124 道 + 多模态 26 道

### 开源生态

PawBench 是 **OpenJudge 生态** 的一部分，底层复用 OpenJudge 的评测引擎和 50+ 生产级 Grader，可自定义 Judge 逻辑、评分规则和任务类型。

---

## 第3页：评测任务体系

### 任务来源

v1.0 的 150 道任务来自 6 个高质量 Agent 评测集：

| 来源 | 数量 | 主要覆盖 |
|---|---|---|
| 自建任务 | 21 | 自动化、信息检索、安全对齐 |
| claweval | 52 | 办公协同、数据分析、内容创作 |
| qwenclawbench | 29 | 自动化、软件工程、安全对齐 |
| pinchbench | 23 | 办公流程、软件工程、信息检索 |
| skillsbench | 15 | 长程 Skill、领域自动化 |
| wildclawbench | 10 | 办公流程、安全对齐 |

### 五维标签体系

每道任务按 5 个正交维度打标，支持精细化的切片分析：

| 维度 | 字段 | 标签值 |
|---|---|---|
| 应用场景 | `scenario` | Office_Productivity、Software_Engineering、Safety_Alignment 等 |
| 原子能力 | `capabilities` | Logic_Reasoning、Math_Computation、Code_Manipulation、Tool_Use、Skill_Use、Planning、Self_Verification |
| 复杂度 | `complexity` | L1（1-2步）、L2（3-5步）、L3（5步以上含分支） |
| 输入模态 | `modality` | text / multimodal（image、audio、video） |
| 运行环境 | `environment` | closed（离线可复现）/ open（需联网或 SaaS API） |

---

## 第4页：评测流程与技术架构

### 评测流程（三步）

```
Step 1: 选择模型与 Harness
        ↓
Step 2: Docker 沙箱隔离运行
   ┌─────────────────────────────┐
   │  每个任务在独立容器中执行     │
   │  workspace 文件按需挂载      │
   │  严格超时与重试机制          │
   └─────────────────────────────┘
        ↓
Step 3: 自动 + LLM 双重评分
   ┌─────────────────────────────┐
   │  Automated: Python grade()  │
   │  LLM Judge: 语义评估        │
   │  Hybrid: 自动分<0.75时清零  │
   └─────────────────────────────┘
```

### 评分模式

| 模式 | 适用场景 | 说明 |
|---|---|---|
| `automated` | 确定性任务 | 内置 Python 断言检查，字节级比对 |
| `llm_judge` | 定性任务（内容生成等） | 使用评分模型 + 细则评估逻辑和业务洞察 |
| `hybrid` | 复杂任务 | 自动检查 + LLM 判断混合，权重可配置 |

### 运行方式

```bash
# 单任务 smoke test
python run_bench.py --tasks T053 --model dashscope/qwen3.6-plus

# 多 Harness 横向对比
python run_bench.py --agents qwenpaw openclaw hermes \
    --model dashscope/qwen3.6-plus --tasks T002 T006

# 顺序评测多个模型
python run_bench.py --model dashscope/qwen3.6-plus \
    --model anthropic/claude-sonnet-4-6
```

支持 OpenAI 兼容 API 和私有化模型接入，不限定部署形式。

---

## 第5页：评测结果解读——切片分析

### 总览：Model × Harness 矩阵

以 v1.0 公开榜单为例（整体 score，范围 0-100）：

| Model | QwenPaw | OpenClaw | Hermes | Harness 极差 |
|---|---|---|---|---|
| claude-opus-4.6 | **78.3** | 76.1 | 78.4 | 2.3 |
| deepseek-v4-pro | **75.6** | 75.4 | 72.1 | 3.6 |
| qwen3.6-max-preview | **78.3** | 75.1 | 68.1 | 10.3 |
| qwen3.6-35b-a3b | **68.3** | 67.8 | 56.7 | 11.5 |
| glm-5.1 | **71.1** | 68.5 | 63.2 | 7.9 |

**关键发现**：Harness 差距可达 11.5 分，接近一次模型大版本升级的收益。

### 切片分析的价值

PawBench 的核心能力不是排名，而是**切片诊断**：

| 切片维度 | 分析价值 |
|---|---|
| 按能力切片 | Skill_Use 平均 47.2，是所有能力中最弱的——Skill 发现、加载仍需加强 |
| 按模态切片 | 纯文本 74.1 vs 多模态 64.0，多模态是共同短板 |
| 按场景切片 | Finance、Software Engineering 等场景 Harness 差距大，适合定位工具/搜索问题 |
| 按复杂度切片 | L3 长任务最容易暴露模型/Harness 差异 |
| 按来源切片 | skillsbench 任务平均仅 40.9，长程 Skill 编排普遍困难 |

---

## 第6页：PawBench 对我们公司的价值

### 适配度分析（基于对比表）

| 需求 | PawBench 能力 |
|---|---|
| 内网私有化部署 | ✅ 开源 + Docker，数据和任务不出内网 |
| 评测完整 Agent 系统 | ✅ 同时评估 Model × Harness × Task |
| 自定义任务 | ✅ 基于 OpenJudge，可自定义任务、Judge、评分规则 |
| 支持多 Agent | ✅ 原生支持 QwenPaw、OpenClaw、Hermes，可扩展 |
| 量化回归 | ✅ 标准化任务 + 自动评分，适用于每次升级的回归测试 |
| Skill 能力评估 | ✅ 7 大原子能力包含 Skill_Use，有 15 道专门任务 |

### 典型应用场景

1. **模型升级评估**：固定 Harness（如 OpenClaw），横向跑新旧模型，看整体分和切片分的变化
2. **Agent 框架迭代**：固定模型，横向跑不同版本 Harness，验证框架改动是否引入退化
3. **自定义 Skill 验证**：新增业务 Skill 后，在相关切片上验证 Skill 发现和执行效果
4. **回归测试流水线**：集成到 CI 流程中，每次 Agent/模型发布自动触发评测

### 集成路径

```
Phase 1（2周）  Phase 2（2周）   Phase 3（持续）
┌──────────┐   ┌──────────┐    ┌──────────────┐
│ 部署环境  │ → │ 适配内网  │ → │ 嵌入迭代流程  │
│ 跑通全量  │   │ 自定义任务│   │ 持续回归优化  │
│ 150任务   │   │ 20-30道  │   │ 切片分析推动  │
└──────────┘   └──────────┘    └──────────────┘
```

---

## 第7页：竞品对比与选择理由

| 对比维度 | PawBench | AgentBench | SWE-bench | Promptfoo |
|---|---|---|---|---|
| 评测对象 | Agent Runtime + Model + Task | LLM-as-Agent | Code Agent | Prompt + Model |
| 内网运行 | ✅ 完全支持 | ✅ 支持 | ✅ 支持 | ✅ 支持 |
| 完整 Agent 评测 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 扩展能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 数据/任务依赖公网 | ⭐⭐（部分可改造） | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Skill/工具调用评测 | ✅ 核心能力 | ❌ 不侧重 | ❌ 不侧重 | ❌ 不支持 |

**选择理由总结**：
- PawBench 是唯一一个**同时评估模型和 Harness** 的评测平台，适合我们既自研 Agent 又调优模型的场景
- 基于 OpenJudge 生态，可扩展性强，能逐步构建适合我们业务的自定义任务集
- 社区活跃，有阿里通义实验室持续维护，长期可持续

---

## 第8页：引用与参考

### 项目链接

- GitHub 仓库：https://github.com/agentscope-ai/PawBench
- 在线榜单：https://agentscope-ai.github.io/PawBench/
- OpenJudge 生态：https://github.com/agentscope-ai/OpenJudge

### 参考文章

- PawBench v1.0 技术博客：https://agentscope-ai.github.io/PawBench/blog/PAWBENCH_MODEL_HARNESS_BLOG/
- 4,050 次 Agent 运行的经验总结（阿里云社区）：https://www.alibabacloud.com/blog/what-we-learned-from-evaluating-4050-agent-runs_603332
- 论文引用格式：

```bibtex
@misc{pawbench,
  title  = {PawBench: A benchmark for evaluating LLM × harness performance},
  author = {The OpenJudge Team},
  url    = {https://github.com/agentscope-ai/PawBench},
  month  = {06},
  year   = {2026}
}
```

### 版本信息

- PawBench v1.0 | 150 tasks | 6 datasets | 3 Harnesses | 7 capabilities
- License: Apache 2.0
- 技术栈：Python 3.11+ / Docker / Node.js 20+（可选，本地榜单站点）
