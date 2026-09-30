---
name: zotero-pdf-highlighting
description: 按 zotero-paper-note 阅读笔记的五个章节（研究问题/数学模型/求解方法/案例研究/实验结果，严格 5 类），对 Zotero 条目挂载的文献 PDF 中的**关键词**写入分类颜色高亮——红 #ff6666、黄 #ffd400、绿 #5fb236、蓝 #2ea8e5、紫 #a28ae5（Zotero 官方批注调色板）。当用户要求"按笔记高亮这篇 PDF""给文献关键词上色""把阅读笔记落到 PDF 上""分类高亮这篇文献""五色标记"，或英文 "highlight the PDF by note categories" / "color-code the paper" 时使用。写入文件内嵌原生 PDF 高亮，Zotero 阅读器直接显示；完全离线，任意 Zotero 版本可用。
license: MIT
---

# Zotero PDF 分类高亮技能

把 `zotero-paper-note` 产出的五章节阅读笔记"落"回 PDF 本体：研究问题红、数学模型黄、求解方法绿、案例研究蓝、实验结果紫。重读论文时按颜色 10 秒定位每类内容，五类信息在 Zotero 阅读器里一眼可辨。

## 定位与边界

- **管**：把高亮写进 PDF 文件本身（文件内嵌批注）。Zotero 阅读器直接显示（带只读锁），可正常添加笔记；完全离线，不依赖 Zotero API，任意 Zotero 版本可用。
- **不管**：Zotero 原生批注条目（可在侧栏按颜色过滤的那种）——那是将来的 Zotero 10 本地 API 路线，需要时另行立项，本技能不碰。
- **上游依赖**：条目下已有五章节阅读笔记（`zotero-paper-note` 产出）；没有笔记时先跑上游技能，或让用户口述/粘贴五类要点。
- 依赖 `pymupdf`（AGPL；uv 按脚本内联声明自动安装，仅本地运行，无分发问题）。

## 类别-颜色契约（严格 5 类）

| 类别 | 颜色 | 对应笔记一级章节 |
|---|---|---|
| 研究问题 | 🔴 #ff6666 | `# 研究问题` |
| 数学模型 | 🟡 #ffd400 | `# 数学模型` |
| 求解方法 | 🟢 #5fb236 | `# 求解方法` |
| 案例研究 | 🔵 #2ea8e5 | `# 案例研究` |
| 实验结果 | 🟣 #a28ae5 | `# 实验结果` |

映射的唯一事实源是 `references/category-colors.yaml`（同文件还配置 Zotero 数据目录 `data_dir`）。类别严格 5 类：plan 里出现其他类别（如"相关工作"）脚本直接拒绝。跨论文必须用同一套颜色语义，"看颜色知类别"才成立；用户要求改色或换 `data_dir` 只改 yaml，不动脚本。

## 工作流程

### Step 1: 定位条目、笔记与附件

1. 用 `zotero_search_items` / `zotero_get_item_metadata` 定位文献条目，记下 `item_key` 与 **PDF 附件 key**。
2. 读取条目下的「阅读笔记」（五章节）。MCP 工具读不到笔记时：请用户把笔记贴进对话，或改用项目根 `literature.jsonl` 里同 `item_key` 的结构化记录——`positioning` / `method.*` / `decision_vars` / `case` / `key_results` 正好覆盖五类别。
3. 提醒用户**关闭 Zotero 里正打开的这份 PDF**：阅读器开着时看不到外部写入的高亮，也可能缓存旧文件。

### Step 2: 定位 PDF 文件

附件文件在 `<data_dir>/storage/<附件 key>/` 下（`data_dir` 来自 category-colors.yaml，默认 `~/Zotero`）。`ls` 确认该目录只有一个 .pdf；用户直接给路径也行（plan 的 `pdf` 字段优先于 `attachment_key`）。

### Step 3: 抽取逐页归一化文本

```bash
uv run <本技能目录>/scripts/extract_pages.py --pdf <PDF 路径> --out /tmp/pages.json
```

脚本做三类归一化：行内空白折叠、跨行断词连字符还原（`distribu-` 换行 `tion` → `distribution`）、跨行以单空格拼接，输出逐页 JSON。**片段必须从这份输出里选**，匹配才有保证。

### Step 4: 写高亮计划 plan.json

