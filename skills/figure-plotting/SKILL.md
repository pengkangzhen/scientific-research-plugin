---
name: figure-plotting
description: >
  Data visualization and plotting. Use whenever the user asks to draw, plot,
  or redraw a figure, or mentions figure, plot, matplotlib, visualization,
  data charts, diagrams, algorithm flowcharts, framework diagrams, topology
  graphs, bar/line/scatter/box plots, heatmaps, Pareto fronts, network
  graphs, convergence curves, CJK figures, thesis figures, shipping routes,
  geographic networks, world maps, land avoidance, or asks about drawio,
  math mode, mathematical symbols, or LaTeX rendering. Covers the full spec
  for data charts (Python/matplotlib) and diagrams/flowcharts (drawio):
  figure contract, Times New Roman font (CJK serif fallback), colorblind-safe
  palettes, mandatory legend audit (export fails when a series lacks a
  legend), vector PDF export with font-embedding verification, script-to-disk
  and iteration conventions, searoute land-avoiding shipping-route generation
  with land-crossing detection.
license: MIT
---

# 绘图技能（figure-plotting）

## 第 0 步：图契约（写代码之前）

动笔前先用两三行确认（可静默完成，复杂多面板图须向用户展示）：

1. **核心结论**：这张图要支撑的一句话论断（如「DDRO 在高扰动场景下成本低于 SAA 且更稳定」）。
2. **面板证据链**：每个子图对应结论的哪一部分证据；不承载独立证据的面板删掉。
3. **主角面板**：多面板时确定一个 hero panel（承载核心证据、占最大面积），其余为从属，不要平均填满画布。
4. **章节归属**：注明该图服务哪一章——第三章问题描述（示意图）、第四章算法设计（流程图）、第五章实验分析（数据图），据此走下方工具路由。

图服务于科学逻辑，美观和排版都从属于把结论画清楚。

## 工具选择（按论文章节路由）

| 章节 | 图型 | 首选工具 | 要点 |
|---|---|---|---|
| 第三章 问题描述 | 示意图：网络拓扑（港口/枢纽/弧）、供应链结构、时间窗 | drawio | 节点/弧/集合用论文记号（如 G=(N,A)）；决策变量、参数、扰动用色块区分并加图例 |
| 第四章 算法设计 | 算法流程图：C&CG/Benders 迭代、启发式主循环 | drawio（矩形=步骤、菱形=判断、圆角=起止，迭代用 loop frame） | 一个流程图只讲一个算法骨架；与伪代码行号对应（如有） |
| 第五章 实验分析 | 数据图：收敛曲线、方法对比、灵敏度、Pareto 等 | Python（matplotlib + figstyle 共享样式） | 见 references/data-charts.md |
| 跨章 | 方法总览/框架图 | drawio | 同第三章要点 |

**路由命中后、动手前，先读本技能 `references/` 下的对应文件（按需加载，不必全读）：**

- **drawio 路线** → `references/drawio-workflow.md`：完整管线（手写 XML → drawio-toolkit 凸包 → CLI 矢量导出 → 视觉验收闭环）与实测防坑（MathJax 宏支持范围、px→pt 字号换算、XML 防截断与原子替换）。
- **数据图路线** → `references/data-charts.md`：版面细节、图型速查、统计要素、figstyle/save_fig 共享样式模块的加载与论文仓库自包含用法。
- **含海运连线的地理网络**（任一路线都可能遇到）→ 另读 `references/sea-routes.md`：searoute 避陆航线生成与程序化穿陆检测门禁。

drawio 示意图与流程图同样遵守硬性规范：Times 风字体、矢量导出、最终印刷尺寸下字号不低于 6 pt；与正文数学符号严格一致的需求由 drawio 内置 LaTeX（math=1 + 反引号语法）承担。

## 硬性规范（每张图必须满足）

