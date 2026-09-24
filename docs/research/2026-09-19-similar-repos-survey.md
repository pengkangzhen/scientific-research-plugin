# 同类插件/技能仓库调研全景（2026-09-19）

> 背景：当时 scientific-review 技能（现 paper-review）准备"集百家之长"做融合升级，主会话派生 8 个只读网络调研子代理并行调研。
> 产出去向：机制层面已融合进 `skills/paper-review/`（溯源见 `skills/paper-review/references/source-basis.md`；融合决策摘要见文末）。
> 本文档的角色：**仓库全景清单**——所有调研发现的 GitHub 仓库、定位与借鉴点，含阴性结论。star 数照抄当时报告口径。

## 1. 学术写作/科研工具箱类仓库（定位最接近本工具箱）

- `yha9806/academic-writing-toolkit`（AWT）— 9 技能/五阶段（Ground→Release）— 真清洁室子代理审稿+非清洁室强制标注、封闭推荐词表、编辑契约+审计脚本分离「审」与「改」
- `wanshuiyin/Auto-claude-code-research-in-sleep`（ARIS，~3.3k–4.4k star）— 研究全生命周期技能集 — rebuttal 三道硬门（溯源/承诺/覆盖）、字符预算双产物、auto-review-loop（≥6/10 过审、诚实条款）
- `K-Dense-AI/scientific-agent-skills` — 165 技能科学库 — peer-review 准入门+11 步流程、意见五字段（Location/Observation/Evidence/Why/Requested action）、审稿 lint
- `lishix520/academic-paper-skills`（~932–1.3k star）— strategist+composer 两技能 — 7 维×5 分锚定量表、大纲 ≥28/35 才放行写作、修订后预测分
- `poldrack/ai-peer-review` — Russ Poldrack 的多 LLM 元审稿工具 — scientific-only 过滤规则、concerns 追溯表、模型匿名化
- `pedrohcgs/claude-code-my-workflow`（P. Sant'Anna, Emory）— 18 agents/60 skills 学术模板 — dispositioned referees 人设、植入缺陷做门的资格认证、编辑-评审-验证三级分离
- `brycewang-stanford/Auto-Empirical-Research-Skills`（AERS）— 76 合集/1096 技能目录 — 6 并行子代理独立读文档再合并；目录本身是同类技能索引
- `brycewang-stanford/AER-skills` — 经济学「识别→稳健性→R&R」技能套件（journal-referee 模拟 top-5 审稿人）
- `appautomaton/latex-arxiv-SKILL` — 门控 LaTeX + BibTeX 验证写作 harness（当时网络超时仅读到元信息）
- `Imbad0202/academic-research-skills` — 与本仓库高度同源（技能名一致），增量价值低
- `yilewang/llm-for-zotero`（~2.2k star）/ `papersgpt/papersgpt-for-zotero` — 阅读器内代理，无质量评审设计（阴性结论）
- `writing-resources/awesome-scientific-writing` — 工具 awesome 清单，无审稿环节
- 非仓库线索：Refine.ink（AI referee）、Georgetown AI Referee 五维榜、Gans NBER w35688

## 2. LLM 自动审稿研究项目

