# Agent评测_v5 - Design Spec

> Human-readable design narrative — rationale, audience, style, color choices, content outline.
> Machine-readable execution contract: `spec_lock.md`. Executor re-reads `spec_lock.md` before every SVG page.

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | Agent评测_v5（PawBench Agent 评测方法论） |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | 13 |
| **Design Style** | Swiss Minimal + Briefing |
| **Target Audience** | 技术团队、AI 架构师、企业决策者 — 正在评估 Agent 评测方案 |
| **Use Case** | 内部分享 / 技术选型汇报 |
| **Delivery Purpose** | `balanced` — 业务演示 + 可阅读，body 24px |
| **Content Strategy** | 平衡 — 基于 v4 素材组织，新增方法论内容，不偏离原文事实 |
| **Created Date** | 2026-08-06 |

---

## II. Canvas Specification

| Property | Value |
| -------- | ----- |
| **Format** | PPT 16:9 |
| **Dimensions** | 1280×720 |
| **viewBox** | `0 0 1280 720` |
| **Margins** | left/right 60px, top/bottom 50px |
| **Content Area** | 1160×620 |

---

## III. Visual Theme

### Theme Style

- **Mode**: `briefing` — 信息型简报，主题分明，篇幅均衡，客观陈述
- **Visual style**: `swiss-minimal` — 网格锁定、留白激进、无装饰，干净专业
- **Theme**: Light theme
- **Tone**: 技术、专业、现代、客观

### Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#FFFFFF` | Page background |
| **Secondary bg** | `#F2F5FA` | Card background, section background |
| **Primary** | `#1E3A8A` | Title decorations, key sections, icons |
| **Accent** | `#2563EB` | Data highlights, key information, links |
| **Secondary accent** | `#93C5FD` | Secondary emphasis |
| **Body text** | `#1A1A2E` | Main body text |
| **Secondary text** | `#64748B` | Captions, annotations |
| **Border/divider** | `#E2E8F0` | Card borders, divider lines |
| **Success** | `#10B981` | Positive indicators |
| **Warning** | `#EF4444` | Issue markers |

### AI Image Strategy

*Not applicable — no AI images in this deck.*

---

## IV. Typography System

### Font Plan

**Typography direction**: 现代 CJK 无衬线，单一家族重量对比，瑞士风格纯粹感

| Role | Chinese | English | Fallback tail |
| ---- | ------- | ------- | ------------- |
| **Title** | `"Microsoft YaHei"` | `Arial` | `sans-serif` |
| **Body** | `"Microsoft YaHei"` | `Arial` | `sans-serif` |
| **Code** | — | `Consolas, "Courier New"` | `monospace` |

**Per-role font stacks**:

- font_family: `"Microsoft YaHei", Arial, sans-serif`
- code_family: `Consolas, "Courier New", monospace`

### Font Size Hierarchy

**Baseline**: Body font size = **24px** (balanced, read + projected mix).

| Purpose | Ratio to body | Size (px) | Weight |
| ------- | ------------- | --------- | ------ |
| Page title | 1.75x | 42 | Bold |
| Subtitle | 1.33x | 32 | SemiBold |
| **Body content** | **1x** | **24** | Regular |
| Annotation / caption | 0.75x | 18 | Regular |
| Page number / footnote | 0.67x | 16 | Regular |

---

## V. Layout Principles

### Page Structure

- **Header area**: 80px top bar with section indicator
- **Content area**: 1160×590 main content
- **Footer area**: 50px bottom bar with page number

### Layout Pattern Library

| Pattern | Suitable Scenarios |
| ------- | ----------------- |
| **Single column centered** | Cover, closing |
| **Symmetric split (5:5)** | Feature lists, comparisons |
| **Full-width with side note** | Data tables, KPI cards |
| **Three column cards** | Feature lists, parallel points |

### Spacing Specification

| Element | Value |
| ------- | ----- |
| Safe margin from canvas edge | 60px |
| Content block gap | 32px |
| Card gap | 24px |
| Card padding | 24px |
| Card border radius | 0 (Swiss sharp) |
| Line-height | 1.5x |

---

## VI. Icon Usage Specification

- **Built-in icon library**: `chunk-filled` (直棱直角实心图标，与 Swiss 几何精确感匹配)
- **Usage method**: SVG placeholder `<use data-icon="chunk-filled/name" .../>`

