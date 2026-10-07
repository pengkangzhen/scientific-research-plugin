---
name: top-journal-writing
description: >
  Top-journal imitation writing — draft or structurally rewrite paper
  sections following the structural blueprints and real-corpus sentence
  patterns of a field's top journals: four-layer inverted-funnel
  introduction, five-sentence abstract formula, methods written like a
  recipe, results with figure-first text-second, four-step discussion,
  two-to-four-sentence closing conclusion; the sentence-pattern library is
  auto-mined from 200 top-journal/top-conference papers (arXiv cs.LG/
  math.OC, MS/POM/JOM/Omega, TRE/TRSC/EJOR, MPM/TRD/MTR). Use when the
  user says "imitation writing", "write/rewrite the Introduction,
  Abstract, or Discussion in top-journal style", "draft the abstract/
  introduction/discussion/conclusion", "fix the structure", or
  "deconstruct this paper's writing" / "draft a section in top-journal
  style". Structure and sentence patterns only; language polish goes to
  paper-polishing, terminology audit to term-audit, submission review to
  paper-review.
license: MIT
---
# top-journal-writing：顶刊仿写

## 定位与边界

- **管**：从零起草论文章节，或对已有章节做**结构性**重写（段落顺序、漏斗层次、句式功能位）；按章节蓝图逐层搭骨架，再从句式库取式填句。
- **不管**：已完成文本的语法/措辞级润色（paper-polishing）、术语黑话（term-audit/jargon-check）、科学内容正确性与审稿（paper-review）、参考文献真实性（reference-verifying）。
- **句式纪律**：写作时套用的每一个句式都必须出自 `references/sentence-bank.md`（每条带真实出处）；句式库没有的功能位，明说"库中无匹配句式"，**不现场编造"顶刊常用句式"**。占位符（数字、引文键）一律显式标注，不虚构。

## 方法来源（三层证据）

1. **结构蓝图**：一篇"拆 200 篇顶刊"写作经验帖的八条方法（漏斗/公式/菜谱/图主文辅/四步走/收口/句式库/模仿循环），经社区调研校准——见 `docs/research/2026-09-30-writing-skills-survey.md`（采纳了 Master-cai 技能包的论点-证据对齐与反向提纲，否决了端到端代写路线）。
2. **句式库**：`references/sentence-bank.md`，按修辞功能 × 领域组织的句式模板，全部泛化自真实语料。
3. **语料证据层**：`data/patterns.jsonl`（带出处的原句）+ `data/papers.jsonl`（200 篇清单：AI 50 / OR 50 / 管理科学 40 / 物流 30 / 航运 30）。语料可用 `scripts/` 再生，见文末。

## 章节蓝图

### 引言：倒漏斗，四层递进

引言不是文献综述。前人工作只在第三层作为"缺口"的对立面出现，逐条罗列=教科书写法。

| 层 | 内容 | 句式功能位 | 红线 |
|---|------|-----------|------|
| ① 大背景 | 一句话点领域重要性 | background | 不超过两行，禁止"随着社会发展"式铺垫 |
| ② 具体问题 | 聚焦到本文的小切口 | background→method 过渡 | 与 ① 之间必须有明确收窄 |
| ③ 缺口 | 别人没解决什么 | **gap**（全文最重要的一句） | 必须具体到"哪类问题缺哪种方法/证据"，不许空泛 |
| ④ 本文贡献 | 我们做了什么、为何补上缺口 | method + contribution | 一句话点明，细节留给贡献列表 |

顶刊引言通常四段，每段不超五行；段间衔接靠层次递进而非过渡词堆砌。正文展开时：②③层之间常插一段 mini 综述（只综述与缺口直接相关的文献），④层后接贡献条目与文章结构段。

### 摘要：五句公式

| 位 | 功能 | 规则 |
|---|------|------|
| 1 | 背景句 | 一句，领域为什么重要 |
| 2 | 问题句 | 一句，存在什么空白（gap 句式的浓缩版） |
| 3 | 方法句 | 一句，我们做了什么 |
| 4 | **结果句** | 一句，关键发现，**必须带具体数字**（"平均降低成本 12.4%""gap 在 300 秒内闭合到 0.8%"） |
| 5 | 意义句 | 一句，对理论/实践意味着什么 |

每句都必须有信息量；"取得了重要进展""效果显著"是废句。写完数一遍：不是五句结构就重排。

### 方法：像菜谱，不像散文

唯一标准：**别人能按它复现**。只写客观事实，零讨论、零"我们认为"。

OR/物流/航运论文的菜谱三栏：

- **材料**：基准实例集（名目、规模、来源/生成方式）、真实数据集（航线/订单/网络，口径与年份）、软件与版本（求解器及版本、语言与库、硬件、时间限制、随机种子）。
- **步骤**：假设列表 → 符号表 → 模型（目标、约束逐条有出处或理由）→ 复杂度/性质证明 → 算法（步骤化，伪代码配文字）。
- **统计**：对比基线是什么、重复次数、指标定义（gap、服务率、运行时）、显著性检验方式。

方法写不清楚，审稿人默认你数据有问题。

### 结果：图是主角，文字是配角

文字只做三件事，不重复方法、不展开讨论：

1. **指出**图里最关键的发现（"图 2 表明：需求波动越大，两阶段鲁棒模型的成本优势越明显"）；
2. **解释**该发现意味着什么，但不越界到机理猜测；
3. **引导**读者看图的关键细节（拐点、异常点、对比条）。

