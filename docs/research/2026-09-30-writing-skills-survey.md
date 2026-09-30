# 科研写作技能调研（2026-09-30）

> 背景：top-journal-writing 技能立项（源自一篇"拆 200 篇顶刊学写作"的经验帖沉淀任务），按仓库惯例先调研社区成熟方案再动手。与 [2026-09-19-similar-repos-survey.md](./2026-09-19-similar-repos-survey.md) 互补：那份聚焦**审稿**侧（paper-review 技能的素材），本份聚焦**写作生成**侧。
> 方法：WebSearch 多轮检索 + 仓库 README/SKILL.md 抽读（GitHub 直连不可达，走 WebFetch 与镜像）。

## 1. 写作技能包（Claude Code skill 形态）

- **`Master-cai/Research-Paper-Writing-Skills`**（~100+ star，增速快）— ML/CV/NLP 论文写作技能，内容源自**浙江大学彭思达老师公开笔记**（`pengsida/learning_research`，正文在 Notion）。组织方式：`SKILL.md` + `references/{abstract,introduction,related-work,method,experiments,conclusion,paper-review}.md` 分章节指南，**按需单文件加载**（明令禁止一次全载）。方法要点：先定 story 再改句子、one message per paragraph、写完反向提纲（reverse outlining）、论点-证据对齐（每条主张须有实验支撑，否则删）、投稿前对抗性自查。
- **`K-Dense-AI/scientific-agent-skills`**（~45.9k star，168 技能，配 arXiv 论文）— 写作相关：`scientific-writing`（证据可追溯写作）、`venue-templates`（期刊模板）、`peer-review`、`literature-review`。组织规范值得借鉴：`SKILL.md` 必含 `metadata.version`（递增）、`license` 逐技能声明、带 `scripts/` 的技能必须配 `tests/<skill>/`（CI 强制）、`skills-ref validate` 校验 frontmatter。
- **`lishix520/academic-paper-skills`**（~1.3k star）— strategist（规划）+ composer（写作）双技能，7 维×5 分锚定量表、大纲评分达标才放行写作（09-19 报告已从审稿角度收录，其写作闸门机制同源）。
- **`academic-writing` GitHub topic 下的技能束** — SSRN/arXiv/期刊写作：orchestrator + draft + 5 支撑技能的多技能编排；国内有 Nature-Paper-Skills（期刊优先、claim 驱动、figure 叙事）等衍生。
- **MCPMarket "Paper Writer" / "Academic Paper Writer"** — 实验数据→LaTeX 手稿；其一附带 `academic-phrasebank.md` 参考文件（Phrasebank 句式库直接内嵌为技能资产）。

## 2. 自动论文写作管线（研究项目）

- **`SakanaAI/AI-Scientist`** — `perform_writeup.py`：按 Introduction/Method/Results… 逐节生成，每节独立系统提示 + Semantic Scholar 引用汇聚 + LaTeX 编译闭环；v2 曾过 ICLR 2025 workshop 审稿。
- **`SamuelSchmidgall/AgentLaboratory`**（arXiv:2501.04227）— 三阶段（文献综述→实验→**报告写作**），paper-solver 把前两阶段产出（计划/代码/结果）迭代精炼成文；论文附录含各阶段提示词全文。
- 共性：**分节提示 + 迭代精炼 + 审稿信号反馈**，但不产出可复用的"写作模式资产"——提示词是一次性的，没有从真实语料挖掘句式。

## 3. 句式库资源（"顶刊句型 100 句"思想源头）

- **Academic Phrasebank**（曼彻斯特大学，refnwrite 系）— 按修辞功能（引入工作/描述方法/报告结果/讨论发现/写结论/引用来源）组织的学术短语库，是该领域事实标准。
- **`ahmetbersoz/chatgpt-prompts-for-academic-writing`** — 头脑风暴/改写/结构化写作提示词合集。
- **`KMCS-NII/AASC`**（arXiv:2006.10334）— 基于 Phrasebank 修辞功能的句式生成研究，验证了"修辞功能→句式模板"路线。
- **`writing-resources/awesome-scientific-writing`** — 工具清单（09-19 从审稿角度判阴性；写作侧亦只是索引，无方法论）。

## 4. 融合决策（top-journal-writing 落地取舍）

**采纳**：
1. **分章节 references + 按需单载**（Master-cai）——但本技能的方法论密度集中在一张"章节蓝图"，正文直接内联表格即可，不拆 7 个文件；
2. **句式库按修辞功能组织**（Phrasebank/AASC）——升级为**带出处的真实语料句式库**（`references/sentence-bank.md` + `data/patterns.jsonl`），这是与全部现有方案的差异点：社区各家要么硬编码建议、要么一次性提示词，没有一家从真实顶刊语料挖掘模式；
3. **论点-证据对齐、反向提纲**（Master-cai）——前者并入蓝图审计清单，后者作为自查步骤；
4. **数据采集脚本与数据文件分离**（本仓库既有惯例，K-Dense 的 validate/tests 思路佐证）——期刊配置 `references/journals.json` 唯一事实源。

**否决**：
- 自动论文生成管线（AI-Scientist/AgentLaboratory 式）——本技能是"人写 AI 辅助"，定位与 pipeline 上游 zotero 精读、下游 paper-polishing/paper-review 衔接，不做端到端代写；
- strategist/composer 双技能拆分——本仓库 pipeline 已有分工，拆两技能反而割裂；
- 整包安装 K-Dense（168 技能耦合面太大，其 README 也建议按主题子集安装）。

**后续候选**：`venue-templates` 类期刊投稿模板技能（LaTeX 模板 + 投稿清单），与本技能互补，暂不立项。
