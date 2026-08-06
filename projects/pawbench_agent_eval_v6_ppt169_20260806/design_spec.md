# Agent评测_v6 - Design Spec

> Human-readable design narrative — rationale, audience, style, color choices, content outline.
> Machine-readable execution contract: `spec_lock.md`. Executor re-reads `spec_lock.md` before every SVG page.

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | Agent评测_v6（PawBench Agent 评测方法论 + 实战评测案例） |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | 14 |
| **Design Style** | Swiss Minimal + Briefing |
| **Target Audience** | 技术团队、AI 架构师、企业决策者 — 正在评估 Agent 评测方案 |
| **Use Case** | 内部分享 / 技术选型汇报 |
| **Delivery Purpose** | `balanced` — 业务演示 + 可阅读，body 24px |
| **Content Strategy** | 平衡 — 基于 v5.5 素材组织（13 页继承），新增 1 页实战评测案例，不偏离原文事实 |
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

### Part 1: 背景与动机（继承 v5.5）

#### Slide 01 - Cover（anchor）

- **Cover impact**: Hero headline「基于 PawBench 的 Agent 评测」+ 三维交叉评测定位，accent rule 分割，页码 /14
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

#### Slide 03 - 主流 Agent 评测方法论全景（dense）

- **Layout**: 三列 × 两行六范式卡片网格，每卡：编号 + 范式名 + 核心思路 + 代表工具
- **Title**: 主流 Agent 评测方法
- **Core message**: 六大范式回答「怎么评」，主流评测体系普遍混合采用
- **Content**:
  - ① 最终状态评估（Final-State）— 确定性后端 + 最终产物/状态比对 — τ-bench / τ²-bench / AppWorld
  - ② 轨迹评估（Trajectory）— 黄金轨迹对齐或 LLM 评判轨迹质量 — LangSmith / AgentEvals
  - ③ LLM-as-a-Judge — 强模型 + Rubric 细则评分 — 通用开放任务
  - ④ 逐步评估（Stepwise）— 对每步独立校验（工具选择/参数/输出）— Arize Phoenix / DeepEval
  - ⑤ pass@k 采样 — k 次运行成功率 — Claw-Eval / CI 实践
  - ⑥ 沙箱环境模拟（Sandbox）— Docker 隔离 + 离线快照可复现 — GAIA / WebArena / OSWorld

#### Slide 04 - 主流 Agent 评测方案对比（dense）

- **Layout**: Full-width data table
- **Title**: 主流 Agent 评测方案对比
- **Content**: 9 个方案 × 维度（定位/评测对象/完整Agent/内网部署/扩展能力/资料生态/最佳场景）+ 评分说明

#### Slide 05 - PawBench 方法论 × 主流范式对比（dense）

- **Layout**: 左右对比 — 左「与主流同源」右「PawBench 独特设计」，底部结论条
- **Title**: PawBench 方法与主流范式对比
- **Core message**: PawBench 混合采用主流范式，并以 Model × Harness 交叉矩阵走出差异化

#### Slide 06 - PawBench 的优势（dense）

- **Layout**: 四核心优势卡 + 差异化条
- **Title**: PawBench 的 优势
- **Content**: 完整 Agent 评测 / 内网安全运行 / Model×Harness 交叉评测 / 开源可扩展

#### Slide 07 - PawBench 能力与评测设计（dense）

- **Layout**: 三步流程 + 七种能力 + 评分模式/覆盖场景/复杂度
- **Title**: PawBench 能力与评测设计
- **Content**: 核心设计理念 f(Model, Harness)；三步评测流程；七种能力诊断；评分模式（automated/llm_judge/hybrid）；4,050 评测单元

#### Slide 08 - 官方评测结果 · Model × Harness 评分矩阵（dense）

- **Layout**: 全宽图片 + 说明（image1.png）
- **Title**: PawBench 官方评测结果 · Model × Harness 评分矩阵
- **Content**: 全景 150 任务（文本+多模态）· 9 模型 × 3 Harness · Overall 综合得分

#### Slide 09 - 评测任务体系（dense）

- **Layout**: 任务来源表 + 五维标签
- **Title**: PawBench 评测任务体系
- **Content**: 150 道任务 × 6 源数据集；五维标签；标签赋能

#### Slide 10 - 任务执行与评分实战 · T053（dense）

- **Layout**: 四步链路 ①②③④
- **Title**: 任务执行与评分实战 · 以 T053 为例
- **Content**: 任务卡；① 沙箱执行 ② 结果采集 ③ 双重评分 hybrid ④ 汇总得分；混合惩罚机制

#### Slide 11 - 任务 ↔ 日常工作能力（dense）

- **Layout**: 表格
- **Title**: PawBench 任务 ↔ 日常工作能力
- **Content**: 8 行映射表 + 注

#### Slide 12 - 应用场景与集成方式（dense）

- **Layout**: 典型场景 + 集成方式 + 企业需求适配表
- **Title**: PawBench 应用场景与集成方式
- **Content**: 模型升级评估 / Agent 框架迭代 / 自定义 Skill 验证 / 回归测试流水线；集成方式；企业需求与能力适配表

### Part 2: 实战评测案例（v6 新增）

#### Slide 13 - 实战评测案例 · OpenClaw 4.14 vs 5.28（dense）

- **Layout**: 左「得分对比」（双版本卡 + 结论条）+ 右「根因分析」（四条证据链），底部数据来源
- **Title**: 实战评测案例 · OpenClaw 4.14 vs 5.28
- **Core message**: 「Agent 框架迭代」场景的真实落地 — 同一 LLM 下版本升级未带来收益，并可归因
- **Content**:
  - 评测条件：同一 LLM（QWen35-397b）× 同一任务集
  - 得分：4.14 = 68.1 / 66.0 / 70.3（avg 0.6774，错误可恢复 107 次）；5.28 = 60.3 / 61.2 / 59.7（avg 0.6144，恢复 0 次）
  - 结论条：平均分下降 6.3 分（0.6774 → 0.6144）
  - 根因 ① 输出流截断 15.8×（partialArgs 137 → 2,160，5.28 架构调整后高频）
  - 根因 ② 截断后不重试（4.14 重试至多 5 次成功恢复；5.28 失败即放弃）
  - 根因 ③ 错误类型三分（timed out / aborted / Context overflow 各约 30%，Context overflow 4.14 未见）
  - 根因 ④ 官方证据（openclaw/openclaw #87571 确认截断 tool call 不重试的架构缺陷）
  - 页脚：数据来源 PawBench 实测（同 LLM QWen35-397b）· penclaw-4.14-vs-5.28-analysis.md · 官方 PR #87571

#### Slide 14 - 总结（anchor）

- **Closing impact**: 三大收束点 + 一段结语（继承 v5.5 Slide 13）
- **Title**: 总结
- **Content**: 交叉评测矩阵 / 灵活可扩展 / 内网安全就绪；结语：Agent 评测正处于关键转折期，从主观判断转向标准化、自动化、多维度量化评测

---

## X. Speaker Notes Requirements

One speaker note file per page, saved to `notes/`:

- **Filename**: match SVG name
- **Content**: script key points, timing cues, transition phrases
