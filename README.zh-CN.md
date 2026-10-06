# Scientific Research Plugin

[English](README.md) | **简体中文**

![License](https://img.shields.io/badge/license-MIT-green)
![Skills](https://img.shields.io/badge/skills-12_+_2_subagents-blue)
![Harnesses](https://img.shields.io/badge/harnesses-16-orange)

每个研究任务都从先例调研开始，论文只是最完整的实例。`research-before-build` 调研技能在研究级问题动手前，工程与学术双源并行查先例；论文管线——文献获取 → 结构化阅读 → 论文出图 → 章节起草 → 写作润色 → 参考文献核查 → 投稿前评审 → 审稿回复 → 会议汇报——是它的完整落地。面向运筹学与机器学习研究者。

一份 `skills/` 事实源，多端分发：Claude Code / ZCode / Codex 插件、原生读取 `~/.agents/skills` 的助手（Gemini CLI、Goose、opencode、Kimi Code、pi），以及由 `install.sh` 扇出到各自专属目录的 Harness（Cursor、Crush、Copilot、Amp、Grok Build、Qwen Code、Droid、Kiro）。

## 亮点

- **一套技能包覆盖全生命周期。** 从一份原始文献清单到会议演讲：Zotero 入库 → 结构化阅读笔记 → 按笔记的 PDF 分类高亮 → 期刊级出图 → 顶刊风格章节起草 → LaTeX 润色 → 名词术语黑话审查 → 引用核查 → 对抗式投稿前评审 → 逐条审稿回复 → 控时 Beamer 幻灯。12 个技能 + 2 个 subagent 按一条管线设计，不是十二个散装工具。
- **取事实，不靠模型回忆。** `reference-verifying` 的每条引用事实都来自官方 API 机核（CrossRef / arXiv / PMLR / OpenReview / ACL Anthology / NeurIPS）——命令取数，零模型记忆。机核未决的条目联网核查，证据必须带可访问 URL；每条存疑结论再独立复核一遍。
- **局外人审计，拒绝自我评分。** `paper-review` 运行三名相互隔离的审稿人（方法严谨 / 领域贡献 / 对抗攻击）加作者辩护仲裁——它针对的失效模式正是"模型给自己打的分"。`jargon-check` 更进一步：隔离 subagent 换独立模型，像陌生人一样读润色后的文本。
- **研究级问题的调研技能，不只是论文工具。** `research-before-build` 作用于先例横跨工程与学术两个世界的研究级问题——方案/方法设计、"人类研究过 X 吗"、研究系统的架构选型；同时派发两个并行 `research-scout` 子代理，一个纵向深挖本领域、一个横向扫描跨领域，各自覆盖 GitHub 级与论文级来源。日常工程未知（选库、集成、部署、排障、安全）交给 harness 原生检索；路径已定的执行不触发。论文管线是它最完整的实例化，不是它的边界。
- **技能之间会接力。** `paper-review` 的 C/M/N 意见清单直接供 `rebuttal` 使用；`paper-polishing` 自带术语审计 follow-up；`research-before-build` 把确定的阅读清单交给 `zotero-paper-fetching`。这条链是设计出来的，不是巧合。
- **一份事实源，16 个前端。** 单一 `skills/` 树同时服务三个插件市场（Claude Code、ZCode、Codex）、五个原生读取 `~/.agents/skills` 的 Harness（Gemini CLI、Goose、opencode、Kimi Code、pi），以及八个经幂等扇出接入的 Harness（Cursor、Crush、Copilot、Amp、Grok Build、Qwen Code、Droid、Kiro）。只落符号链接，不污染 `$HOME`。
- **OR & ML 深耕，引擎领域无关。** 出自供应链韧性研究者之手：`figure-plotting` 内置帕累托前沿、网络拓扑、收敛曲线等运筹学图型配方，并做嵌字体验证；`paper-review` 按稿检测领域 gate（OR 各族、ML+OR、LLM/agent），引擎本身可自由扩展到任何领域。

## 科研流水线

| Skill / Agent | 形态 | 一句话 |
|---|---|---|
| ⓪ `research-before-build` | skill | 研究级问题动手前先查先例：工程源（文档、GitHub 仓库）与学术源（论文）双维恒查，纵向/横向两个 `research-scout` 子代理并行派发 |
| ① `zotero-paper-fetching` | skill | 自动检索全网相关文献，补全元数据，下载 PDF，并分层导入 Zotero 库 |
| ② `zotero-paper-note` | skill | 逐篇精读产出结构化笔记，写回 Zotero 条目 |
| ② `zotero-pdf-highlighting` | skill | 把阅读笔记的五个类别按颜色写回 PDF 高亮：问题红 / 模型黄 / 方法绿 / 案例蓝 / 结果紫 |
| ③ `figure-plotting` | skill | 基于论文手稿设计可视化图表，内置科研配色方案，导出高清矢量图 |
| ④ `top-journal-writing` | skill | 按顶刊结构蓝图起草或重构章节——引言倒漏斗、摘要五句公式、方法菜谱、讨论四步走——句式库出自 200 篇顶刊/顶会语料的自动挖掘 |
| ④ `paper-polishing` | skill | LaTeX 学术润色：语法、用词、句式、逻辑、语气五维改到可发表 |
| ④ `jargon-check` | **subagent** | 针对 AI 写作“AI 腔”与“学术黑话”，脱离上下文单独审查术语套话 |
| ④ `term-audit` | skill | 名词术语黑话批量审计漏斗：确定性提取 + 五信号排序 → `jargon-check` terms 模式分批并行 → 变体分组 + 漂移合并 |
| ⑤ `paper-review` | skill | 三位隔离评审 + 作者答辩仲裁，输出 C/M/N 问题清单 |
| ⑤ `reference-verifying` | skill | 通过官方 API 机器核查文献引用，而非模型记忆，防止幻觉引用 |
| ⑥ `rebuttal` | skill | 根据审稿意见逐条修订论文手稿，并同步 Response Letter |
| ⑦ `slide-making` | skill | 把论文稿件做成会议演讲 PPT 或开题/答辩 Beamer |

### 调研层与管线层

- **调研层（⓪）**：`research-before-build` 作用于研究级先例问题——方案与方法设计、"人类研究过/解决过 X 吗"、研究系统的架构选型——不作用于日常工程未知（harness 原生检索已覆盖），也不作用于路径已定的执行。它是整个技能包的世界观：动手前先查先例，且不止于本领域——把问题剥离领域术语后问"人类历史上是否解决过"，从任务描述与仓库约定锁定调研问题，检索维度上工程（文档/issues/成熟仓库）与学术（论文）恒双开，检索方向上纵向深挖本领域、横向跨领域借鉴——以两个 `research-scout` 子代理成对并行同启（横向绝非纵向失败后的退路），检索策略按面分解+松弛阶梯构造查询，候选按问题结构匹配度排序，以决策影响验收。
- **管线层（①–⑦）**：论文生命周期，是这套调研技能最完整的实例化——从一份参考文献清单到会议演讲。

⓪ → ① 是上下游而非包含：`research-before-build` 决定"是否调研、调研什么"；`zotero-paper-fetching` 把确定的文献清单获取入库。

### Skill 与 Subagent 的分界

- **skill**：描述自动触发，主对话内运行——适合流程编排（检索、润色、审稿、回复）。
- **subagent**：显式派发，隔离会话。两种职责配得上隔离："局外人视角"的审计（`jargon-check` 的核心价值正在于此：换模型、换上下文，专查写作模型的用词盲区）与并行调研线（`research-scout`：`research-before-build` 面对研究级问题成对派发——一个纵向深挖、一个横向扫描，预算各自切片；隔离买到的是并行与主上下文干净）。

## 用法：直接说需求

技能靠描述自动触发，没有需要背的斜杠命令。两个 subagent 站在自动触发之外：`jargon-check` 由你点名调用，让审计发生在写文本的那段对话之外；`research-scout` 由 `research-before-build` 面对研究级问题成对派发，你从不直接调用。另外，任何研究级问题，`research-before-build` 都会先工程+学术双源查先例再动手——无需邀请。

| 你说 | 触发 | 得到 |
|---|---|---|
| "物流网络的地缘政治风险怎么量化？有没有现成方案？" | `research-before-build` | 先例备忘录——工程与学术候选，按结构匹配排序评估 |
| "把这 30 条文献加进 Zotero 并下载 PDF" | `zotero-paper-fetching` | 元数据补全的条目，PDF 按出版商归档 |
| "读一下这篇文献，做结构化笔记" | `zotero-paper-note` | 笔记回写 Zotero 条目 + `literature.jsonl` |
| "按笔记给这篇 PDF 上色" | `zotero-pdf-highlighting` | PDF 内嵌五色高亮 + 逐页报告 |
| "画这张帕累托前沿 / 供应链网络拓扑图" | `figure-plotting` | 矢量 PDF，Times New Roman，字体已嵌入 |
| "按顶刊风格写 Introduction" / "把这段摘要重构一下" | `top-journal-writing` | 蓝图章节骨架 + 带出处的句式库取式成句 |
| "润色一下 Introduction" | `paper-polishing` | 修改后的 LaTeX，标记原样保留 |
| "审一遍用词"（润色之后） | `jargon-check`（点名调用） | 陌生审稿人视角的黑话审计 |
| "把全篇名词术语都审一遍" | `term-audit` | 排序候选表、分批判定报告、变体/漂移表 |
| "投稿前把参考文献全查一遍" | `reference-verifying` | 字段级核对表 + 严重度分级 |
| "像审稿人一样审这篇稿子" | `paper-review` | 三审稿人评审报告 + C/M/N 意见清单 |
| "按审稿意见逐条写回复" | `rebuttal` | `\changed{}` 标注、编译后的 PDF、更新的回复信 |
| "把这篇论文改成 15 分钟的报告" | `slide-making` | Beamer 幻灯、控时讲稿、演讲者备注 |

## 安装

**按你使用的工具选路径：**

- 用 **Claude Code / Codex / ZCode** → 方式一，插件——安装与更新由插件客户端管理。
- 用**其他任何兼容 Agent Skills 的 Harness**，或同时用多个 → 方式二，`install.sh`——一个符号链接汇聚点加按 Harness 扇出，不污染 `$HOME`。
- **Gemini CLI、Goose、opencode、Kimi Code、pi** 原生读取 `~/.agents/skills`，方式二即可全覆盖。

### 方式一：插件（Claude Code / Codex / ZCode）

Claude Code——本仓库自带市场清单，先添加市场再安装：

```bash
claude plugin marketplace add pengkangzhen/scientific-research-plugin
claude plugin install scientific-research-plugin@scientific-research-plugin
```

Codex——先添加市场，再在 `~/.codex/config.toml` 启用：

```bash
codex plugin marketplace add pengkangzhen/scientific-research-plugin
```

```toml
[plugins."scientific-research-plugin@scientific-research-plugin"]
enabled = true
```

ZCode——本仓库自带插件市场清单（`.claude-plugin/marketplace.json`，source 解析到仓库根）：

1. 克隆仓库到本地，取其根目录路径。
2. 插件市场 → 添加 → 添加插件市场，粘贴仓库根目录。
3. 个人 → scientific-research-plugin → Scientific Research Plugin → 安装。

两个 subagent（`jargon-check`、`research-scout`）随插件包的 `agents/` 目录分发；不加载插件子代理的 Harness 执行 `./install.sh`，经 `~/.agents/agents` 接入。

### 方式二：技能直装（任何兼容 Agent Skills 的 Harness）

```bash
git clone https://github.com/pengkangzhen/scientific-research-plugin.git
cd scientific-research-plugin
./install.sh          # 幂等：~/.agents/{skills,agents} + 按已装 Harness 扇出
```

验证：

```bash
ls ~/.agents/skills    # 12 个技能
ls ~/.agents/agents    # 两个 subagent（jargon-check、research-scout）
```

`install.sh` 先把全部内容落链到 `~/.agents/skills`——Agent Skills 开放标准位置（Anthropic 于 2025 年 12 月开源该格式，已有 40+ 工具采纳）——再扇出到使用自有目录的 Harness。扇出只作用于检测到已安装的 Harness，不会污染 `$HOME`；新装某个 Harness 后重跑一次 `./install.sh` 即可。

| Harness | 技能目录 | 接入方式 |
|---|---|---|
| Gemini CLI | `~/.agents/skills`（`~/.gemini/skills` 的别名） | 原生；或 `gemini skills install <repo> --path skills` |
| Goose | `~/.agents/skills` | 原生 |
| opencode | `~/.agents/skills`（也读 `~/.claude/skills`） | 原生 |
| Kimi Code | `~/.agents/skills` 或 `~/.config/agents/skills`（还读 `~/.kimi`、`~/.claude`、`~/.codex`） | 原生 |
| pi | `~/.agents/skills`（项目级 `.agents/skills`） | 原生 |
| Cursor | `~/.cursor/skills` | 扇出 |
| Crush | `~/.config/crush/skills` | 扇出 |
| GitHub Copilot CLI | `~/.copilot/skills` | 扇出；也可用 `gh skill`（预览版）从 GitHub 安装 |
| Amp | `~/.config/agents/skills`（项目级 `.agents/skills`） | 扇出，以 `~/.config/amp` 判定已安装 |
| Grok Build | `~/.grok/skills`（项目级 `.grok/skills`） | 扇出 |
| Qwen Code | `~/.qwen/skills` | 扇出 |
| Droid | `~/.factory/skills`（项目级 `.factory/skills`） | 扇出 |
| Kiro | `~/.kiro/skills`（工作区级 `.kiro/skills`） | 扇出 |

未覆盖：iFlow CLI（项目级 `.iflow/` 自有布局 + 技能市场体系，无用户级技能目录可扇出）。

清单之外的助手仍可用 `halter sync --apply` 分发。两个 subagent 在扇出目标中没有对应机制（它们没有 subagent 概念）——经 `~/.agents/agents` 到达 Claude 系 Harness。

## 目录结构

```
├── skills/                      # 12 个自动触发技能（唯一事实源）
│   ├── research-before-build/
│   ├── zotero-paper-fetching/
│   ├── zotero-paper-note/
│   ├── zotero-pdf-highlighting/
│   ├── figure-plotting/
│   ├── top-journal-writing/
│   ├── paper-polishing/
│   ├── term-audit/
│   ├── paper-review/
│   ├── reference-verifying/
│   ├── rebuttal/
│   └── slide-making/
├── attic/                       # 退役技能，保留溯源
│   └── academic-paper-review/   # 7-agent 期刊评审模拟（上游：academic-research-skills）
├── agents/
│   ├── jargon-check.md          # 隔离审计 subagent
│   └── research-scout.md        # 并行先例调研 subagent（L2 纵向/横向双线）
├── .claude-plugin/
│   ├── plugin.json              # Claude Code 插件清单
│   └── marketplace.json         # Claude Code / ZCode 市场清单（source 指向仓库根）
├── .zcode-plugin/plugin.json    # ZCode 插件清单
├── .codex-plugin/plugin.json    # Codex 插件清单
├── .agents/plugins/marketplace.json  # Codex（~/.agents）市场清单
└── install.sh                   # 裸装：~/.agents 汇聚 + 按已装 Harness 扇出
```

## 维护约定

- 修改任何 skill 一律改本仓库，`install.sh` 是 symlink——本机即时生效，推送即发布。
- 版本号变更需同步四处并保持一致：三个插件清单（`.claude-plugin/`、`.zcode-plugin/`、`.codex-plugin/`）与 `.claude-plugin/marketplace.json` 条目。
- 官方 ZCode 市场通道（zai-org/zcode-plugins 的 `plugins/scientific-research-plugin/`）自 2026-09-24 起**暂停**——恢复前不做 fork 同步、不提 PR。若恢复：每次发版提同步 PR，`version` 与 `description_i18n` 逐字一致（官方 `validate.py` 强制校验），公告前先确认对方 `marketplace.json` 确实列出了新版本。
- `academic-paper-review` 已退役归档至 `attic/`（上游：academic-research-skills）；其有效机制（致命缺陷四标准、实验红线、Devil's Advocate 攻击维度）已并入 `paper-review`。完整来源谱系见 `skills/paper-review/references/source-basis.md`。
- 本仓库为 v11：v1 只含 4 个写作技能；v2 扩展为科研全流程（`language-polish` 演化为 `paper-polish`）；v3 加入纪律层 `research-before-build`（⓪）与汇报层 `academic-ppt`（⑦）并将 `scientific-review` 更名为 `paper-review`；v4 将 `paper-review` 重构为三盲审对抗评审团（nature-reviewer 式架构、OR/ML+OR 领域 gate、作者辩护仲裁），并退役 `academic-paper-review`；v5 新增 `reference-verify`（⑤ 投稿前参考文献体检，从一次全稿引用核查实战凝练的三层核查法）；v6 新增 `term-audit`（名词术语黑话批量审计：确定性提取 → 五信号排序 → `jargon-check` terms 模式分批并行 → 变体/漂移合并，种子词表源自 Kobak et al. 2025 超额词汇研究）并为 `jargon-check` 增加 `terms` 审计模式；v7 按官方技能命名最佳实践（动名词形式）将五个技能更名：`figure-plot` → `figure-plotting`、`paper-polish` → `paper-polishing`、`reference-verify` → `reference-verifying`、`zotero-paper-fetch` → `zotero-paper-fetching`、`academic-ppt` → `slide-making`——共 10 skill + 1 subagent；v8 新增 `zotero-pdf-highlighting`（按阅读笔记五类别给 PDF 写分类颜色高亮：PyMuPDF 文件内嵌批注路线、严格五类对齐 Zotero 官方调色板、幂等可重跑）——现共 11 skill + 1 subagent；v9 新增 `top-journal-writing`（④ 顶刊风格章节起草/重构：引言倒漏斗、摘要五句公式、方法菜谱、讨论四步走蓝图 + 句式库——从 arXiv 与 OpenAlex 采集的 AI/OR/管理/物流/航运五域 200 篇顶刊语料自动挖掘，句句带出处）——现共 12 skill + 1 subagent；v10 令 `research-before-build` 的 L2 真正并行——纵向与横向两条调研线同时派发为 `research-scout` 子代理（每线一个、预算切片、按线停止规则，无子代理机制的 Harness 走降级路径）——现共 12 skill + 2 subagent；v11 将 `research-before-build` 聚焦到研究级先例问题——删除 L1/L2 分层，工程与学术双维恒开，日常工程未知（选库/选框架、集成、部署、迁移、云配置、排障、性能、安全）交还 harness 原生检索——并新增问题拆解：PICO 式面分解（面内 OR、面间 AND）+ 松弛阶梯（全组配 → 丢最绑定场景的面转为评估期过滤 → 概念升上位），合成自 Cochrane 组块检索、Motro 查询松弛与 step-back prompting——且每份调研落盘为带日期的阅读清单，存于 `docs/research/`（论文带 DOI/arXiv ID 供 `zotero-paper-fetching`，repo 带钉定版本）。

## License

MIT
