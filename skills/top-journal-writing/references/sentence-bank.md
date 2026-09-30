# 顶刊句式库（sentence bank）

> **使用规则**（与 SKILL.md 的纪律节配套）：
> - 每条 = 泛化模板 + 真实例句 + 出处 id（可回查 `data/patterns.jsonl` 与原文）。
> - 写作时**换词不换骨架**：模板的 `<槽位>` 填自己的内容，句式结构可复用，整句照抄是抄袭。
> - 例句是证据不是范文——它们展示"这个功能位顶刊怎么写"，不是让你模仿它的具体措辞。
> - 域标签：ai / or / mgmt / logistics / shipping，对应 `data/papers.jsonl` 的五域。没有你所在域的条目时，
>   跨域借用安全（句式是跨域通用的），但优先用本域条目对齐语域。
> - 语料：200 篇（2026-09-30 采集，见 `data/README.md`）；泛化时人工筛过一轮。

## 五域差异速记（来自语料的真实观察，写跨域投稿时校准用）

- **管理科学系（MS/POM/JOM/Omega）**：摘要常省略背景句，第一句直接 "This paper examines/studies…"；意义句最发达，"managerial insights" 是标配。
- **AI 顶会体**：背景句短促（一句话点到），几乎不写意义句，结果句必带数字与基线。
- **OR 数学体**：背景句从数学对象切入（"X is an extension of Y"），gap 句爱用否定式（"no lower bound has been established"）。
- **物流/航运**：背景句爱挂宏观议程（net zero、脱碳、韧性）；航运意义句偏政策导向（policymakers）。

---

## 背景句（background）——引言第①②层、摘要第 1 句

- 模板：`<能力/要素> is essential/critical/vital to <目标>`
  例：Reliable refusal of harmful requests is essential to the safe deployment of language models. —— arXiv:2609.35544（ai）
- 模板：`<技术> have demonstrated promising <性质> by <机制>`
  例：Looped transformers have demonstrated promising parameter efficiency by reusing layers for latent computation. —— arXiv:2609.35748（ai）
- 模板：`<方法> is a widely adopted <类别> in <领域>`
  例：K-means is a widely adopted clustering approach in signal processing and machine learning. —— arXiv:2609.34310（or）
- 模板：`<方案> offers a promising pathway to <宏观目标>`
  例：Containerized battery swapping offers a promising pathway to zero-emission inland waterway transport. —— 10.1016/j.tre.2026.105258（logistics）
- 模板：`Today, achieving <议程> is a top agenda for almost all <组织>`
  例：Today, achieving net zero in logistics and operations is a top agenda for almost all organizations. —— 10.1016/j.tre.2026.105166（logistics）
- 模板：`<主体> are increasingly required to respond to <内外部挑战>`
  例：Ports are increasingly required to respond to both internal and external market challenges. —— 10.1080/03088839.2026.2737441（shipping）
- 模板：`In recent years, <短缺/趋势> in <行业> have become increasingly prominent`
  例：In recent years, talent shortages in the shipping industry have become increasingly prominent. —— 10.1080/03088839.2026.2729879（shipping）
- 模板：`Under <条件>, <预测/估计> are prone to <风险>`
  例：Under deep uncertainty, long-range transport forecasts are prone to inaccuracy. —— 10.1016/j.trd.2026.105610（shipping）
- 模板：`<现象A> and <现象B> often undermine <系统> performance`
  例：Information distortion and incentive misalignment often undermine supply chain performance. —— 10.1287/mnsc.2025.02137（mgmt）
- 模板：`<对象> is a novel solution for <问题域>`（系统/装备类论文）
  例：The pick-and-drive system is a novel solution for warehouse automation. —— 10.1016/j.ejor.2026.09.002（logistics）

## 缺口句（gap）——引言第③层、摘要第 2 句（全文最重要的一句）

**置疑型**
- 模板：`How to <做X> both <优点1> and <优点2> still remains unclear.`
  例：How to initialize linear ViTs both efficiently and effectively still remains unclear. —— arXiv:2609.35745（ai）
