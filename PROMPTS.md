# 自动化科研准备 Skills 调用模板

本仓库面向“人类实操前准备”：先明确领域周期动态，再总结热点、趋势和现有不足，随后用 AI 辅助构思 idea 与规划实验路线。默认不运行实验、不训练模型、不自动写论文投稿。

## 1. 总控入口：让 auto-research 路由子技能

`auto-research` 是高层入口，适合你只描述目标，由它选择或串联下游 skill。

调用关系：

```text
auto-research
├── 信息获取层：research-daily / research-weekly / research-monthly
├── 长周期判断：research-yearly-hotwords / research-yearly-trends
├── 单篇深读：paper-trace
└── 研究准备层：research-gap-analysis → research-idea-planning → experiment-roadmap
```

常用模板：

```text
使用 $auto-research 调研“AI Agent 评测”，自动判断适合的调研粒度，输出中文 HTML 报告，并更新本地知识库。
```

```text
使用 $auto-research 对“空间音频大模型”做实操前准备：先看近一年趋势，再总结最近一周动态，最后给出研究缺口和可规划 idea，全部生成中文 HTML。
```

```text
使用 $auto-research 调研“多模态推理模型”，目标是为人类后续实验做准备。请覆盖热点、现有不足、可验证机会和下一步实验规划，不要运行实验。
```

## 2. 信息获取层：先建立事实底座

### 日调研：research-daily

用于今天或最近 24 小时的快速变化；适合追踪官方更新、突发论文、产品发布和社区信号。

```text
使用 $research-daily 查询“视频生成模型评测”今天最新动态，要求列出来源、时间、可信度和潜在影响。
```

```text
使用 $research-daily 调研“OpenAI API”最近 24 小时变化，区分官方更新、社区信号和待验证消息。
```

### 周调研：research-weekly

用于最近 7 天领域周报；适合每周固定巡检论文、开源项目、产品和产业动态。周报可嵌入区间内重点论文的 `paper-trace`。

```text
使用 $research-weekly 调研“AI Agent 评测”最近一周动态，输出中文 HTML 周报，并更新 knowledge_base。
```

```text
使用 $research-weekly 生成“空间音频大模型”最近一周调研报告，按论文、开源项目、产业动态、风险和后续追踪问题分类。
```

### 月调研：research-monthly

用于最近 30 天阶段性综述；适合判断一个方向是否形成稳定趋势。

```text
使用 $research-monthly 调研“端侧多模态大模型”最近一个月论文、项目和产业动态，生成中文 HTML 报告。
```

```text
使用 $research-monthly 复盘“多智能体协作框架”最近一个月进展，总结核心趋势、代表项目、争议点和下月追踪问题。
```

### 候选来源采集增强

适合先用无密钥公共 API 建立候选来源池，再做人工或 Agent 复核。

```text
使用 $auto-research 调研“AI Agent 评测”最近一周动态。请先用内置候选来源采集脚本检索 arXiv、OpenAlex 和 GitHub，再补充官方博客/新闻来源，最后生成中文 HTML 报告并更新本地知识库。
```

```text
使用 $research-monthly 调研“多模态智能体”最近一个月进展。要求先生成候选来源 JSONL，复核后只引用能支撑结论的论文、仓库和官方来源。
```

## 3. 长周期判断层：找热点与趋势

### 近一年研究热词：research-yearly-hotwords

用于提取关键词、方法名、数据集名、benchmark、任务设置和增长信号。

```text
使用 $research-yearly-hotwords 分析“语音大模型”近一年研究热词，按证据强度、增长信号和研究启发排序。
```

```text
使用 $research-yearly-hotwords 分析“自动驾驶世界模型”近一年热词，要求给出每个热词的含义、代表来源、别名和后续检索 query。
```

### 近一年研究趋势：research-yearly-trends

用于战略判断、选题规划和研究路线分析。

```text
使用 $research-yearly-trends 分析“具身智能大模型”近一年研究趋势、机会和风险，生成中文 HTML 趋势报告。
```

```text
使用 $research-yearly-trends 调研“世界模型”近一年发展方向，区分真实趋势、短期热点和证据不足的推测。
```

## 4. 单篇深读层：paper-trace

`paper-trace` 用于你已经对某篇论文感兴趣的场景。它应输出中文 HTML，分析技术脉络、相对前作差异、实验协议、复现风险和后续追踪 query。报告文件名使用方法简写或短标题，不用日期前缀。

```text
使用 $paper-trace 分析 arXiv:2606.13095，生成中文 HTML，重点说明它继承了哪些前置技术、相对前作的差异和复现风险。
```

```text
使用 $paper-trace 分析 https://arxiv.org/pdf/2606.11795，生成中文 HTML。请自动判断论文所属主题并归类存储，报告名使用方法简写或短标题。
```

```text
使用 $paper-trace 对论文 “Balancing ASR and diarization in end-to-end LLMs for multi-talker speech recognition” 做技术溯源分析，并给出后续追踪 query。
```

与其它技能组合：

```text
使用 $paper-trace 分析 arXiv:xxxx.xxxxx 后，再基于该论文暴露的问题调用 $research-idea-planning，生成 3 个可验证研究 idea。
```

## 5. 研究准备层：从不足到实验路线

### 研究缺口分析：research-gap-analysis

用于从趋势、周报、月报或单篇论文中抽取现有不足、数据缺口、评测瓶颈、可验证机会和风险。

