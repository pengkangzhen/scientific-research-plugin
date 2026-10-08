---
name: hedge-audit
description: >
  Whole-manuscript defensive-writing (over-hedging) audit — targets the
  AI-typical habit of defending every claim as it is made, with
  section-conditional verdicts: escape clauses bolted onto Results
  ("However, this does not necessarily mean...", "should be interpreted
  with caution"), null-result self-explanation, contribution-weakening
  hedges in Abstract/Introduction ("we attempt to"), hedge stacking
  anywhere, and scattered caveats that duplicate Limitations. Doctrine:
  Results reports, Discussion interprets, Limitations concedes — each hit
  is disposed as delete / move-to-Discussion / move-to-Limitations / keep,
  with relocation integrity and per-section hedge-density gradients.
  Read-only audit. Use when the user says "defensive writing check",
  "hedge audit", "over-hedging", "too many howevers", "Results keeps
  defending itself", "weakened contributions", "防御性写作", "检查
  however 是不是太多", or asks where a caveat should live.
license: MIT
---

# hedge-audit：防御性写作审计

## 定位与边界

- **管**：**全稿范围**（Abstract 到 Conclusion）放错位置或过度堆叠的 hedge——"一边陈述、一边替自己辩护"的防御性写作。AI 写作的典型习惯是一句话照顾所有可能性：你说 A 和 B 显著相关，它补"但这不证明因果"；你说某组更高，它补"未测量因素也可能有影响"；你说不显著，它补"不显著不等于没作用"。各章纪律不同：Results 最严（只报告），Discussion/Limitations 是让步的合法归宿，但同样要审——堆叠、与 Limitations 重复、只让步不表态，都是病。
- **不管**：语言润色走 paper-polishing，章节结构起草/重写走 top-journal-writing，科学性评审走 paper-review，名词术语审计走 term-audit。放对位置且未过度的谨慎不是病，不判。
- **只读审计**：输出判定表与搬迁地图，不改稿；用户要求落地修改时另行确认。

## 判定基准（三章分工，全稿视角）

Results 报告你得到了什么；Discussion 解释你怎么理解它；Limitations 承认它解释不了什么。三章各做各的事，其余章节各有其责（见章节规则表）。

全稿判定问题永远是一个：**这句话是在给读者提供信息，还是在给作者预留退路？**

> Results 是展示你做了什么，不是展示你没做什么。

健康稿件的 hedge 密度应呈**梯度**：Abstract / Introduction / Results 低，Discussion 中，Limitations 高。梯度倒挂（Results 比 Discussion 还谨慎）是最响的红旗。

## 病理五型（全稿适用，锚点在 Results）

| 型 | 名称 | 形态 | 典型处置 |
|---|---|---|---|
| R1 | 转折开脱 | `[断言] + However/Nevertheless/That said + [退路从句]`；退路从句词表见 references | 最严三区删后半句；有实质内容则移 Discussion |
| R2 | null 自救 | Results 里解释"为什么没有结果"（样本量、残余混杂、指标定义） | 移 Discussion（解释机制）或 Limitations（让步） |
| R3 | 撒胡椒面 | caution / "further research is needed" 散落各章各段，而非集中 Limitations | 删；确有分量者集中到 Limitations |
| R4 | hedge 堆叠 | 一句内 ≥2 个认识论修饰词（may possibly / might potentially）——**唯一无章节豁免的病理** | 压缩为单个修饰词或删 |
| R5 | 合法精度 | 统计报告动词与设计相符（"was associated with"、实测后恰当的 "suggests"） | **KEEP**——这是精度，不是防御 |

R1–R3 的**最严三区**：Results（及 CS 风格 Experiment 的结果报告段）、Abstract 的头条结果句、Introduction 的贡献句。同样的句式落在 Discussion 属正常论证。**不许把 R5 误报成病**：统计上诚实的措辞被删掉，与防御性写作同样是灾难。

## 章节规则表

| 章节 | 病理信号 | 合法容忍 |
|---|---|---|
| Abstract | 头条结果被弱化（数字前缀 may/could）；hedge 堆叠 | 结尾一句全局 scope；与设计相符的精度动词 |
| Introduction | 贡献句弱化；gap 陈述过度让步 | 批判他人工作的转折（那是进攻） |
| Methods | 预防性免责（"以防万一"式） | 设计固有边界、假设声明 |
| Results | R1–R4 全量，最严 | R5 统计精度 |
| Discussion | 堆叠；与 Limitations 重复；通篇只让步、没有任何一句不戴 hedge 的核心解读 | 让步后再推进的正常论证；机制解释 |
| Conclusion | 定位句反复防御；逐段缀 caution | 一句全局定位（"augments, rather than replaces"式） |
| Limitations | 自我贬低式过度让步（把"边界陈述"写成"结果不可信"）；堆叠 | 集中让步——这是它的家 |

## 管线（六步）

**① 输入契约。** 一份 `.tex`（或纯文本）手稿路径；多文件工程先找 `\input`/`\include` 展开。**全稿在审**；无独立 Results/Discussion 章节的 CS 风格论文，把 Experiment 内的"结果报告段"与"机理分析段"分开标记，前者按 Results 纪律审。

**② 章节边界。** `grep -n '\\\\\(sub\)\?section'` 定位各章行号区间；每个 hedge 命中先标注它落在哪一章，再按章节规则表定性。

**③ 机械扫描。** 两条命令扫全稿（词表与正则见 `references/patterns.md`）：

```bash
# 主扫：结构化 marker（转折、退路、caution、解释式 may/might）
grep -nEi "however|nevertheless|nonetheless|that said|with caution|caveat|\
should be noted|worth noting|does not necessarily|not necessarily|rather than claiming|\
cannot (rule out|exclude|guarantee|claim)|possible explanation|may (be due|be attributed|reflect)|\
might (be due|reflect)|could be (due|attributed)|further (research|studies|investigat)|\
interpreted|overinterpret|underestimat" manuscript.tex

# 副扫：认识论修饰词（高频词，人工过筛）
grep -nEi "may |might |possibly|perhaps|appear to|seems? to|unclear|uncertain|arguab|\
(attempt|hope|try) to" manuscript.tex
```

**④ 逐条定性。** 每个命中读上下文（前后各 2–3 句），标注章节，按章节规则表 + however 二分测试判 R1–R5。二分测试：转折之后的内容**帮读者**（逻辑对比、推进论证）→ 不是病；**保作者**（免责、留退路、预防性认错）→ R1。

**⑤ 处置与搬迁完整性。** DELETE / MOVE→Discussion / MOVE→Limitations / KEEP 四档。MOVE 前先查目标章节现有文本：内容已存在 → 改判 DELETE（去重）；目标章节根本不存在（无 Discussion 的论文）→ 报告标注"无处可搬"，交用户决策，不擅自定去留。R3 判定要全稿数一遍散落的 caution，与 Limitations 现有内容对照后再下"删还是集中"的结论。

**⑥ 密度统计与终报告。** 各章 hedge 数 / 百句，画梯度画像（Abstract/Intro/Results 低、Discussion 中、Limitations 高为健康；倒挂即红旗），附两条全稿检查：G1 撒胡椒面总数及可集中清单；G2 Discussion 是否存在至少一句不戴 hedge 的核心解读句（一句都没有 = 过度防御）。

## keep-list（防误报，逐条过完再下结论）

- **统计报告精度**：`was associated with` / `suggests` / `consistent with`——与相关性设计、观测数据相符的动词。研究设计本身不支撑因果动词时，用因果动词才是错。
- **设计固有谨慎**：Methods 里"may not generalize"式的设计边界句。
- **单句 scope 说明**：Abstract 结尾或 Conclusion 里**一句**全局性谨慎（"MAKO thus augments, rather than replaces, expert judgment"这类放在结论里的定位句是合法的）。
- **Discussion 的让步-推进结构**："This improvement is likely attributable to X, though part of the gain may stem from Y"——让步后仍推进论证，是正常学术写法。
- **审稿人要求**：rebuttal 语境中 reviewer 点名要求的 caveat——那是谈判结果，不是防御性写作。
- **有依据的"may"**：一句一个、指向具体机制的认识论修饰；堆叠才病（R4）。
- **Related Work 的转折**：对他人工作局限的批判性 however 是进攻不是防御。

## 输出格式

```markdown
## 防御性写作审计报告：<manuscript>

**总结论**：一句话（如"Results 纪律良好，仅 2 处轻微越界；Discussion 存在与 Limitations 重复的 caution 3 处"）。

**判定表**（按章节分组）
| # | 章节 | 位置 | 原句（节选） | 型 | 处置 | 建议 |
|---|------|------|--------------|----|------|------|
| 1 | Results | manuscript.tex:794 | "…However, this does not…" | R1 | DELETE | 删 however 起的后半句 |

**密度梯度**：各章 hedge/百句一行表 + 梯度是否健康。
**搬迁地图**：MOVE 项 → 目标章节现有内容对照（是否重复、建议并入第几段）。
**全稿检查**：G1 撒胡椒面清单；G2 Discussion 核心解读句有无。
**keep 记录**：判 KEEP 的命中及理由（防误报复核）。
```

改写建议给到"删 however 起的后半句"或"并入 Discussion 第 3 段"的粒度，可直接执行。

## 降级路径

无特殊依赖（Grep + 判断即可）。长稿 marker 命中过多时，按章节切分精读：最严三区（Results/Abstract 头条/Intro 贡献句）全文精读，Discussion/Limitations 只审堆叠与重复，其余章节做密度统计。