- 模板：`Yet, it remains empirically unknown whether <因果问题> and <机制问题>.`
  例：Yet, it remains empirically unknown whether generative search increases consumer purchases and how search behavior changes when it can begin from expressed intent rather than keywords. —— 10.1287/mnsc.2025.02458（mgmt）
- 模板：`However, <对象> remains insufficiently understood.`
  例：However, its strategic role in market-based dispatch remains insufficiently understood. —— 10.1016/j.omega.2026.103661（mgmt）

**解耦/割裂型（管理科学与物流最常用）**
- 模板：`However, existing studies often <割裂的决策A与B>, which can lead to suboptimal <系统> performance.`
  例：However, existing studies often decouple tactical pricing from operational routing decisions, which can lead to suboptimal system performance. —— 10.1016/j.tre.2026.105239（logistics）
- 模板：`These features have been investigated individually in the literature but have not been considered simultaneously.`
  例：（原文即模板级句式）—— 10.1287/trsc.2025.0155（logistics）

**计算难度型（OR 论文）**
- 模板：`However, the problem becomes strongly NP-hard already when <结构条件>.`
  例：However, the problem becomes strongly NP-hard already when the interaction graph has treewidth two. —— arXiv:2609.35595（or）
- 模板：`However, large-scale <问题> often involve <规模> that make the search space extremely high-dimensional and computationally prohibitive.`
  例：However, large-scale network problems often involve hundreds of control decisions that make the search space extremely high-dimensional and computationally prohibitive. —— 10.1016/j.tre.2026.105256（logistics）

**理论空白型**
- 模板：`However, to the best of our knowledge, whether <开放问题> remains underexplored.`
  例：However, to the best of our knowledge, whether looping improves test-time scaling as outputs grow longer remains underexplored. —— arXiv:2609.35748（ai）

**现实摩擦型（航运常用：列举摩擦加剧失配）**
- 模板：`However, <趋势> has made <稀缺资源> even more strained.`
  例：However, the exponential expansion of market information has made experts' limited attention even more strained. —— 10.1080/03088839.2026.2717553（shipping）
- 模板：`However, <摩擦1>, <摩擦2>, <摩擦3> exacerbate <供需失配>.`
  例：However, imperfect value-added transportation services in the online channel, channel competition, limited capacity, and divergent overbooking behaviors between channels exacerbate demand-capacity mismatches. —— 10.1080/03088839.2026.2717550（shipping）

## 方法句（method）——摘要第 3 句、方法章各段首

- 模板：`We introduce <名称> (<缩写>) to <解决什么>.`
  例：We introduce Projected Distribution Matching Distillation (PDMD) to filter critic errors. —— arXiv:2609.35768（ai）
- 模板：`We propose <名称>, a framework that <以何种方式解决何种问题>.`
  例：We propose X-Reset, a framework that instead resolves exploration with human hand-object demonstrations. —— arXiv:2609.35715（ai）
- 模板：`We consider the problem of <优化目标> over <约束集合>.`
  例：We consider the problem of minimizing a sparse quadratic function over the unit hypercube. —— arXiv:2609.35595（or）
- 模板：`We derive an exact and explicit <结构> that characterizes the optimal <策略/解>.`
  例：We derive an exact and explicit threshold structure that characterizes the optimal control policy. —— arXiv:2609.35153（or）
- 模板：`We study <对象> in <实验/市场设置>.`
  例：We study demand for symmetric and asymmetric information sources in the laboratory. —— 10.1287/mnsc.2024.08449（mgmt）
- 模板：`We consider a <决策主体> that <行为设定>.`
  例：We consider a monopolist that over time offers its customers new versions of an evolving product. —— 10.1177/10591478261492947（mgmt）
- 模板：`For <任务环节>, we propose a(n) <算法类型>.`
  例：For posterior inference, we propose an Markov chain Monte Carlo algorithm. —— 10.1287/trsc.2026.0063（logistics）
- 模板：`We validate our approach using real-world data from <平台/企业>.`
  例：We validate our approach using real-world data from a major food delivery platform. —— 10.1287/trsc.2025.0149（logistics）
