# 数据来源与许可说明

## 文件清单

| 文件 | 内容 | 生成方式 |
|------|------|----------|
| `papers.jsonl` | 200 篇语料清单（id/title/venue/domain/year/url，纯事实性元数据） | `scripts/harvest_papers.py` |
| `patterns.jsonl` | 挖掘出的写作句式原句（function/domain/venue/year/id/section/sentence） | `scripts/mine_patterns.py` |

语料采集日期：**2026-09-30**。重新采集/挖掘的命令见 `SKILL.md` 末节「语料与句式库再生」。

## 语料构成（200 篇）

| 领域 | 配额 | 来源 |
|------|------|------|
| ai | 50 | arXiv cs.LG（ML 顶会论文主体） |
| or | 50 | arXiv math.OC（Math. Programming / OR / TRSC 等预印本） |
| mgmt | 40 | Management Science 12 / POM 12 / JOM 12 / Omega 4 |
| logistics | 30 | Transportation Research Part E 12 / Transportation Science 12 / EJOR 6 |
| shipping | 30 | Maritime Policy & Management 10 / Maritime Transport Research 10 / TR Part D 10 |

期刊论文经 OpenAlex（`has_abstract:true` 过滤，2019 年起）获取；**原始摘要全文不入库**（harvest 写到
`--raw` 指定的临时目录），入库的只有元数据与挖掘出的单句短引文。

## 数据来源与版权口径

- **arXiv**：元数据与摘要按 arXiv 的 API 与元数据许可使用（非商业检索用途）。
- **OpenAlex**：元数据 CC0；摘要索引来自 OpenAlex 数据管道。
- **patterns.jsonl 中的单句**：每句 ≤ 400 字符、逐句标注出处（DOI/arXiv id），属带署名的学术性短引，
  仅用于写作模式研究，不构成对原文的替代性分发。句式库（`references/sentence-bank.md`）进一步把
  原句泛化为模板，写作产出不再复用原文表述。
- 套用句式写论文时，**换词不换骨架**；整句照抄即为抄袭——`SKILL.md` 的纪律节同样约束这一点。

## 已知局限

- Elsevier 系期刊（TRE/EJOR/TRD/Omega）在 Crossref/OpenAlex 的摘要覆盖不全，语料中占比偏低；
  航运/物流域的句式证据密度低于 AI/OR 域，句式库中相应条目跨域引用时会标注。
- `gap_intro / contribution / conclusion / limitation` 四类句式只来自 arXiv 全文（HTML 版本，
  2023-12 以后提交的论文才有），覆盖 ai/or 两域。
- 挖掘是正则启发式：分类有噪声，人工泛化句式库时已做一轮筛选，但引用单句前建议按 `id` 回看原文。