对照笔记五章节的内容，提炼各类**领域关键词**，从 pages.json 的文本里**逐字复制**（规则见下），写到 `/tmp/plan.json`（schema 与示例见 `references/plan-example.json`）：

```json
{
  "pdf": "<PDF 绝对路径>",
  "spans": [
    {"category": "研究问题", "text": "empty container repositioning"}
  ]
}
```

关键词**默认每词只高亮首次出现处**——高亮是"这个术语在文中哪里首次登场"的路标，一个关键词标多次就是重复。需要放开时给该 span 加 `"max_hits": 0`（全文标注），整份 plan 统一调整用 `"max_hits_default"`。落点想限定到某章节/页面时，可选加 `"pages": [起, 止]`（1 基含端区间）或 `"page_hint": 页码`（也用于消歧）。

### Step 4.5: 元词/泛词信号检查

草拟完候选词、写入 plan 之前，跑信号层脚本把"换文测试"机械化：

```bash
uv run <本技能目录>/scripts/check_terms.py --words "<候选词逗号分隔>" [--item-key <条目>]
uv run <本技能目录>/scripts/check_terms.py --plan /tmp/plan.json
```

四信号 → 三判级：**结构/仪表黑名单**（case study、CPU time…）与**领域泛词表**（supply chain、liner shipping、机器学习…，`references/term-lexicon.yaml` 可按研究方向扩充）命中 → 红旗；**库内 DF ≥15%**（词出现在 Zotero 库 ≥15% 篇的标题/摘要/标签）→ 红旗，8–15% 灰区（数据自适应兜底）；**方法构词模式**（`修饰语+方法通名`：two-stage stochastic programming、组合预测）→ 术语绿灯。只建议不拦截：红旗/灰区逐个过三测试再定稿。DF 依赖 zotero.sqlite 快照，/mnt/c 读取偶发撕裂时自动跳过（黑名单/泛词表/方法模式不受影响）。

### Step 5: dry-run 核对

```bash
uv run <本技能目录>/scripts/highlight_pdf.py --plan /tmp/plan.json --dry-run
```

退出码 1 表示有"未找到"关键词——几乎总是拼写/形态被改写了，回 Step 4 从 pages.json 重新逐字选取，直到 0 未命中再继续。

### Step 6: 写入并交付

去掉 `--dry-run` 正式执行，把报告（类别 × 颜色 × 页码 × 状态）贴给用户，并附两句提醒：

- Zotero 里关闭该 PDF 标签页后重开即可看到高亮；
- 多设备用户：Zotero 默认不重传已上传过的文件，需手动触发同步（或 Settings → Sync → Reset File Sync History）。

## 关键词选取规则（质量的关键）

1. **只用领域术语，禁用元词**：判据是——这个词描述"论文研究的对象世界"（术语），还是"论文文本的组织与测量过程"（元词）。三测试任一不过即弃：
   - **换文测试**：换一篇同领域论文这词还会原样出现？（case study / CPU time 换哪篇都在 → 元词；AEU6 / LSTM-SVR 专属这篇 → 术语）
   - **笔记测试**：它会作为实质内容写进五章节笔记某一行吗？笔记只写内容不写结构——笔记不收的词，高亮也不收。
   - **专指测试**：同类有更具体的词就用具体的（average profit 优于 profit，更优于 objective function）。
   几乎总是术语：算法/框架名（Benders decomposition、two-stage stochastic programming、LSTM-SVR）、案例专名（AEU6、Busan New Port、中欧班列）、论文标题与关键词行里的词、发现围绕的量与结论短语（average profit、预测误差、significantly better）。几乎总是元词：章节结构词（case study、numerical example、instance、test problem、experiment、problem statement、model formulation、computational results）、测量仪表词（CPU time、runtime、solution quality、training time；例外：论文贡献本身就是它）。灰区泛化建模词（objective function、decision variable、constraint）：先按专指测试换具体名，换不出且该类缺词则整类跳过，不硬凑。论文没有某类内容（如纯数值论文无真实案例）同样整类跳过并说明。
