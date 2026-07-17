# PawBench 简介 - Design Spec

> Human-readable design narrative — rationale, audience, style, color choices, content outline.
> Machine-readable execution contract: `spec_lock.md`. Executor re-reads `spec_lock.md` before every SVG page.

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | PawBench 简介 |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | 5 |
| **Design Style** | Swiss Minimal + Briefing |
| **Target Audience** | 技术团队、AI 架构师、企业决策者 — 正在评估 Agent 评测方案 |
| **Use Case** | 内部分享 / 技术选型汇报 |
| **Delivery Purpose** | `balanced` — 业务演示 + 可阅读，body 24px |
| **Content Strategy** | 平衡 — 基于素材组织，合理提炼，不偏离原文事实 |
| **Created Date** | 2025-07-17 |

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

*No icons used in this deck — 5 pages are text/tables driven, Swiss minimal aesthetic.*

---

## VII. Visualization Reference List

*Not applicable — no data charts in this deck.*

---

## VIII. Image Resource List

*Not applicable — no images in this deck (\(image\_usage: none\)).*

---

## IX. Content Outline

### Part 1: Agent 评测背景

#### Slide 01 - Cover

- **Cover impact**: Hero headline "PawBench" at architectural scale + subtitle "Agent 评测新范式", a single horizontal accent rule dividing title block from bottom info line
- **Layout**: Single column centered, oversized title occupies upper 60%, thin accent rule, subtitle and info below
- **Title**: PawBench
- **Subtitle**: Agent 评测新范式 — Model × Harness 交叉评测基准
- **Info**: 阿里通义实验室 AgentScope 团队 | 2025

#### Slide 02 - 为什么需要 Agent 评测

- **Layout**: Asymmetric split — left 40% vertical accent bar with section label, right 60% three KPI cards
- **Title**: 为什么需要 Agent 评测
- **Core message**: Agent 系统升级缺乏量化手段和归因能力，现有 Benchmark 难以满足企业需求
- **Content**:
  - **痛点一：升级效果无法量化** — 从模型升级到 Agent 框架迭代，效果好坏依赖 cherry-pick 案例
  - **痛点二：失败归因困难** — 任务失败了，不知道是模型能力不足、Harness 调度问题还是工具调用失败
  - **痛点三：现有方案局限** — 通用 LLM 榜单不测工具调用；学术 Benchmark 依赖公网无法内网部署

### Part 2: 工具对比

#### Slide 03 - 主流 Agent 评测方案对比

- **Layout**: Full-width data table with alternating row backgrounds (secondary_bg / white), header row with primary background
- **Title**: 主流 Agent 评测方案对比
- **Core message**: PawBench 是唯一同时评估 Model + Harness + Task 完整 Agent 系统的评测平台
- **Content**:
  - 对比表：PawBench / OpenJudge / WildClawBench / AgentBench / GAIA / SWE-bench
  - 对比维度：定位 / 评测对象 / 完整 Agent / 内网运行 / 扩展能力 / 生态
  - 关键发现：PawBench 在企业内网部署和完整 Agent 系统评估上优势明显

### Part 3: PawBench 特性

#### Slide 04 - PawBench 核心特性

- **Layout**: Three column cards, each with icon area + title + bullet points
- **Title**: PawBench 核心特性
- **Core message**: Model × Harness 交叉矩阵 + 标准化评测流程 + 原子能力诊断
- **Content**:
  - **交叉评测矩阵**：9 模型 × 3 Harness × 150 任务 = 4,050 个评测单元，精准定位瓶颈在模型还是框架
  - **三步入式评测**：选模型+Harness → Docker 沙箱隔离运行 → 自动 + LLM 双重评分
  - **七维能力诊断**：原子能力切片分析 — Tool_Use、Code_Manipulation、Logic_Reasoning 等

#### Slide 05 - 为什么选择 PawBench

- **Layout**: Asymmetric — left side three stacked value cards, right side integration roadmap timeline
- **Title**: 为什么选择 PawBench
- **Core message**: PawBench 是企业 Agent 评测的首选平台 — 开源、内网可用、可扩展、持续维护
- **Content**:
  - **唯一交叉评测**：同时评估模型 + Harness + 任务，适合既自研 Agent 又调优模型的团队
  - **开源生态**：基于 OpenJudge，可自定义任务和 Judge，社区由阿里通义实验室持续维护
  - **企业就绪**：Docker 内网部署、数据不出网、CI 流水线集成

---

## X. Speaker Notes Requirements

One speaker note file per page, saved to `notes/`:

- **Filename**: match SVG name
- **Content**: script key points, timing cues, transition phrases
