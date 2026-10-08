# hedge-audit 判定词表与样例

词表是初筛网，不是判决书：命中只说明"值得读上下文"，定性永远靠 R1–R5 分类与 however 二分测试（SKILL.md）。

## 一、marker 正则（机械扫描）

主扫与副扫见 SKILL.md 管线 ③。补充深扫（主副扫命中稀少、但仍怀疑有防御性写作时）：

```bash
grep -nEi "it is (possible|plausible) that|one (possible|plausible) explanation|\
a likely explanation|we cannot exclude|cannot be excluded|remains to be|\
in part due to|at least in part|should not be (over|overly) interpret|\
warrant(s)? caution|caution is warranted|must be interpreted|may have (under|over)estimat" manuscript.tex
```

## 二、退路从句词表（R1 核心）

| 类 | 短语 |
|---|---|
| 因果免责 | does not necessarily imply / mean；correlation … does not imply causation；does not prove；cannot establish causality |
| 未测因素 | other unmeasured / confounding / unobserved factors may (also) …；residual confounding cannot be excluded |
| 谨慎阅读 | should be interpreted with caution；warrant caution；should be viewed as … rather than … |
| 效果免责 | non-significant does not mean no effect；the absence of significance does not imply …；may underestimate / overestimate |
| 外推免责 | may not generalize；our results may not extend to … |
| 留后路 | further research / studies are needed；future work should …（出现在 Results 时） |
| 先行声明 | rather than claiming …；we do not claim …（出现在 Results 时；出现在 Conclusion/Limitations 是合法定位句） |

## 三、null 解释词表（R2）

insufficient sample size / statistical power；ceiling / floor effects；measurement error；residual confounding；the instrument / indicator may not capture …；the observation window may be too short。

出现在 Results → R2（移 Discussion 或 Limitations）；出现在 Discussion/Limitations → 正常，不判。

## 四、hedge 堆叠（R4）

may possibly；might potentially；could perhaps；it seems possible that … may …。

一句内 may / might / could / perhaps / possibly / likely / seemingly 计数 ≥2 即命中，压缩为单个修饰词或删。

## 五、中文稿 marker

但 / 然而 / 不过 / 需要指出的是 / 值得注意的是 / 并不一定 / 并不意味着 / 尚不能排除 / 可能存在其他（未测量）因素 / 应谨慎解读 / 有待进一步研究。

中文"但"高频，只审 Results 区间内、后接免责内容者；表逻辑推进的"但"按 however 二分测试放行。

## 六、处置决策树

```
命中 hedge
├─ 所在章节？→ 对照 SKILL.md 章节规则表
├─ 全稿通用（任何章节，无豁免）：
│  R4 堆叠      → 压成单个修饰词或删
│  R3 撒胡椒面  → Limitations 已覆盖？删 ： 集中到 Limitations
├─ 最严三区（Results / Abstract 头条句 / Introduction 贡献句）：
│  however 二分测试 → 帮读者（逻辑对比、推进论证）→ KEEP
│                    → 保作者 → R1：后半句有实质信息？移 Discussion ： 删
│                              R2：解释机制 → 移 Discussion；让步范围 → 移 Limitations
├─ Discussion：让步后再推进 → KEEP；纯退路 / 与 Limitations 重复 → 删或并入
├─ Methods / Conclusion 定位句 / Limitations / Abstract 结尾单句 → KEEP（记录，不计病）
```

**搬迁完整性**：每个 MOVE 先查目标章节现有文本——内容已存在改判 DELETE（去重）；论文没有独立 Discussion/Limitations 时，报告标注"无处可搬"，交用户决策，不擅自定去留。

## 七、样例

**R1：删后半句**

- 原：No significant association was observed between A and B (β = 0.04, 95% CI: −0.03–0.11, p = 0.27). However, this does not necessarily mean that A and B are unrelated.
- 改：No significant association was observed between A and B (β = 0.04, 95% CI: −0.03–0.11, p = 0.27).
- 理由：前句已完成报告职责；"为什么没结果"是 Discussion 的问题，不是 Results 必须回答的。

**R5：保留（防误报）**

- "Higher A was associated with higher B (β = 0.21, p < 0.001)." ——动词与观测设计相符，句尾无退路从句 → 干净。
- Abstract 结尾一句 "…, suggesting MAKO can deliver reliable decision support." ——单句、紧随数据、全局唯一 → KEEP。

**Introduction 贡献弱化（最严三区）**

- 原：We attempt to address the three-echelon ECR problem…
- 改：We address the three-echelon ECR problem…
- 理由：贡献句里的 attempt / hope to / try to 是预防性认输——做了就是做了，成败评价留给读者与审稿人。

**Abstract 头条弱化（最严三区）**

- 原：Our results may suggest that knowledge loading could potentially improve formulation quality…
- 改：Knowledge loading raises the strict success rate from 36.0% to 76.0% (95% CI …).
- 理由：头条数字前加 may + potentially 双重弱化是 R4；精度交给置信区间，不交给形容词。

**Discussion 合法让步（防误报，全稿规则）**

- "This improvement is likely attributable to the hinterland-gated arc rules, though part of the gain may stem from prompt formatting." ——让步后仍推进论证（给出主因判断）→ KEEP。
- 反例（病）："This improvement may be due to several factors, though it is difficult to determine which." ——只让步、不推进、不给出任何判断 → 过度防御，压紧或删除。

**边界案例（实测：mako 稿，OR/LLM 方向）**

- Results 内 "the +3.3 pp gain over MAKO-knowledge is modest on this instance, where knowledge loading already removes most formulation errors." ——前半是诚实的效应量报告（KEEP 倾向），后半是机制解释（Discussion 味）；无独立 Discussion 的 CS 风格稿可容忍，判"轻微，可选移出"。
- Conclusion 内 "Rather than claiming a task-agnostic multi-agent solver, this result speaks to operational usefulness …" ——位置正确（结论定位句）→ KEEP。
- Related Work 内 "However, existing multi-agent optimization frameworks still exhibit several limitations." ——对他人工作的批判性转折，是进攻不是防御 → KEEP。

## 八、however 二分测试

问：however / 但 之后的小句，删掉后读者损失信息吗？

- 损失（它是论证的一步：对比、让步后再推进）→ 逻辑对比，KEEP。
- 不损失（它只取消作者的责任：免责、留退路、预防性认错）→ R1。

等价判别：把 however 之后的内容主语换成作者——"这保护的是作者还是读者？"