2. **逐字复制**：关键词必须取自 Step 3 输出的归一化文本，禁止改写、翻译、缩略。笔记是中文概括，PDF 是英文原文——匹配发生在 PDF 原文上，不是笔记文本上。
3. **避免裸的常见词**：单个高频泛词（cost、model、network）会高亮满篇，要么并入多词术语（*unmet demand cost*），要么加 `page_hint`；论文自造名词/缩写（SOP-MAS 类）不受此限。
4. **宁缺毋滥**：笔记某类内容在 PDF 里找不到可靠对应关键词时，跳过并说明，不硬凑；关键词数量以"扫颜色能定位该类内容"为准，不是越多越好。
5. **同一关键词只归一类**：跨类内容重复时选最贴近的类别，不重复高亮。

## 匹配行为（脚本自动处理，无需在 plan 里规避）

- **整词对齐**：命中片段尾邻字符若是字母/数字（复数/屈折），高亮自动向后吞并整个词（关键词 `leased container` 会完整高亮 `leased containers`）；前邻字符若是字母/数字，说明命中嵌在更长复合词里，自动跳过（`linear programming` 不会误配 `nonlinear programming`）。
- **连字自动展开**：PDF 排版连字（proﬁt 里的 ﬁ、ﬂow 里的 ﬂ）在抽取与匹配两侧统一展开为普通字母——关键词按常规拼写写（`average profit` 即可），无需带连字字符。
- **大小写敏感**：关键词照抄 pages.json 里的出现形态——有的术语只以特定大小写出现（如关键词行的 `Approximate dynamic programming`），换个形态就匹配不到。
- **出现次数上限（max_hits）**：默认每词 1 处（区间/全文内首次出现）；span 级 `"max_hits": 0` 全文标注、`"max_hits": N`（>1）均匀分布取 N 处，plan 级 `"max_hits_default"` 统一调整。被截取时报告注明"全文命中 N 处，取首处/均匀取 M 处"。
- **可选锚定（pages / page_hint）**：默认落点是每词首次出现处，不做章节限定；确实想把某词固定到特定章节或页面时（附录在 References 后、只标某节的用法），加区间显式指定，显式锚定不过滤参考文献区。
- **参考文献区自动跳过**：References 标题之后的命中是文献列表里的标题噪声，自动跳过并在报告计数；附录排在 References 之后的论文，用 `page_hint` 强制写入。
- **跨色重叠提示**：不同类别关键词或原自带高亮在同一位置叠加时，报告尾部列出页码——多因两个关键词共享子串（如 `container slot allocation` × `allocation policy`），必要时收窄一方归属或改用 page_hint。

## 幂等与重跑

- 脚本对"同位置 + 同色"的已有高亮自动跳过——重跑、补片段、加新类别都安全，不会叠双层。
- 文件内嵌高亮在 Zotero 阅读器里是**只读锁定**的：不能在阅读器里删除。要清除：用原始文件替换（重新同步/重新下载附件），或在阅读器里 File → Import Annotations 转成 Zotero 原生批注（转换后从文件剥离，之后可在 Zotero 里管理）。

## 边界与故障排查

| 症状 | 处置 |
|---|---|
| extract 输出为空 / 全空页 | 扫描件无文本层，跳过并告知用户 |
| 脚本报"PDF 已加密" | 跳过并告知用户 |
| "未找到"关键词 | 拼写/形态/大小写被改写，回 Step 4 逐字重选 |
| 关键词只命中在参考文献列表 | 脚本自动跳过并报告；确属正文内容时用 page_hint 指页 |
| 写入后阅读器不显示 | 关闭该 PDF 标签页重开 |
| 附件目录有多个 PDF | plan 里用 `pdf` 字段指明 |
| 其他设备看不到高亮 | 手动触发同步或重置文件同步历史 |

## 与 zotero-paper-note 的关系

上游技能：笔记五章节是本技能的类别来源，`literature.jsonl` 是备选输入。做完笔记后用户说"顺手把这篇高亮了"，直接从 Step 1 接续，无需重读论文。

## 触发示例

```
用户：按笔记给 6XL3KWIB 那篇的 PDF 上色
→ [定位条目/笔记/附件 → extract_pages.py → 写 plan → dry-run 0 未命中 → 写入 → 报告 + 两句提醒]

用户：笔记做完了，把五类内容在高亮里标出来
→ [上游 zotero-paper-note 刚产出笔记 → 直接进本技能流程]

用户：重跑一下高亮，补几个数学模型的关键词
→ [改 plan 只加新 spans → 执行（已有高亮自动跳过）]
```