- 模板：`We analyze a case study using data from <运营商>, where <设定细节>.`
  例：We analyze a case study using data from a tramp shipping operator, where diesel, LNG, ammonia, LPG, and methanol are the available fuels. —— 10.1016/j.martra.2026.100153（shipping）
- 模板：`We propose a novel <框架名> integrating <构件A> and <构件B>.`
  例：We propose a novel risk management framework integrating an EUA Price Call Option (EPCO) and a Carbon Emission Equipment Loss Insurance (CEELI). —— 10.1016/j.trd.2026.105644（shipping）

## 结果句（result）——摘要第 4 句，必须带数字

- 模板：`In <实验设置>, <方法> reduces <指标> by <N>% relative to <最强基线>.`
  例：In regional-routing experiments, PRISM reduces median worst-case regret by 50.2% relative to the strongest baseline. —— arXiv:2609.35569（ai）
- 模板：`<方法> uses <N>% fewer <资源> on average than <基准策略> at matched <质量>.`
  例：In offline budget-control replay, TokenCast uses 21.3% fewer tokens on average than a fixed-budget policy at matched trace completion. —— arXiv:2609.35760（ai）
- 模板：`Numerical experiments show that <结构/机制> is associated with reductions in <计算/成本指标>.`
  例：Numerical experiments show that the one-factorization structure and the correction after the arc step are associated with reductions in computation time. —— arXiv:2609.34275（or）
- 模板：`This approach yields an improved <理论条件> and outperforms the previous <方法>.`
  例：This approach yields an improved spectral-radius convergence condition and outperforms the previous method. —— arXiv:2609.33682（or）
- 模板：`The results show that <干预> reduces <痛点> and improves <福利> relative to <对照情形>.`
  例：The results show that storage reduces imbalances and improves welfare relative to a no-storage case. —— 10.1016/j.omega.2026.103661（mgmt）
- 模板：`We show that this benefit of <机制> results in higher <利润> when <成本条件>.`
  例：We show that this benefit of event pacing results in higher profits when fixed or variable costs are high. —— 10.1177/10591478261492947（mgmt）
- 模板：`<成本指标> can be reduced by up to <N>% by <做法>.`
  例：Operational costs can be reduced by up to 27% by reallocating and reusing more than half of the robots deployed. —— 10.1287/trsc.2025.0523（logistics）
- 模板：`Numerical results show that the <设计> consistently yields the best performance.`
  例：Numerical results show that the private design with sequential release consistently yields the best performance. —— 10.1287/trsc.2025.0017（logistics）
- 模板：`The finding of the analysis is that the introduction of <政策> increased <结果> by <N>%.`
  例：The finding of the analysis is that the introduction of this policy increased vehicle fleet renewal by 2.2%. —— 10.1016/j.trd.2026.105603（shipping）
- 模板：`The results reveal <N> typical <类型/轨迹>, with significant differences in <结果变量> across them.`
  例：The results reveal four typical career trajectories, with significant differences in career success across them. —— 10.1080/03088839.2026.2729879（shipping）

## 意义句（implication）——摘要第 5 句、讨论第④步

- 模板：`A case study with <对象> illustrates the managerial insights for <策略>.`
  例：A case study with SaaS clients illustrates the managerial insights for proactive retention strategies. —— 10.1016/j.omega.2026.103653（mgmt）
- 模板：`Our results advance the theory of <领域> and provide actionable insights for <企业> to <行动>.`
  例：Our results advance the theory of safety management and provide actionable insights for industrial firms to effectively operationalize DSM. —— 10.1002/joom.70048（mgmt）
- 模板：`These findings provide empirical insights for future <模型/研究> that <扩展方向>.`
  例：These findings provide empirical insights for future consumer search models that allow search to originate at the intention-expressing stage. —— 10.1287/mnsc.2025.02458（mgmt）
- 模板：`The proposed <框架> provides empirically grounded insights into <应用场景1>, <应用场景2>, and <应用场景3>.`
  例：The proposed critical encounter extraction framework provides empirically grounded insights into MASS development and testing, maritime situational awareness enhancement, and traffic management. —— 10.1016/j.tre.2026.105261（logistics）
