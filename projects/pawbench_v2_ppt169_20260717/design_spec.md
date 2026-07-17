# pawbench_v2 - Design Spec

> Human-readable design narrative — rationale, audience, style, color choices, content outline.

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | pawbench_v2 |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | 7 |
| **Design Style** | swiss-minimal |
| **Target Audience** | 技术团队 + 决策者 |
| **Use Case** | 产品简报 — PawBench 企业级 Agent 评测平台介绍 |
| **Delivery Purpose** | `balanced` 商务演示 |
| **Content Strategy** | 整合精简版+详细版+工具对比表，去掉OpenJudge和"失败归因困难" |
| **Created Date** | 2026-07-17 |

---

## II. Canvas Specification

| Property | Value |
| -------- | ----- |
| **Format** | PPT 169 |
| **Dimensions** | 1280×720 |
| **viewBox** | `0 0 1280 720` |
| **Margins** | left/right 60px, top 50px, bottom 40px |
| **Content Area** | 1160×630 |

---

## III. Visual Theme

### Theme Style

- **Mode**: briefing
- **Visual style**: swiss-minimal
- **Theme**: Light theme
- **Tone**: tech, professional, modern, professional

### Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#FFFFFF` | Page background |
| **Secondary bg** | `#F2F5FA` | Card background, section background |
| **Primary** | `#1E3A8A` | Title decorations, key sections, icons, header bar |
| **Accent** | `#2563EB` | Data highlights, key information, links |
| **Secondary accent** | `#93C5FD` | Secondary emphasis |
| **Body text** | `#1A1A2E` | Main body text |
| **Secondary text** | `#64748B` | Captions, annotations |
| **Tertiary text** | `#94A3B8` | Supplementary info, footers |
| **Border/divider** | `#E2E8F0` | Card borders, divider lines |
| **Success** | `#10B981` | Positive indicators |
| **Warning** | `#EF4444` | Issue markers |

---

## IV. Typography System

### Font Plan

**Typography direction**: modern CJK sans

| Role | Chinese | English | Fallback tail |
| ---- | ------- | ------- | ------------- |
| **Title** | `"Microsoft YaHei"` | `Arial` | `sans-serif` |
| **Body** | `"Microsoft YaHei"` | `Arial` | `sans-serif` |
| **Emphasis** | — | `Arial` | `sans-serif` |
| **Code** | — | `Consolas, "Courier New"` | `monospace` |

**Per-role font stacks**:
- Title: `"Microsoft YaHei", Arial, sans-serif`
- Body: `"Microsoft YaHei", Arial, sans-serif`
- Emphasis: same as Body
- Code: `Consolas, "Courier New", monospace`

### Font Size Hierarchy

**Baseline (unitless px)**: Body = 24

| Purpose | Size (px) | Weight |
| ------- | --------- | ------ |
| Cover title | 80 | Bold |
| Page title | 40 | Bold |
| Subtitle | 28 | Regular |
| **Body content** | **24** | Regular |
| Annotation / table body | 18 | Regular |
| Page number / footnote | 14 | Regular |

---

## V. Layout Principles

### Page Structure

- **Header area**: Title bar with deep blue left accent, page number + title
- **Content area**: Flexible grid, Swiss-modular
- **Footer area**: Thin divider line + page number

### Spacing

| Element | Value |
| ------- | ----- |
| Canvas margin | 60px |
| Content block gap | 32px |
| Icon-text gap | 12px |
| Card padding | 24px |
| Card gap | 24px |
| Card border radius | 0 (Swiss sharp) |

---

## VI. Icon Usage

| Purpose | Icon Path | Page |
| ------- | --------- | ---- |
| Pain point / warning | `chunk-filled/warning-triangle` | P02 |
| Check / solution | `chunk-filled/circle-checkmark` | P02 |
| Rocket / launch | `chunk-filled/rocket` | P07 |
| Code / dev | `chunk-filled/code` | P04 |
| Chart / benchmark | `chunk-filled/chart-bar` | P03 |
| Database / data | `chunk-filled/database` | P05 |

