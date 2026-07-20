# Outline — Agent评测（更新版，7 页）

> 目标：在原有 6 页基础上插入 1 页「任务执行与评分实战（以 T053 为例）」，插在第 4 页（评测任务体系）之后。
> 风格沿用原 deck 身份：1280×720、白底、深蓝 #1E3A8A、微软雅黑+Arial、无渐变、绿/红点缀、星标评分、页脚 0X/07。

## Slide 1 — 为什么需要 Agent 评测
- 主标题 + 副标题：两大核心痛点驱动 Agent 评测需求，PawBench 提供标准化解法
- 两列痛点→解法对照：升级效果无法量化；现有方案局限（通用榜单不评工具调用、学术 Benchmark 依赖公网）
- 底部价值条：量化升级效果 / 精准定位短板 / 内网安全运行

## Slide 2 — 主流 Agent 评测方案对比
- 对比表：工具 / 定位 / 评测对象 / 关键维度评分 / 优势 / 劣势 / 最佳场景
- 覆盖 PawBench / WildClawBench / SkillsBench / PinchBench / AgentBench / GAIA / SWE-bench / DeepEval / Promptfoo
- 评分用 ★ 星标（优★★★★★ / 良★★★★ / 弱★★）；底部数据来源说明

## Slide 3 — PawBench 能力与评测设计
- 核心公式：Agent 表现 = f(Model, Harness)
- 三步评测流程：① 选择模型与 Harness 组合 ② Docker 沙箱隔离运行 ③ 自动+LLM 双重评分
- 七维原子能力：Tool_Use / Skill_Use / Code_Manipulation / Logic_Reasoning / Planning / Math_Computation / Self_Verification
- 评分模式：automated / llm_judge / hybrid；复杂度 L1/L2/L3；9 模型×3 Harness×150 任务=4050 单元

## Slide 4 — PawBench 评测任务体系
- 150 道任务 × 6 源数据集 × 五维标签体系
- 来源表：自建 21 / claweval 52 / qwenclawbench 29 / pinchbench 23 / skillsbench 15 / wildclawbench 10
- 五维标签：scenario / capabilities / complexity / modality / environment
- 底部：按场景/能力/复杂度三种切片分析用法

## Slide 5 —【新增】任务执行与评分实战 · 以 T053 为例
- 目标：用一个真实任务讲清「任务如何被执行、结果如何被分析、得分如何产生」
- 任务卡（T053）：来源 pinchbench｜类型 内容创作｜指令「写 500 词《远程办公对开发者好处》博客并存为 blog_post.md」｜无外部依赖
- 横向四段流程（执行→采集→评分→汇总）：
  1. 沙箱执行：Agent 在 Docker 容器中运行，纯文本生成
  2. 结果采集：harness 把 OpenClaw session 归一化为 transcript 事件流，并把新生成文件内容注入 transcript；产物落盘 workspace_path
  3. 双重评分（hybrid，自动 0.6 + LLM 0.4）：
     - 自动检查：文件存在 / 词数 450–550→1.0 / 有标题结构 / 含 remote·dev 关键词
     - LLM 评判：内容质量 / 结构 / 写作 / 词数达标 / 完成度 五维
  4. 汇总得分：score = 0.6×自动 + 0.4×LLM，<0.75 触发混合惩罚机制
- 页脚点题：一个任务卡 = Prompt + Expected Behavior + 自动检查 + LLM Rubric，对框架中立

## Slide 6 — PawBench 应用场景与集成方式
- 典型场景：模型升级评估 / Agent 框架迭代 / 自定义 Skill 验证 / 回归测试流水线
- 集成：Docker 一键部署 / 内网适配 / OpenJudge 自定义 Task·Judge·Runner
- 企业需求→能力对照表（内网私有化 / 完整 Agent / 自定义扩展 / Skill 评估 / 量化回归）

## Slide 7 — 总结
- 三栏：交叉评测矩阵 / 灵活可扩展 / 内网安全就绪
- 底部要点 + 署名信息（阿里通义实验室 AgentScope、Apache 2.0、9×3×150=4050 单元）