- 模板：`<决策者> should therefore establish <多维协同体系> rather than <单一工具>.`
  例：Policymakers should therefore establish a multidimensional, coordinated policy system rather than a single tool. —— 10.1080/03088839.2026.2727588（shipping）
- 模板：`Moreover, this study offers policy implications to enable more effective, data-driven <决策/管理>.`
  例：Moreover, this study offers policy implications to enable more effective, data-driven decision-making and market risk management. —— 10.1080/03088839.2026.2717553（shipping）

## 引言缺口句（gap_intro）——引言正文里的展开版缺口（摘要挖不到，全文挖掘所得）

- 模板：`How to <X> is therefore a question of practical significance, yet still remains unclear.`
  例：How to initialize linear ViTs efficiently and effectively is therefore a question of practical significance, yet still remains unclear. —— arXiv:2609.35745（ai）
- 模板：`Yet our understanding remains limited even for <最基本情形>.`
  例：Yet our understanding remains limited even for basic monotone Lipschitz inclusions. —— arXiv:2609.35631（or）
- 模板：`Under <假设/设定>, to the best of our knowledge, no <结果类型> has been established specifically for <问题类>.`
  例：Under averaged smoothness, to the best of our knowledge, no lower bound has been established specifically for NC-SC minimax optimization. —— arXiv:2609.35206（or）

## 贡献句引导（contribution）——引言第④层开头

- 模板：`Our (main) contributions are/can be summarized as follows:`
  例：Our main contributions can be summarized as follows. —— arXiv:2609.35595（or）
- 模板：`In summary, our primary contributions are as follows:`
  例：In summary, our primary contributions are as follows: —— arXiv:2609.35745（ai）

## 收口句（conclusion）——结论第 1 句

- 模板：`In this paper, we have developed a systematic <理论/方法> for <问题>.`
  例：In this paper, we have developed a systematic theory for (exponential) output-to-state stability of linear infinite-dimensional systems with bounded output operators. —— arXiv:2609.35735（or）
- 模板：`We presented a <统一视角/框架> that <分解出哪些组成部分>.`
  例：We presented a unified view of distributional training that separates sampling, encoding, distribution modeling, and matching discrepancy. —— arXiv:2609.35763（ai）
- 模板：`We present <名称>, a <工件> for <任务>, built on <方法基础>.`
  例：We present Peppy, an AI-assisted workflow for first-order optimization, built on the domain-specific machinery of PEP and the systematic framework of Yoon et al. (2026). —— arXiv:2609.35762（or）
- 模板：`In this work, we prove <理论保证> for <形式化对象> and demonstrate <优势>.`
  例：In this work, we prove convergence guarantees for a mathematical formalisation of Soft Actor Critic and demonstrate theoretical advantages of having a target policy arising from mirror descent. —— arXiv:2609.35466（or）

## 局限展望句（limitation）——讨论/结论第④步

- 模板：`The main open question left by <定理/结果> is <权衡>.`
  例：The main open question left by Theorem 5.1 is the tradeoff between the deterministic and stochastic terms. —— arXiv:2609.35631（or）
- 模板：`Moreover, we do not incorporate <要素> in this work, which remains a challenging direction for future work.`
  例：Moreover, we do not incorporate explicit critic dynamics in this work which remains a challenging direction for future work. —— arXiv:2609.35466（or）
- 模板：`Future work could extend <本工作> to support <更广范围> and thereby cover <更多情形>.`
  例：Future work could extend Peppy to support a broader range of proof structures and thereby cover more algorithms and forms of convergence analysis. —— arXiv:2609.35762（or）
- 模板：`Future work may also include <具体扩展>, which <更进一步的做法>.`
  例：Future work may also include replacing the present hard E-step with the standard EM E-step, which takes expectations with respect to the posterior distribution over latent trajectories. —— arXiv:2609.35758（ai）

---

## 库的生长（模式 C 拆解范文时使用）

拆解中发现库外优秀句式时，按上面条目格式追加到对应小节，必须带例句与出处 id；追加前先查重（同功能位同结构即视为已有）。本文件是**人工泛化层**，不随 `mine_patterns.py` 自动覆盖——语料再生后需要人工重审一次，剔除过时条目、补充新证据。