*本 deck 以文本/表格/网格驱动，仅在方法论范式卡片等处按需使用少量图标。*

---

## VII. Visualization Reference List

*Not applicable — 本 deck 无数据图表（方法论页为概念范式卡片，非数据可视化）。*

---

## VIII. Image Resource List

| File | Acquire Via | Status | Usage |
| ---- | ----------- | ------ | ----- |
| `image1.png` | source-imported | Ready | P08 官方评测结果矩阵（v4 Slide 6 原图） |

---

## IX. Content Outline

### Part 1: 背景与动机（继承 v4）

#### Slide 01 - Cover（anchor）

- **Cover impact**: Hero headline「基于 PawBench 的 Agent 评测」+ 三维交叉评测定位，accent rule 分割，页码 /13
- **Layout**: Single column centered, oversized title, thin accent rule
- **Title**: 基于 PawBench 的 Agent 评测
- **Subtitle**: 三维交叉评测 · Model × Harness × Task
- **Info**: 150 道标准化任务 · 自动评分引擎 · Docker 内网隔离 · 七维原子能力诊断

#### Slide 02 - 为什么需要 Agent 评测（dense）

- **Layout**: 上下两痛点卡 + 右侧价值要点，或左右对称分栏
- **Title**: 为什么需要 Agent 评测
- **Content**:
  - 痛点一：升级效果无法量化 — 人工挑选少量案例判定 → PawBench 解法：150 道标准化任务 + 自动评分引擎，版本间横向对比
  - 痛点二：现有方案局限 — 通用 LLM 榜单不测工具调用；学术 Benchmark 依赖公网 → PawBench 解法：开源 + Docker 沙箱隔离，数据不出网
  - PawBench 价值：量化升级效果 / 精准定位短板 / 内网安全运行

#### Slide 03 - 主流 Agent 评测方案对比（dense）

- **Layout**: Full-width data table（继承 v4 Slide 3 表格）
- **Title**: 主流 Agent 评测方案对比
- **Content**: 9 个方案（PawBench / WildClawBench / SkillsBench / PinchBench / AgentBench / GAIA / SWE-bench / DeepEval / Promptfoo）× 维度（定位/评测对象/完整Agent/内网部署/扩展能力/资料生态/最佳场景）+ 评分说明 + 数据来源脚注

### Part 2: 方法论（新增）

#### Slide 04 - 主流 Agent 评测方法论全景（dense）

- **Layout**: 三列 × 两行六范式卡片网格，每卡：编号 + 范式名 + 核心思路 + 代表工具
- **Title**: 主流 Agent 评测方法论全景
- **Core message**: 六大范式回答「怎么评」，主流评测体系普遍混合采用
- **Content**:
  - ① 最终状态评估（Final-State）— 确定性后端 + 最终产物/状态比对，可复现但工程量大 — τ-bench / τ²-bench / AppWorld
  - ② 轨迹评估（Trajectory）— 黄金轨迹对齐或 LLM 评判轨迹质量，可定位失败步骤 — LangSmith / AgentEvals
  - ③ LLM-as-a-Judge — 强模型 + Rubric 细则评分，可扩展、适合开放任务 — 通用开放任务
  - ④ 逐步评估（Stepwise）— 对每步独立校验（工具选择/参数/输出），错误定位精确 — Arize Phoenix / DeepEval
  - ⑤ pass@k 采样 — k 次运行成功率，衡量随机一致性，更诚实但成本高 — Claw-Eval / CI 实践
  - ⑥ 沙箱环境模拟（Sandbox）— Docker 隔离 + 离线快照可复现，真实与可控的折中 — GAIA / WebArena / OSWorld
- **Note**: 数据来源：ACL 2026《A Survey on Evaluation of LLM-based Agents》、AgentCompass、Claw-Eval 等公开文献与社区实践

#### Slide 05 - PawBench 方法论 × 主流范式对比（dense）