```text
使用 $research-gap-analysis 分析“AI Agent 长程任务评测”的研究缺口，基于近一年论文、benchmark 和开源项目，输出中文 HTML。
```

```text
使用 $research-gap-analysis 基于已有“空间音频大模型”周报和 paper-trace，整理当前方法的不足、缺失评测和可落地改进机会。
```

### 研究 idea 规划：research-idea-planning

用于生成、筛选和排序 idea。外部 `idea-creator`、`idea-discovery`、`novelty-check` 的能力在本仓库中优先折叠到这个 skill：既要发散，也要做证据约束和初步查新。

```text
使用 $research-idea-planning 针对“多模态智能体评测”生成 5 个研究 idea。每个 idea 需要包含核心假设、相关证据、可能创新点、初步 novelty check、最小验证实验和风险。
```

```text
使用 $research-idea-planning 基于上一份 gap-analysis 报告，筛选 3 个最值得人类投入实验的 idea，并按新颖性、可验证性、成本和失败风险排序。
```

### 实验路线图：experiment-roadmap

用于把选中的 idea 转成 claim-driven 的实验规划；只规划，不执行。

```text
使用 $experiment-roadmap 将 idea“用过程级轨迹一致性评估长程 Agent”转成实验路线图，包含主张、baseline、ablation、指标、数据、运行顺序、停止条件和风险。
```

```text
使用 $experiment-roadmap 基于上一份 idea-planning 报告中排名第一的 idea，规划人类接下来两周可以执行的最小实验闭环，不要运行实验。
```

## 6. 推荐组合流程

### 周期巡检 → 重点深读 → 缺口

适合每周或每月固定维护领域认知。

```text
使用 $auto-research 对“音频语言模型”执行三阶段调研：
1. 生成最近一周动态周报；
2. 对区间内最值得关注的论文执行 paper-trace；
3. 基于周报和论文溯源总结研究缺口。
全部输出中文 HTML，并更新本地知识库。
```

### 长周期趋势 → 缺口 → idea → 实验路线

适合从零进入一个方向，最终形成可交给人类执行的实验计划。

```text
使用 $auto-research 对“具身智能大模型评测”做实操前准备链路：
1. 分析近一年研究趋势；
2. 总结关键热词和代表来源；
3. 做研究缺口分析；
4. 生成并排序研究 idea；
5. 为排名第一的 idea 生成实验路线图。
所有阶段都生成中文 HTML，不要运行实验。
```

### 单篇论文 → 领域机会

适合你读到一篇高兴趣论文，想知道能否扩展成自己的方向。

```text
使用 $auto-research 围绕 arXiv:xxxx.xxxxx 做论文驱动选题：先调用 paper-trace 做技术溯源，再围绕它的限制调用 research-gap-analysis，最后调用 research-idea-planning 生成 3 个可验证 idea。
```

### 热词 → 检索式 → 周期追踪

适合建立后续持续监控 query。

```text
使用 $research-yearly-hotwords 分析“世界模型”近一年热词，并把每个热词转化为后续 weekly/monthly 可复用的检索 query。
```

## 7. 输出要求增强

可追加到任意指令后面：

```text
报告需要包含：核心判断、代表来源、风险与限制、下一步查询建议，并确保每个事实性判断都有来源链接。
```

```text
报告面向科研选题，请重点分析可做的研究空白、数据/评测瓶颈、失败风险和未来 3 个月值得跟踪的问题。
```

```text
报告面向工程落地，请重点分析可复现项目、产品动态、部署风险、短期可验证机会和不建议投入的方向。
```

```text
请保留英文方法名、模型名、数据集名和 benchmark 名称；中文解释其作用、证据强度和局限。
```

## 8. 当前不纳入核心链路的外部 skill

这些外部 skill 对科研全流程有价值，但不符合本仓库当前“人类实操前准备”的边界，暂不作为核心 skill 纳入：

- 实验执行与算力调度：`run-experiment`、`experiment-bridge`、`experiment-queue`、`monitor-experiment`、`training-check`、`vast-gpu`、`serverless-modal`。
- 自动论文写作与投稿闭环：`paper-write`、`paper-writing`、`paper-compile`、`auto-paper-improvement-loop`、`rebuttal`、`resubmit-pipeline`。
- 审稿与结果审计后处理：`paper-claim-audit`、`citation-audit`、`experiment-audit`、`kill-argument`、`research-review`。
- 专利和法域流程：`prior-art-search`、`patent-*`、`jurisdiction-format`。
- 展示产物生成：`paper-slides`、`paper-poster`、`figure-spec`、`mermaid-diagram`、`paper-illustration`，仅在未来需要汇报材料时再考虑。

可以未来增强但暂不新增独立 skill 的方向：

- `research-wiki` / `wiki-enrich`：更适合作为现有 `knowledge_base/` 的持久化图谱增强，而不是新增平行入口。
- `novelty-check`：当前放入 `research-idea-planning` 的 idea 评估维度。
- `formula-derivation`：适合理论型方向，未来可作为可选准备层补充。
- `paper-plan` / `grant-proposal`：偏写作与申请书，不属于当前实操前实验准备主链路。

## 9. 共享支撑层：auto-research-common

通常不需要直接调用 `auto-research-common`。它负责统一来源策略、报告 schema、HTML 模板、渲染脚本、导航区块和 knowledge_base 更新。

只有在调试或校验时直接使用：

```text
使用 $auto-research-common 校验 examples 中的报告 JSON 是否符合 schema，并渲染一个 HTML 示例。
```