- `SakanaAI/AI-Scientist` — reviewer 模块（perform_review.py）：NeurIPS 式 1–10 逐档定义、保守偏置 prompt、反思轮收敛协议、集成取均值+AC 聚合
- `ResearAI/DeepReviewer-v2`（西湖大学，ACL 2025）— tool-loop 审稿 agent — Finalization Gates（≥3 次检索+≥10 条逐行标注才许出终稿）、证据链字段；v1 论文 arXiv:2503.08569
- `Ahren09/AgentReview`（EMNLP 2024 Oral）— 审稿流程模拟器（Reviewer/Author/AC/PC）— 录取配额强制排序、inclusive-AC 聚合、恶意 reviewer persona 改造为魔鬼代言人
- `maxidl/openreviewer`（UKP Lab/TU Darmstadt）— 79k 条 ICLR 专家审稿微调的 Llama-8B — 分数分布对齐人类、按会议官方模板约束输出
- `zhu-minjun/Researcher` — CycleReviewer/CycleResearcher 双闭环（ICLR 2025）— merits/demerits/suggestions+confidence 输出 schema
- `allenai/marg-reviewer` — 分节多 reviewer 聚合（详见第 3 节）
- `haoxuan-unt2024/llm4innovation` — 引用了 PaperEval（未深读）
- 论文类：ReviewerGPT（arXiv:2306.00622，封闭式 checklist 优于开放式评论）、LLM 审稿综述（arXiv:2501.10326，Information Fusion 2025）
- 阴性结论：LLamaReview 未找到；ReviewAgent 无权威单一同名单目（至少三个同名）

## 3. 科研全流程自动化框架

- `zhu-minjun/Researcher`（CycleResearcher）— 写-审-改训练闭环 — 审稿数据即 rubric 语料（Reviewer-5K 数据集）
- `SakanaAI/AI-Scientist` / `SakanaAI/AI-Scientist-v2` — 九字段 JSON 审稿模板、写/引/审三模型分离、review_iclr_bench 自测集
- `allenai/marg-reviewer`（MARG，arXiv:2401.17519）— actionable feedback 操作化定义（每条 weakness 必须对应一个可执行修改动作）
- `SamuelSchmidgall/AgentLaboratory` — `--num_reviews` 审-改轮数、平台期终止条件
- `O0000-code/awesome-academic-skills` — 按科研生命周期组织的 Claude 技能合辑（含 review/rebuttal 技能）
- `Imbad0202/academic-research-skills` — Rebuttal-Audit 模式（coverage/tone/evidence 三查）
- `brycewang-stanford/Auto-Empirical-Research-Skills` — 含 response-to-reviewers 技能
- `Ahren09/AgentReview` — rebuttal 多角色仿真自检（AC persona 判「回应能否翻盘」）
- `HKUDS/AI-Researcher`（NeurIPS 2025 Spotlight）— 声明式端到端，review 无细粒度 rubric
- `AgentRxiv/AgentRxiv` — agent 论文预印本服务器，README 未完成，不值得借鉴
- `worldbench/awesome-ai-auto-research` — auto-research survey 合辑（持续索引用）
- `AkariAsai/OpenScholar` — 文献综合助手，无 review 功能（阴性结论）
- `openags/Awesome-AI-Scientist-Papers` — 论文集非代码
- 非仓库：AppliedScientist（arXiv:2509.02395，无开源仓库）— judge 对齐校准、事实漂移监控

## 4. Claude 技能生态中的审稿技能

- `AlexWortega/ai-peer-review-skill` — 3 审稿人+meta-reviewer — SSoT 偏见种子注入分视角、OS 级并行脚本、NATO 代号匿名化、强制 arXiv 核查
- `Yuan1z0825/nature-skills`（24.5k star 中文科研技能合集）— nature-reviewer：恰好 3 盲审+1 综合 — claim/evidence 双指针+resolution test、冻结后再比较、Blocking 分级；姊妹技能 nature-response
- `lyra81604/peer-review` — 九维双尺度 — 可复现性单独成维、会议/期刊权重切换、致命缺陷总分封顶
- `agentscope-ai/OpenJudge`（阿里 AgentScope）— paper-review 技能 — 客观错误（correctness）与主观质量分离打分、BibTeX 逐条核验
- `Imbad0202/academic-research-skills` — academic-paper-reviewer：Journal-Fit 专职席位+动态 persona+合同治理重审边界
- `K-Dense-AI/scientific-agent-skills` — peer-review（隐私门禁+文献佐证+line-by-line 表格）；姊妹技能 scholar-evaluation
- `stephenturner/skill-peer-review-assistant` — Consensus API 检索 — 作者先自评、每条 weakness 挂真实文献、audit log
- `bytedance/deer-flow` — academic-paper-review 技能：7 段式结构、禁模糊建议、逐节扫描
- `davila7/claude-code-templates` — peer-review（8 项清单）+ paper-reviewer（审前 4 问、signal/noise/silence/voice 四象限）
- `poldrack/ai-peer-review` 及 fork `CBS-HPC/ai-peer-review_vllm`
- MCPMarket 三款：Academic Peer Review（poemswe，Reviewer 2 对抗式 persona）、Academic Peer Review Simulator（ldm2060，中英双语+可发表性策略）、Peer Reviewer for Researchers（nealcaren，连 Zotero 库生成流派审稿人 persona）
- `HughYau/AcademicForge` — 中文技能目录（收录 nature-reviewer 等）
- 阴性结论：`anthropics/skills` 官方库 21 个技能无任何学术审稿技能；`travisvn/awesome-claude-skills`、`helloianneo/awesome-claude-code-skills`、`hesreallyhim/awesome-claude-code` 均无学术审稿条目