- **Layout**: 左右对比 — 左「与主流同源」右「PawBench 独特设计」，底部结论条
- **Title**: PawBench 方法论与主流范式的关系
- **Core message**: PawBench 混合采用主流范式，并以 Model × Harness 交叉矩阵走出差异化
- **Content**:
  - 同源（与主流一致）：
    - 确定性断言检查（自动评分）= 最终状态评估 ①
    - LLM 评判 + Rubric 细则 = LLM-as-a-Judge ③
    - Docker 沙箱隔离运行 = 沙箱环境模拟 ⑥
  - 独特（差异化）：
    - Model × Harness × Task 交叉矩阵 — 主流把 Harness 当隐藏变量，PawBench 显式化为独立评测维度
    - hybrid 惩罚机制 — 自动分 < 0.75 时 LLM 分清零，防跳过任务/空文件刷分
    - 评分对框架中立 — 只依赖 transcript 与 workspace_path，刻意不做轨迹对齐
  - 结论条：与主流「同源混合、交叉创新」，在完整 Agent 评测维度上更全面

### Part 3: PawBench 深度（继承 v4）

#### Slide 06 - PawBench 的优势（dense）

- **Layout**: 四核心优势卡 + 差异化条（继承 v4 Slide 4）
- **Title**: PawBench 的优势
- **Content**: 完整 Agent 评测（Model×Harness×Task）/ 内网安全运行（Docker 数据不出网）/ Model×Harness 交叉评测（行业首创解耦）/ 开源可扩展（OpenJudge 生态，Apache 2.0，AgentScope 维护）

#### Slide 07 - PawBench 能力与评测设计（dense）

- **Layout**: 三步流程 + 七种能力 + 评分模式/覆盖场景/复杂度（继承 v4 Slide 5）
- **Title**: PawBench 能力与评测设计
- **Content**: 核心设计理念 f(Model, Harness)；三步评测流程（选择组合→沙箱运行→双重评分）；七种能力诊断（Tool_Use/Skill_Use/Code_Manipulation/Logic_Reasoning/Planning/Math_Computation/Self_Verification）；评分模式（automated/llm_judge/hybrid）；覆盖场景；任务复杂度 L1/L2/L3；4,050 评测单元

#### Slide 08 - 官方评测结果 · Model × Harness 评分矩阵（dense）

- **Layout**: 全宽图片 + 说明（继承 v4 Slide 6，image1.png）
- **Title**: PawBench 官方评测结果 · Model × Harness 评分矩阵
- **Content**: 全景 150 任务（文本+多模态）· 9 模型 × 3 Harness · Overall 综合得分；图片；数据来源脚注

#### Slide 09 - 评测任务体系（dense）

- **Layout**: 任务来源表 + 五维标签（继承 v4 Slide 7）
- **Title**: PawBench 评测任务体系
- **Content**: 150 道任务 × 6 源数据集；五维标签（scenario/capabilities/complexity/modality/environment）；标签赋能（按场景对比/按能力诊断/按复杂度分层）

#### Slide 10 - 任务执行与评分实战 · T053（dense）

- **Layout**: 四步链路 ①②③④（继承 v4 Slide 8）
- **Title**: 任务执行与评分实战 · 以 T053 为例
- **Content**: 任务卡（来源/类型/复杂度/环境/评分）；① 沙箱执行 ② 结果采集 ③ 双重评分 hybrid ④ 汇总得分；混合惩罚机制

#### Slide 11 - 任务 ↔ 日常工作能力（dense）

- **Layout**: 表格（继承 v4 Slide 9）
- **Title**: PawBench 任务 ↔ 日常工作能力
- **Content**: 8 行映射表（邮件/通讯录/资讯/Excel/PDF/代码/Skill 创建/Skill 使用）+ 注

#### Slide 12 - 应用场景与集成方式（dense）

- **Layout**: 典型场景 + 集成方式 + 企业需求适配表（继承 v4 Slide 10）
- **Title**: PawBench 应用场景与集成方式
- **Content**: 模型升级评估 / Agent 框架迭代 / 自定义 Skill 验证 / 回归测试流水线；环境部署 / 内网适配 / 持续迭代；企业需求与能力适配表

#### Slide 13 - 总结（anchor）

- **Closing impact**: 三大收束点 + 一段结语（继承 v4 Slide 11）
- **Title**: 总结
- **Content**: 交叉评测矩阵 / 灵活可扩展 / 内网安全就绪；结语：Agent 评测正处于关键转折期，从主观判断转向标准化、自动化、多维度量化评测

---

## X. Speaker Notes Requirements

One speaker note file per page, saved to `notes/`:

- **Filename**: match SVG name
- **Content**: script key points, timing cues, transition phrases