1. **矢量 PDF**：默认导出 PDF（出版质量）；仅用户明确要求时才用 SVG（网页用途）或 PNG。
2. **字体**：Times New Roman，缺字体环境按回退链 `Times New Roman → Times → Liberation Serif → Nimbus Roman`（样式文件已内置，WSL/Linux 不再静默换成 DejaVu）。中文图（中文期刊/学位论文）用 `load_style(zh=True)`：拉丁字符与数字走 Times，中文走宋体（`SimSun → Songti SC → Noto Serif CJK SC` 按平台回退）。
3. **标签默认英文**（国际投稿），即使数据包含中文；中文论文场景用户明说后才切中文模式，中文一律宋体，不混入黑体/楷体。
4. **图例**：同一子图内 ≥2 组视觉可分的序列（靠颜色 / 线型 / marker / 填充任一维度区分）必须配图例且逐组完整；数据图路线由 `save_fig` 内置图例审计强制（缺失或不完整会报错拒绝导出），drawio 路线靠视觉验收闭环核查。

## 尺寸与字号（按最终印刷尺寸设计）

- 先问目标版面：单栏图宽约 3.5 in / 89 mm，双栏约 7.2 in / 183 mm（EJOR、TRE 等 Elsevier 期刊同此标准）；`figsize` 按此设定，不先画大图再缩。
- 最终印刷尺寸下：轴标签 7–9 pt、刻度 6–8 pt、面板字母 8–12 pt 加粗；字号不得小于 6 pt。

## 配色（色盲安全，默认执行）

- 离散类别：默认 Okabe-Ito 色板——`['#0072B2', '#D55E00', '#009E73', '#E69F00', '#56B4E9', '#CC79A7', '#000000']`。
- 连续 / 热力图：感知均匀色图 `viridis` / `plasma` / `cividis`；**禁用 jet / rainbow**。
- 发散型数据（如改善/恶化）：`RdBu_r` / `PuOr`，并以 0 为中心。
- 曲线较多时叠加冗余编码（不同 linestyle + marker），保证灰度打印下也可区分。
- 每张图克制用色：中性色 + 一个信号色系 + 一个强调色，不追求最大色彩区分度。

## 执行约定

- **脚本落盘**：生成脚本保存到项目内 `figures/scripts/<fig_name>.py`，不要只在临时目录跑一次性命令。
- **运行方式**：项目内有 pyproject.toml 用 `uv run --no-sync python figures/scripts/<fig_name>.py`；否则用 `python3`。
- **输出验证**：数据图统一走 `save_fig`（内置图例审计、非空与字体嵌入校验）；drawio 导出后须 `ls -la` 确认存在且非空，另走 `references/drawio-workflow.md` 的视觉验收闭环。两类都在回复中报告**绝对路径**，再让用户查看。
- **迭代请求**（改字号、配色、图例位置等）：先读 `figures/scripts/` 下的原脚本 → 修改 → 重跑；文件名保持不变，保证 LaTeX 中的 `\includegraphics` 引用稳定。

## 交付前检查清单

- [ ] 矢量 PDF；任何情况下不用 JPEG（有压缩伪影）
- [ ] Times New Roman（中文图：中文宋体），最终印刷尺寸下字号 ≥ 6 pt
- [ ] 字体已嵌入：pdffonts 核对 emb 全 yes（drawio 导出的 PDF 同样检查；无 pdffonts 环境用 `mutool info -F`）
- [ ] 图内无标题——标题只写在 LaTeX `\caption{}`，删除 `plt.title`
- [ ] 色盲安全配色 + 灰度可辨
- [ ] 轴标签齐全、带单位
- [ ] 误差棒 / 置信带有定义
- [ ] 多面板有 A/B/C 标签且样式一致
- [ ] 每个子图的分类标记（实心/空心、形状、颜色）都有图例逐项说明语义
- [ ] 图例审计通过（`save_fig` 导出即验证）：每个含 ≥2 组可分序列的子图都有完整图例，辅助元素已标 `_nolegend_`
- [ ] 无 3D 效果、无多余网格线和装饰
- [ ] 图的内容能独立支撑图契约中的核心结论