## 5. 顶会与 OR/MS 期刊审稿指南（方法论来源，非仓库为主）

ICML 2025（Claims-and-Evidence 表单）、Transportation Science 2025（唯一逐条化 OR 期刊准则+计算实验五查）、INFORMS《OR》编辑部声明（数学+实证双轨）、NeurIPS 2025（四维+6 档 Overall）、ACL Rolling Review（可复现性 5 档锚点）、Management Science《Code and Data Disclosure Policy》（随机种子/测试算例黄金清单）、INFORMS OR 披露政策、ICLR 2025（四问+建议与评分解耦）。唯一 GitHub 来源：`informsjoc.github.io`（IJOC 论文代码仓库索引，如 `INFORMSJoC/2024.0884`）。

## 6. 当时的融合决策（主会话确认）

**采纳**（scientific-review 496→660 行，十项机制）：①Claims-and-Evidence 映射（ICML/ICLR）②数学/实证双轨（INFORMS OR）③实验红线清单（本地改编）④致命缺陷四条硬判定+总分封顶（本地 DA agent + lyra81604）⑤Reviewer 七连问（本地 DA 裁剪）⑥辩护评分+反谄媚三规则（本地）⑦锚定量表+Confidence 绑定验证深度（NeurIPS + AI-Scientist）⑧审稿纪律 10 条（TRSC 2025 + ICLR + AWT 清洁室）⑨排序标定「100 篇进前 10 吗」（AgentReview + Thelwall）⑩自检 6 问+Issue 直通 rebuttal（本地）。

**否决**（能力边界）：7 人评审团/calibration 模式（归 academic-paper-reviewer 职责）；SSoT 种子+OS 并行脚本（AlexWortega，单文件承载不了）；BibTeX 逐条核验（OpenJudge，转 zotero-paper-fetch）；清洁室硬性子代理化（AWT，降级为软规则）。

**后续候选**：ARIS 三道硬门、Rebuttal-Audit 三查——rebuttal 技能升级素材。

## 原始报告恢复方法

原始报告全文存于 ZCode 会话数据库 `~/.zcode/cli/db/db.sqlite`（表 `message`/`part`，正文在 `part.data` JSON 中 `type=="text"` 的记录）。主会话 `sess_f026d67a-d9c3-4415-b40b-eb247d4e041d`（2026-09-19 21:50），8 个子代理会话 ID 前缀均为 `sess_subagent_agent_`：966a53cd（工具箱类仓库）、b55ab8a9（LLM 自动审稿）、21af7687（科研自动化框架）、d7442e1d（审稿指南）、b0b6bcdd（本地深读）；另有两个被中断的会话（cf73becf、c0e3d4d4）无最终报告，其主题已被完整会话覆盖。本文档即由上述会话的最终报告浓缩而成（2026-09-23 恢复）。