---

## IX. Content Outline

### Slide 01 - Cover

- **Cover impact**: "Agent 表现 = f(Model, Harness)" core formula as the provocative hook — a typographic poster layout with bold deep-blue zone + formula highlight
- **Layout**: Asymmetric split — left 40% deep blue column with title, right 60% white with formula hero and metadata
- **Title**: PawBench
- **Subtitle**: Agent 评测新范式 — Model × Harness 交叉评测基准
- **Info**: 阿里通义实验室 AgentScope 团队 | 2025

### Slide 02 - 为什么需要 Agent 评测

- **Title**: 为什么需要 Agent 评测
- **Core message**: 两大核心痛点驱动 Agent 评测需求，PawBench 提供标准化解法
- **Content**:
  - 升级效果无法量化：模型/Agent 升级后效果好坏依赖 cherry-pick 案例，无法形成决策依据 → PawBench：150 道标准化任务 + 自动评分，跑完出分可对比
  - 现有方案局限：通用 LLM 榜单不测工具调用，学术 Benchmark 依赖公网无法内网部署 → PawBench：开源 + Docker 沙箱，完全私有化部署，数据不出网

### Slide 03 - 主流 Agent 评测方案对比

- **Title**: 主流 Agent 评测方案对比
- **Core message**: 9 款工具完整横向对比，PawBench 是唯一同时评估 Model + Harness + Task 的完整 Agent 评测平台
- **Content**: 9工具对比表（不含OpenJudge）：PawBench / WildClawBench / SkillsBench / PinchBench / AgentBench / GAIA / SWE-bench / DeepEval / Promptfoo
  - 列：工具 | 定位 | 评测对象 | 完整Agent | 内网运行 | 扩展能力 | 适用场景
  - 底部补充：现有 Benchmark 局限说明 + 关键发现

### Slide 04 - PawBench 核心特性

- **Title**: PawBench 核心特性
- **Core message**: 三维交叉矩阵 + 三步入式评测 + 七维能力诊断，构成完整评测体系
- **Content**:
  - 核心公式：Agent 表现 = f(Model, Harness)
  - 三维矩阵：9 模型 × 3 Harness × 150 任务 = 4,050 评测单元
  - 评测流程：选择模型与Harness → Docker沙箱隔离运行 → 自动+LLM双重评分
  - 7大能力：Tool_Use / Skill_Use / Code_Manipulation / Logic_Reasoning / Planning / Math_Computation / Self_Verification
  - 5大场景：办公协同 / 软件工程 / 数据分析 / 信息检索 / 自动化脚本
  - 3级复杂度：L1(1-2步) / L2(3-5步) / L3(5步以上含分支)

### Slide 05 - 评测任务体系

- **Title**: 评测任务体系
- **Core message**: 6个来源150道任务 + 五维标签体系，支持精细化切片分析
- **Content**:
  - 任务来源表：自建任务21 | claweval 52 | qwenclawbench 29 | pinchbench 23 | skillsbench 15 | wildclawbench 10
  - 五维标签：应用场景(scenario) / 原子能力(capabilities) / 复杂度(complexity) / 输入模态(modality) / 运行环境(environment)

### Slide 06 - 应用场景与集成路径

- **Title**: 应用场景与集成路径
- **Core message**: 4大典型应用场景 + 三阶段集成路径，快速落地
- **Content**:
  - 4大典型场景：模型升级评估 / Agent框架迭代 / 自定义Skill验证 / 回归测试流水线
  - 价值适配表：需求 vs PawBench 能力对照
  - 三阶段路径：Phase1(2周)部署环境 → Phase2(2周)适配内网 → Phase3(持续)嵌入迭代

### Slide 07 - 选择 PawBench

- **Closing impact**: 唯一交叉评测平台 + 开源生态可扩展 + 企业就绪内网安全 — 三句话收尾
- **Layout**: Center-weighted closing layout — 3 key value cards + GitHub CTA
- **Content**: 总结3个核心价值 + GitHub 链接 + 社区信息
