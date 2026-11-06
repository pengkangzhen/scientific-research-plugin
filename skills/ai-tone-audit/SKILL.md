---
name: ai-tone-audit
description: >
  Chinese academic AI-tone (LLM-ese / slop) audit and optional surgical
  de-AI rewrite — targets twelve structural and lexical tells in Chinese
  theses, journal papers, and grant proposals: throat-clearing macro
  openers, didactic signposts ("值得注意的是", "综上所述"), inflated value
  clichés and bureaucratic buzzwords ("赋能", "闭环", "具有重要意义"), binary
  contrast shells ("不是…而是…"), mechanical four-character chains, non-step
  enumerations, paragraph-ending summary tails, nominalized weak verbs
  ("对…进行分析"), false agency, numberless evaluative claims, bold/em-dash
  tics, and flat sentence/paragraph rhythm. Three-stage funnel:
  deterministic density scan → isolated-context reviewer (delete /
  concretize / restructure / keep / route; never synonym-swap or invent
  facts) → user-confirmed rewrite gated by regression re-scan. Read-only
  report by default. Triggers: "去AI味", "AI味太重", "检查AI腔", "去机器味",
  "像AI写的", "ai-tone-audit", "audit AI tone", "deslop Chinese paper".
license: MIT
---

# ai-tone-audit：中文学术写作去 AI 味审计

## 定位与边界

- **管**：中文学术手稿（硕博学位论文、中文核心期刊论文、基金本子、开题/技术报告，支持 `.tex` / `.docx` / `.md` / `.txt`）中的 **12 类 AI 腔（Z1–Z12）**——从表面的高频路标词、公文拔高套话，到深层的二分对照壳、欧化弱动词、无数字空泛断言与句法节奏均质化。
- **不管（按病种分流）**：
  - 防御性让步、Results 段尾免责退路、同句对冲词堆叠 → 转交 `hedge-audit`
  - AI 自造复合名词标签、项目黑话与跨节术语漂移 → 转交 `term-audit` / `jargon-check`
  - 英文手稿语法措辞润色 → `paper-polishing`；章节骨架重搭 → `top-journal-writing`；科学性与实验设计评审 → `paper-review`
  - **不做商业「降 AIGC 率 / 洗稿」**：AIGC 检测器假阳性高且易诱导破坏学术准确性的同义词替换。本技能唯一判准是**信息密度与领域专家读感**。
- **默认只读审计，改写须经用户确认**：跑完 Stage 1 + Stage 2 输出审计报告后**立即停下**，把判定表与 `⟨作者补：…⟩` 事实清单交给用户裁决；仅当用户明确指示落地修改时才进入 Stage 3。

## 核心去味法则：三动作一禁令

| 动作 | 适用病理 | 执行准则 |
|---|---|---|
| **删（DELETE）** | 零信息背景铺垫（Z1）、讲义路标词（Z2）、空喊意义与段末升华（Z3/Z7） | 整句或短语直接剥离；删后事实命题与上下文逻辑毫发无损即为删对 |
| **实（CONCRETIZE）** | 无数字性能断言（Z10）、空泛价值拔高（Z1/Z3） | 替换为手稿**已存在**的数值、算例规模、耗时、对比基准或机理；手稿无现成事实时**严禁编造**，一律标 `⟨作者补：…⟩` 向作者提问 |
| **改（RESTRUCTURE）** | 二分对照壳（Z4）、非步骤枚举（Z6）、欧化弱动词（Z8）、抽象施事（Z9）、节奏均质（Z12） | 弱动词还原为强动词（「对模型进行求解」→「求解模型」）；补回缺失主语；拆解「不是…而是…」为直陈句；长短句错落打断节拍器节奏 |
| **禁（NEVER）** | **同义词替换打地鼠**（「至关重要」→「极为关键」、「赋能」→「助力」） | 换汤不换药只会制造次级套话，Stage 3 回归扫描直接拦截 |

完整病理定义、合法豁免情形与前后改写样例见 `references/tells.md`。

## 三段漏斗管线

```
待审手稿 (.tex / .docx / .md / .txt)
  │
  │ Stage 1：确定性扫描（scripts/scan_tells.py，零模型）
  ▼
分章节密度表 + 行号命中清单 (scan.md + scan.json)
  │
  │ Stage 2：独立上下文审稿（子智能体只读审计，见 references/reviewer-ticket.md）
  ▼
结构化审计报告 + 需作者补充的事实清单  ◀── 【默认终点：停下等用户确认】
  │
  │ Stage 3：外科式改写 + 回归闸门（仅在用户确认并补齐事实后执行）
  ▼
edit_file 最小粒度落盘 → scan_tells.py --compare 回归校验（零新增命中且总分下降）
```

### Stage 1：确定性扫描（零模型）

先跑脚本获取全稿与各章节的客观密度分布，定位重灾区（遵循 `WP:AISIGNS`「看聚集密度、不因单词定罪」原则）：