结果句是全文最短的句子——逐句删到不能再删。图表本身（信息密度、字体、配色）走 figure-plotting。

### 讨论：顶刊与普刊的分水岭，四步走

| 步 | 内容 | 要点 |
|---|------|------|
| 1 | 重申主要发现 | 一句话，不啰嗦 |
| 2 | 与已有研究对比 | 一致还是矛盾，各自为什么；矛盾处点名对比对象 |
| 3 | 解释机制 | 为什么会得到这个结果，理论支撑是什么 |
| 4 | 局限与展望 | 诚实指出不足，但立刻接"这不影响主要结论"——自信的局限 |

第 2、3 步是审稿人判断作者水平的地方，写薄了讨论就是"把结果又说一遍"。

### 结论：短，就对了

两到四句：做了什么 → 发现了什么 → 意味着什么 →（可选）下一步。不出现新数据、新文献。超过一段就是没写完引言和讨论的账。

### 语言：套句式，不抄句子

- 拆句式结构、换自己的内容；整句照搬是抄袭。
- 每个功能位先查 `references/sentence-bank.md` 的对应小节，选域内（你的投稿领域）模板，换词填充。
- 同一功能位全文只用一种句式变体；换着花样重复同一件事是新手病。

## 工作流

### ① 路由

```
用户输入
  ├─ 起草：给章节名（+素材：模型/实验结果/Zotero 笔记） ──────→ 模式 A
  ├─ 重写：给已有章节 + "结构不对/像教科书/太散" ──────────→ 模式 B
  └─ 拆解：给一篇范文（PDF/tex/链接） + "学它的写法" ────────→ 模式 C
```

### 模式 A：起草

1. 确认目标章节与投稿领域（ai / or / mgmt / logistics / shipping，未说明则按 or+logistics 默认）。
2. 按蓝图列骨架：每段一句话说清该段功能（漏斗第几层/讨论第几步）。
3. 逐功能位查句式库取式填句；数字、引文键、图号用 `%<占位>%` 显式标注。
4. 对照下方自查清单交稿。

### 模式 B：结构审计与重写

1. 通读章节，做**反向提纲**：给每段提炼一句"这段在干嘛"，标到蓝图的功能位上。
2. 诊断：层次缺失（漏斗断在第二层）、顺序错乱（缺口句出现在贡献句之后）、段落超载（一段干三件事）、句式空转（有 gap 形无 gap 实）。
3. 只动结构：段序、段切分、句式功能重排；措辞级问题列清单移交 paper-polishing，不越界代改。
4. 输出重写稿 + 结构诊断表（反向提纲 → 诊断 → 改动理由）。

### 模式 C：拆解范文

1. 读全文，按蓝图做结构标注：引言逐段标漏斗层次、摘要逐句标功能位、讨论标四步位置。
2. 产出拆解报告：结构骨架图 + 各层长度统计 + 值得套用的句式（附原文出处）。
3. 拆解报告若发现语料库之外的优秀句式，按 `references/sentence-bank.md` 的格式追加（带出处），完成"库的生长"——这正是帖子八条方法的最后一条：拆得多了开始挑顶刊的毛病，就出师了。

### 自查清单（A/B 模式交稿前过一遍）

- [ ] 引言：漏斗四层齐全，gap 句具体，无文献罗列
- [ ] 摘要：五句各就各位，结果句带数字
- [ ] 方法：复现所需要素（实例/版本/硬件/时间限制/种子）齐
- [ ] 结果：无方法复述、无讨论展开，句长收敛
- [ ] 讨论：四步齐全，对比与机制两步有实质内容
- [ ] 结论：≤4 句，无新数据新文献
- [ ] 句式：全部出自句式库且可溯源；同功能位无重复变体
- [ ] 占位符：数字/引文/图号均为显式占位，无编造
- [ ] 论点-证据对齐：引言/摘要里每条主张都有对应实验或文献支撑，撑不住的主张已删

## 语料与句式库再生（维护模式）

```bash
# 采集 200 篇（arXiv API + OpenAlex，期刊配置在 references/journals.json）
uv run skills/top-journal-writing/scripts/harvest_papers.py \
    --mailto you@example.com --raw /tmp/tjw-harvest

# 挖掘句式（摘要级 + arXiv HTML 全文级）
uv run skills/top-journal-writing/scripts/mine_patterns.py \
    --abstracts /tmp/tjw-harvest/abstracts.jsonl --fulltext 24
```

- 换领域/期刊：改 `references/journals.json`（ISSN 会经 OpenAlex 自动反查校验）。
- 挖掘产出 `data/patterns.jsonl` 是证据层；`references/sentence-bank.md` 是人工泛化的使用层——再生成语料后需要人工重审句式库，脚本不自动覆盖它。
- 数据来源与许可说明见 `data/README.md`。

## 输出与纪律

- **产出语言跟手稿走**（LaTeX 论文即英文），与用户交流用中文。
- 起草物是**结构完备的草稿**：句式真、结构对、占位显式；数字与结论的真值由作者负责——这是"仿写"不是"代写"。
- 每次交稿附句式溯源表（套用句式 → 句式库条目 → 语料出处 id）；做不到溯源的句子要么删要么换成占位句。
- 帖子原话作为元方法收尾：模仿不是为了像，是为了不像——先老老实实拆五十篇，再谈自己的写法。
