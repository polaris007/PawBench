# 09 评测任务体系 - 演讲备注

**时长建议**: 90 秒

**讲解要点**:
- 150 道任务来自 6 个源数据集：自建 21、claweval 52、qwenclawbench 29、pinchbench 23、skillsbench 15、wildclawbench 10。
- 五维标签体系：场景 scenario、能力 capabilities（Logic/Math/Code/Tool/Skill/Plan/Verify 七类）、复杂度 complexity（L1 1-2 步 / L2 3-5 步 / L3 5+ 含分支）、输入模态 modality（text / multimodal）、运行环境 environment（closed 离线复现 / open 需联公网）。
- 五维标签如何赋能：按场景分类对比（排除噪声）、按能力定向诊断（精准定位短板）、按复杂度分层评估（识别多步推理退化点）。
- 每道任务 5 维标签可任意组合筛选，灵活构建定制化评测维度。

**过渡语**:
抽象体系之外，看一个具体任务怎么跑完整个链路。
