---
name: term-audit
description: >
  Batch jargon/terminology audit for a LaTeX manuscript (term audit) — a
  two-stage funnel over the paper's noun phrases: a deterministic script
  extracts candidate noun phrases ranked by five signals, batches are
  dispatched in parallel to jargon-check terms mode, then variants are
  normalized, grouped, and re-checked together for terminology drift. Use
  when the user says "audit the terminology", "check the jargon/nouns",
  "terms must be consistent", "pre-submission terminology check",
  "terminology consistency", wants jargon-check run over a whole paper
  (not just one passage), or says "check terminology" / "terminology
  audit". The unit of jargon pathology is the highly compressed multi-word
  compound noun (controller-level execution); this skill is the batch
  funnel built for them.
license: MIT
---
# term-audit：名词黑话批量审计

## 定位与边界

- **管**：复合名词短语层面的黑话——AI 自造的紧凑标签、未定义的项目命名、跨领域借词、机械性术语变体（大小写/连字符/单复数）、可溯源判真伪的疑似幻觉术语。
- **不管**：一次性空话短语（"a promising technical pathway"）和整段语域问题——那走 jargon-check 的 `passage`/`full` 模式；论证层面的概念误用——那走 paper-review。本技能的报告与 passage 审计互补，不互相替代。
- 一切判定只出自 jargon-check（独立审计员）；本技能的脚本是确定性提取与分组，零模型判断。

## 管线

```
manuscript.tex (+白名单 +基线语料，均可选)
  │ ① extract_terms.py     确定性：候选名词短语 + 五信号排序 + 切批
  ▼
候选表 candidates.{md,json}（批 1 = 得分最高，最优先送审）
  │ ② jargon-check × N 并行   每批 15–30 条，terms 模式，Grep 自取上下文与行号
  ▼
各批判定表
  │ ③ group_variants.py     确定性：表面变体簇 + 同族短语对
  ▼
合并者 jargon-check：判定表 + 变体分组 → 语义漂移复查 → 终报告（只读，不改稿）
```

## ① 提取与排序

```bash
uv run skills/term-audit/scripts/extract_terms.py manuscript.tex \
  --whitelist terms.txt --baseline "published/*.tex" \
  --json candidates.json --md candidates.md
```

- `--whitelist`（强烈建议）：项目自定义命名清单（方法名、缩写、步骤名）。命中即排除——没有它，SOP-MAS 这类合法命名会混进候选。
- `--baseline`（可选）：你自己已发表论文的 glob。基线缺席 +2 分，是"这词不像你写的"信号；不给则跳过该信号。
- 五信号：频次、结构位置（title/abstract/section）、style 黑名单命中（见下）、日常词拼接比、基线缺席。多词复合短语是主目标；单名词只走 style 黑名单侧道且豁免最低频次。
- 黑名单来自 Kobak et al. (Science Advances 2025) 的 900 超额词表（`data/excess_words.csv`，MIT），来源与许可见 `data/README.md`。
- 参数缺省即 `--top 60 --min-count 2 --batch-size 20`：候选上限 60 条、最低出现 2 次、每批 20 条；术语密集的长稿或要捞低频新造词时，调大 `--top`、调低 `--min-count`。

## ② 分批派审

从候选表按批取术语（批 1 优先；时间紧就只审批 1）。每个并行 jargon-check 的工单模板：

```
审计模式：terms
待审对象：<manuscript.tex 的绝对路径>
术语批（第 N 批，共 M 批）：
1. controller-level execution
2. workflow intelligence
…（15–30 条）
术语表白名单：<terms.txt 绝对路径 或 "未提供，重复大写命名按待确认项目术语处理">
对照文件：<response letter 路径，无则写"无">
```

要点：审计员逐术语 `Grep -n` 自取上下文与行号，判定框架、四档判定、防过度审计规则全部沿用 jargon-check 原文，工单不重复。

**降级路径**：当前环境没有子代理机制（或 jargon-check 未安装）时，在主会话按 jargon-check 的 terms 模式契约逐批自审——四档判定、白名单与只读纪律原样沿用，并在终报告注明「审计非隔离上下文」。

## ③ 变体分组与合并

```bash
uv run skills/term-audit/scripts/group_variants.py candidates.json --json variants.json --md variants.md
```

- **表面变体簇**（大小写/连字符/单复数）是机械性漂移铁证，直接列入终报告"必修"区。
- **同族短语对**（共享 2+ 词的不同候选）交给合并者判断是否语义漂移。
- 合并者工单：`full` 或 `passage` 模式均可，附全部各批判定表 + variants.md + 手稿路径；它的增量职责只有两件事——跨批术语漂移复查、汇总结论（各类计数 + 最优先三件事）。各批已判定的词条不重复审。

## 输出与纪律

- 终报告结构：必修（可疑自造/漂移/变体）→ 待裁决（疑似幻觉 + 检索词、待确认项目术语）→ 无问题名单（明确说没问题，防过度审计）。
- **全程只读**：改稿决策归作者。建议替换遵循 jargon-check 的优先级（复用论文已有术语 > 标准学术术语 > 显式定义新标签）。
- 短稿（< 20 条候选）不必切批并行，一个 terms 工单 + 一个合并者即可。
