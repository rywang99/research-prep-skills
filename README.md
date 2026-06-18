# research-prep-skills

面向 Codex 和 Claude Code 的自动化调研 skills 库，用于把一个研究主题转换为可追踪的日/周/月报、近一年热词/趋势分析、研究缺口、idea 规划或实验路线图，并输出自包含中文 HTML 报告。

## 使用示例

在 Codex 中可以直接按 `$skill-name` 调用；在 Claude Code 中使用对应 slash command，例如 `/auto-research`、`/research-yearly-full-cycle`。

```text
使用 $auto-research 调研“空间音频大模型”最近一周的研究和产业动态，生成中文 HTML 报告，并更新本地知识库。
```

```text
使用 $research-yearly-trends 分析“具身智能大模型”近一年研究趋势、机会和风险，生成中文 HTML 趋势报告。
```

```text
使用 $paper-trace 分析论文 arXiv:2606.13095 的技术脉络、实验协议和复现风险，生成中文 HTML。
```

```text
使用 $research-gap-analysis 分析“空间音频大模型”的现有不足和可验证机会，生成中文 HTML。
```

```text
使用 $research-idea-planning 基于“空间音频大模型”的缺口报告构思 5 个可发表 idea，并排序。
```

```text
使用 $experiment-roadmap 为 Cross-Format Spatial Token Alignment 规划实验验证路线，不运行实验。
```

```text
使用 $formula-derivation 为 Cross-Format Spatial Token Alignment 整理变量、假设、推导步骤和 sanity checks，不运行实验。
```

```text
使用 $research-yearly-full-cycle 对“AI Agent 评测”做最近 365 天的全流程调研，按月度切片、全年趋势、缺口、idea、路线图和独立评分输出中文 HTML，并使用 Codex goal 跟踪总任务。
```

```text
使用 $research-independent-evaluator 独立评分 reports/ai-agent-evaluation/idea_planning_v1.json，给出 rubric 分数、阻塞问题和必要迭代建议，不改写原报告。
```

更多提示词示例见 `PROMPTS.md`。

## 能力概览

- `auto-research`：总控入口，按用户意图自动路由到合适的调研模式。
- `research-daily`：今日或最近 24 小时动态追踪，默认不生成研究热词/趋势聚类。
- `research-weekly`：最近 7 天论文、开源项目、产品和产业信号周报，默认不生成研究热词/趋势聚类。
- `research-monthly`：最近 30 天阶段性综述。
- `research-yearly-hotwords`：近一年研究热词、增长信号和代表证据分析。
- `research-yearly-trends`：近一年趋势聚类、驱动因素、机会和风险分析。
- `research-gap-analysis`：总结领域现有不足、评价瓶颈、数据缺口和可验证机会；宽口径/全年请求默认保留 8-15 个多类型缺口。
- `research-idea-planning`：基于调研证据生成和排序研究 idea，不运行实验；宽口径/全年请求默认保留 10-20 个发散候选。
- `experiment-roadmap`：把选定 idea 转成 claim-driven 实验路线图，不创建或提交实验任务。
- `formula-derivation`：为理论型方向整理变量、假设、推导步骤和验证条件，不声称自动证明。
- `paper-trace`：针对单篇论文生成技术溯源、重点阅读信号和复现风险 HTML。
- `research-yearly-full-cycle`：编排全年月度切片、热词/趋势、缺口、idea、实验路线/公式准备、独立评分和必要迭代。
- `research-independent-evaluator`：独立读取已保存产物并按 rubric 评分，不在同一 pass 中改写被评报告。
- `scripts/collect_sources.py`：从无密钥公共 API 采集候选来源，生成可复用 JSONL。
- `scripts/trace_report_papers.py`：为日/周调研自动嵌入所有区间内文献的展开 trace。
- `scripts/archive_reports.py`：把长期累积的 dated 报告移动到 `archive/YYYY/MM/<mode>/` 并生成主题索引。
- `scripts/query_knowledge_base.py`：查询本地 `knowledge_base/` 中的实体和关系图谱。
- `scripts/common_utils.py`：仓库级脚本共用的轻量 JSON、时间和 slug 工具。

## 目录结构

```text
.agents/skills/auto-research/              # 调研总控 skill
.agents/skills/research-*/                 # 各调研模式的 skill 指令
.agents/skills/formula-derivation/         # 理论准备与公式推导规划 skill
.agents/skills/paper-trace/                # 单篇论文技术溯源 skill
.agents/skills/research-yearly-full-cycle/ # 全年全流程调研、评分和迭代编排 skill
.agents/skills/research-independent-evaluator/ # 独立评分与质量门控 skill
.agents/skills/auto-research-common/       # 共享配置、模板、schema、渲染脚本
.claude/skills/                            # Claude Code 项目级 skills 镜像，由脚本生成
CLAUDE.md                                  # Claude Code 项目记忆入口
examples/                                  # 示例报告和采集结果 fixture
scripts/                                   # 仓库级采集、查询、校验和脚手架工具
reports/                                   # 本地生成的 HTML/JSON 报告，默认不入库
knowledge_base/                            # 本地调研知识库与轻量图谱，默认不入库
```