```bash
uv run skills/ai-tone-audit/scripts/scan_tells.py <manuscript> \
  --json /tmp/ai_tone_before.json --md /tmp/ai_tone_before.md
```

- 支持 `.tex`（自动展开 `\input`/`\include`，剥离公式/图表/代码/参考文献环境）、`.docx`、`.md`、`.txt`。
- 若 `skills/ai-tone-audit/data/baseline_stats_zh.json` 存在（或通过 `--baseline` 指定），自动加载 ≤2022 人类基线计算经验分位阈值与各章 `z` 分数；否则使用暂定阈值并在报告首行如实声明。
- 章末「本章小结 / 结论」内的单次「综上所述」自动按章节标题规则豁免，不计入扣分。

### Stage 2：独立上下文审稿（默认终点）

写作模型对自己刚生成的腔调有盲区。读取 `references/reviewer-ticket.md`，派发**未参与本稿写作的只读子智能体**（如 `research` 子智能体）执行上下文审计：

1. 将手稿路径、`/tmp/ai_tone_before.md`、`skills/ai-tone-audit/references/tells.md` 填入工单模板派审；超过 15,000 字的长稿按章切分并行派单。
2. 审计员逐处核查前后 2–3 句上下文，执行两项关键双向校准：
   - **去误报（判「留」）**：标准学科术语四字枚举（Z5）、真实算法/证明步骤枚举（Z6）、符号定义节规整句式（Z12）一律放行并注明理由；
   - **抓漏网**：通读捞出正则未覆盖的空心车轱辘话段落、跨句同义反复、缺乏主语或具体对象的泛泛之谈。
3. 将审计报告呈现给用户，重点高亮 **「需作者补充的事实清单（`⟨作者补：…⟩`）」**，随后结束本轮，等待用户确认哪些条目要改、补充哪些真实数据。

**降级路径**：当前运行环境不支持子智能体时，在主会话严格按 `references/tells.md` 与 `references/reviewer-ticket.md` 契约逐章自审，并在报告首行注明「审计非隔离上下文」。

### Stage 3：外科式改写与回归闸门（用户确认后）

用户确认改写范围（并提供槽位事实，或指示保留 `⟨作者补：…⟩` 占位符）后：

1. **写前读取与最小替换**：先 `read_file` 校验目标行段最新内容，再用 `edit_file` 仅替换必要的最小连续行块（不重写无关健康句子，不碰 `.docx` 二进制裸写——`.docx` 手稿输出逐段对照修改稿供作者粘贴）。
2. **不变量核查**：LaTeX 命令、`label`/`ref`/`cite` 键值、数学公式、原有实验数字与核心论断必须 100% 守恒；未获作者提供的数据保留 `⟨作者补：…⟩` 显式标记，绝不脑补。
3. **强制回归闸门**：

```bash
uv run skills/ai-tone-audit/scripts/scan_tells.py <manuscript> \
  --json /tmp/ai_tone_after.json --compare /tmp/ai_tone_before.json
```

- 闸门通过条件：**新增命中数为 0**（拦截「打地鼠」式次生套话）且**总加权分下降**（退出码 `0`）。
- 若退出码非零，定位新增命中当场修正并重跑，直至闸门通过。

## 防误报保留清单（Keep-list，下判定前必核）

- **标准学科四字术语并列**：「整数规划、动态规划与鲁棒优化」「精确求解、启发式规则与仿真评估」→ 留。
- **真实算法/实验/证明步骤**：「首先初始化可行解……其次求解子问题……最后更新上界」→ 留。
- **章末小结 / 全文结论的单次收束词**：标题含「小结 / 结论 / 总结」节内的单处「综上所述」→ 留（脚本已自动豁免）。
- **带紧邻数据支撑的程度词**：同句或紧邻下一句已给出具体数值/表号/p 值的「显著降低（由 14.2 h 降至 9.6 h，p < 0.01）」→ 留。
- **定理/定义环境内的首次加粗术语**与符号说明节的天生短句序列 → 留。

## 生成端预防与人类基线校准

- **起草前预防**：用 AI 辅助起草中文论文、基金本子或回复信前，可先读取 `references/positive-style.md`（14 条纯正向中文学术风格规范，零禁用词清单，规避粉色大象反弹）。
- **课题组人类基线校准**（推荐）：收集课题组或同领域 **2022 年及以前** 的中文论文全文（`.tex`/`.docx`/`.md`），运行 `scripts/build_baseline.py` 生成经验基线，后续扫描即自动启用领域专属阈值与 `z` 分数（详见 `data/README.md`）：

```bash
uv run skills/ai-tone-audit/scripts/build_baseline.py \
  --corpus "published_le2022/*.tex" "theses_le2022/*.docx" \
  --desc "课题组 ≤2022 中文论文全文"
```