## 快速开始

校验 skills、配置和渲染流程：

```bash
python3 scripts/validate_skills.py
```

同步 Claude Code 项目 skills：

```bash
python3 scripts/sync_claude_skills.py
```

只检查 Claude Code 镜像是否最新：

```bash
python3 scripts/sync_claude_skills.py --check
```

渲染示例报告：

```bash
python3 .agents/skills/auto-research-common/scripts/render_report.py \
  --input examples/minimal_report.json \
  --output reports/demo/demo_weekly.html \
  --update-kb
```

采集候选来源：

```bash
python3 scripts/collect_sources.py \
  --topic "automated research agent" \
  --query "automated research agent" \
  --sources arxiv,openalex,github \
  --window-days 30 \
  --limit-per-source 5 \
  --output /tmp/collected_sources.jsonl
```

采集脚本默认使用 arXiv、OpenAlex 和 GitHub Search 等无密钥来源；如设置 `GITHUB_TOKEN`，GitHub 请求限额会更高。未传 `--output` 时，结果写入 `knowledge_base/<topic_slug>/collected_sources.jsonl`。

单篇论文技术溯源：

```bash
python3 scripts/trace_single_paper.py \
  --paper "2606.13095" \
  --topic "多说话人语音识别"
```

周报/日报在渲染前自动执行论文 trace：

```bash
python3 scripts/trace_report_papers.py \
  --report reports/<topic_slug>/YYYY-MM-DD_weekly.json
```

论文 trace 会以默认 `--jobs 8` 并发执行，并嵌入 HTML 的展开区块；不会缓存 PDF，也不会写回 PDF 注释。

查询本地知识库图谱：

```bash
python3 scripts/query_knowledge_base.py \
  --topic spatial-audio-llm \
  --type idea \
  --limit 5
```

整理长期累积的报告目录：

```bash
# 先查看移动计划，不改动文件
python3 scripts/archive_reports.py \
  --topic multi-speaker-speech-recognition \
  --dry-run

# 确认后移动到 reports/<topic_slug>/archive/YYYY/MM/<mode>/
python3 scripts/archive_reports.py \
  --topic multi-speaker-speech-recognition \
  --apply
```

归档脚本默认输出摘要；需要完整 move plan/result 时追加 `--json`。如果归档后需要同步修复知识库历史运行记录中的旧报告路径，可追加 `--repair-kb-paths`。

新增调研模式示例：

```bash
python3 scripts/new_research_mode.py quarterly \
  --label 季度调研 \
  --window-days 90 \
  --description "最近 90 天阶段性趋势复盘"
```

## 输出与隐私

- 默认报告路径：`reports/<topic_slug>/YYYY-MM-DD_<mode>.html`。
- 长期或重复调研可在渲染时追加 `--archive-output`，将匹配的 HTML/JSON 报告移动到 `reports/<topic_slug>/archive/YYYY/MM/<mode>/`，并让 `--update-kb` 记录归档后的最终 HTML 路径。
- 已累积的报告可用 `scripts/archive_reports.py --topic <topic_slug> --apply` 批量归档；脚本默认不删除文件，`paper-trace` 目录默认跳过；加 `--repair-kb-paths` 可把 `knowledge_base/<topic_slug>/runs.jsonl` 中归档前的旧 `report_path` 修正到索引里的归档路径。
- 单篇论文 trace 默认路径：`reports/paper-trace/<category_slug>/<method_slug>.html`。
- 默认知识库路径：`knowledge_base/<topic_slug>/`，其中 `entities.jsonl`、`links.jsonl`、`graph_latest.json` 是 research-wiki/wiki-enrich 风格的轻量图谱增强；当前 schema version 为 `1.0`。
- `reports/*` 和 `knowledge_base/*` 已在 `.gitignore` 中忽略，只保留 `.gitkeep` 占位文件，避免把个人调研报告、来源列表、运行记录提交到 Git。
- 不要提交 API Key、浏览器 Cookie、私有源导出或其他敏感材料。

## 开发约定

- 新模式统一注册到 `.agents/skills/auto-research-common/config/research_modes.json`。
- `.agents/skills/` 是 skill 源目录；`.claude/skills/` 是 Claude Code 生成镜像，不要手改。
- 修改任何 skill 后运行 `python3 scripts/sync_claude_skills.py` 和 `python3 scripts/validate_skills.py`。
- 候选来源采集优先通过 `scripts/collect_sources.py` 生成 JSONL，再由 Agent 复核关键来源并整理成报告 JSON。
- 报告 JSON 字段应遵循 `.agents/skills/auto-research-common/references/report_schema.md`。
- 来源引用和可信度判断遵循 `.agents/skills/auto-research-common/references/source_policy.md`。
- Python 脚本优先使用标准库，保持依赖轻量。
- 仓库级脚本的通用时间、slug、JSONL 辅助逻辑优先放在 `scripts/common_utils.py`；skill 内部脚本仍需保持可独立运行。
- 修改 schema、模板、知识库图谱或渲染行为后，更新 `examples/` fixture 并运行 `python3 scripts/validate_skills.py`。
