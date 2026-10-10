# drawio 示意图工作流（第三章拓扑 / 第四章流程 / 框架图）

> 触发场景：网络拓扑（港口/枢纽/弧）、供应链结构、时间窗示意、算法流程图（C&CG/Benders 迭代、启发式主循环）、方法总览/框架图。
> 路由到 drawio 路线时先读本文件再动手；共享硬性规范（Times 字体、矢量导出、≥6 pt 下限、色板）与交付前检查清单见 SKILL.md。

完整管线：**手写 .drawio XML → drawio-toolkit 生成凸包区域 → 桌面版 CLI 导出矢量 PDF → 渲染 PNG 视觉验收（至少两轮）→ `\includegraphics`**。导出成功不等于完成，验收通过才算。

## 1. 源文件与标签约定

- `.drawio` 与导出 PDF 同目录（论文 `figs/`）；cell 用语义化 id（`nH1`、`eG_L4`、`lgHub`），文件头写 design tokens 注释（字号阶梯、Okabe-Ito 映射、线宽分级）。
- 所有 cell `fontFamily=Times New Roman`；**数学符号一律用 drawio 内置 LaTeX 语法**：`mxGraphModel` 设 `math="1"`，标签里反引号包裹公式（`` `H_1` ``、`` `y^{\text{in}}_{1,t}` ``），可与 HTML（`<span>`/`<i>`/`<br>`）混排。纯文本里禁止 `H^hub`、`xi_n,t` 这类字面量——会按原样印出来。**从第一版就用 math=1**：不要先用 Unicode 下标（`H₁`）凑合再迁移——迁移时 toolkit 匹配串、regions.json 全部要跟着改，成本高（fsm Figure 1 实测）。
- **drawio 桌面版（30.x）MathJax 宏支持范围**（2026-09-16 逐变体实测）：`\omega \pi \lambda \eta \xi \kappa \mathcal{A} \in \Omega` 及上下标均正常；**upright 文本必须用 `\text{...}`**；`\mathrm{...}` 与 `\rm` 不被识别（宏名按字面排出，且 `in` 被解析成 ∈）；`{=}` 按字面输出括号（用 `=`）；裸多字母（`y^{in}`）被解析为变量积或 ∈。统一用 `\text{}` 包多字母词。
- **要被 drawio-toolkit 匹配的节点，value 就是含反引号的完整字符串**（`` `L_1` ``），`regions.json` 的 `nodes` 必须逐字符相同（含反引号）；只供展示的标签无此约束。

## 2. 凸包 / 服务区多边形（drawio-toolkit，零安装）

```bash
uv run --project <drawio-programmatic 路径> drawio-toolkit upsert-buffered-regions \
  --drawio <fig.drawio> --parent 1 --after <锚点cell id> --config <regions.json>
```

- 语义与坑：节点按 `parent` 属性过滤、按 **value 精确匹配**取中心；`remove_id_prefix` 幂等删除重建（`hull_` 前缀的标签 cell 也会被删，需重加）；锚点 cell 决定 z-order——插在锚点后 = 底色带之上、节点之下。
- 生成的凸包 cell 自带 value 会**居中渲染**压住内容：生成后把 value 置空，标签另加 text cell 放角落或 hull 外上方。
- `regions.json` 是凸包唯一事实源，与 `.drawio` 同目录入库；**节点坐标改动后必须重跑工具包**。
- 工具包位于 mako 仓库 `tools/drawio-programmatic/`；论文需跨机器自包含时整目录拷入论文仓库（同 figstyle 的自包含逻辑）。

## 3. 导出与字体核对

- WSL（无本地 drawio）借 Windows 桌面版：`"/mnt/c/Program Files/draw.io/draw.io.exe" -x -f pdf -crop -o "$(wslpath -w <out.pdf>)" "$(wslpath -w <in.drawio>)"`；macOS 或有本地 CLI 时直接 `drawio -x -f pdf -crop`。
- **CLI 能渲染 MathJax 数学式**（渲染为矢量路径，因此 PDF 字体清单里不会出现 MathJax_* 字体，属正常）。关键防坑：math 标签渲染后的实际宽度可超过 cell 宽度且导出不裁剪标签——内容顶到画布右缘会被**水平分成两页**。画布 `pageWidth` 要比最右内容多留 ~60px，配合 `-crop` 收回白边。
- **验证分层**：文本层（`mutool draw -F text`）能抓到完全未渲染的标签（含反引号原文），但**抓不到宏级失败**——`\mathrm` 不被识别时 MathJax 会把宏名字母排版成矢量路径，文本层同样干净。宏级正确性只能目检渲染图，且必须用开放式提问（"列出上标文字"）而非确认式提问（"是否渲染正确？"会得到顺从的"是"）。怀疑某宏有毒时，把变体写进同一文件的带行号标记行，一次导出目检对比。
- pdflatex 报 "PDF version 1.7, but at most 1.5 allowed" 无害；字体嵌入核对：无 pdffonts 的环境用 `mutool info -F <pdf>`（TimesNewRoman 子集 + 个别 Type3 矢量字形均属正常）。
- 不要试图 SendKeys 自动化 Windows 桌面版 GUI 导出：中文输入法候选框会吞键（Enter 确认的是候选而非对话框），且保存对话框焦点不可靠——CLI 渲染已够用。

## 4. 字号换算（drawio px → 印刷 pt）

`printed_pt = px × 0.75 × (版心 mm ÷ (画布 px ÷ 96 × 25.4))`。先从编译日志拿真实版心（`grep textwidth manuscript.log`）再定画布与字号阶梯。例：cas-sc 版心 468pt≈165mm、画布 1060px → 缩放 0.61 → 最小字号 **14px** 才满足 6 pt 下限。

## 5. 视觉验收闭环

- gs 渲染 PNG（`gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r150 -o out.png fig.pdf`）交视觉模型审查，跑两轮：第一轮要**具体缺陷清单**（标签压线、箭头擦边、tofu、拥挤、空白失衡）；逐条修复后，第二轮只要 **SHIP/FIX 判定**，并要求判定放在回答第一行（防回复被截断看不到结论）。
- 提防视觉模型的顺从性幻觉：诱导式提问（“是否看到反引号？”）可能得到顺着问句编造的答案。凡有客观判据的判断（math 是否渲染、页数、字体嵌入）一律用文本层/工具输出核实，视觉审查用开放式描述型提问。
- 每轮渲染的 PNG **换新文件名**，避免上传缓存命中旧图误判。
- 常用修复手法：边标签压线 → 摘成独立 text cell 垂直偏移放置；箭头贴节点边缘 → 加显式 exit/entry 锚点（菱形用顶点 `(0.5,0)/(0,0.5)/(0.5,1)/(1,0.5)`）；区域空洞 → 用实例中真实存在的弧穿过填充，不硬挪节点凑布局。

## 6. 预览与设计经验

- 给用户实时预览：`@drawio/mcp`（ZCode 已注册）的 `open_drawio_xml` 可把当前 XML 在浏览器 draw.io 编辑器打开；`search_shapes` 可查 stencil，但工业风 stencil 慎用于学术图——两篇论文（mako、fsm-stackelberg）的图均为纯几何词汇。
- 实例带真实地理坐标（港口/城市经纬度）时，**按相对方位布局 + 底色带（海域等）**远比抽象分层框图有说服力（已验证：mako `ecr_schematic`、fsm `fig_ecr_schematic`）。
- **图内不放成段文字**：注释性长句（"stage-1 sea moves / vessel call…"、"Representative arcs —…"这类）一律不进图，全部写在 LaTeX `\caption{}` 里；图内只留图形、数学符号、短标注和图例。画完自检：数一数图里超过一行的文字块，有就搬进 caption。
- 手绘感来自层级：主角节点加大加深（更粗描边、更深填充），主流程弧加粗，注记一律细线斜体；全员同权重 = 自动生成感。
- **程序化改 XML 的防截断**：`ET.tree.write()` 先清空文件再序列化，任何属性值忘了 `str()`（如 float 的 `-0.5`）都会留下截断损坏且无备份。改 .drawio 一律先写临时文件再 `os.replace()` 原子替换；损坏后若节点几何未变，删掉生成性 cell（凸包）按补丁历史重建、toolkit 重跑即可恢复。
- **新建 cell 必须带 `as="geometry"`**：`<mxGeometry>` 缺 `as` 属性时 XML 仍良构、ET 不报错，但 drawio 导出时该 cell 几何失效，内容 bbox 被算到远处 → PDF 平铺成 N 页（表现为"只有最后一页有内容"）。症状性修法：遍历所有 mxGeometry 补 `as="geometry"`。另：浮动边（sourcePoint/targetPoint 式）加 Array 路径点同样会触发 bbox 爆炸，曲线/折线要用 `shape=mxgraph.basic.polygon` + `polyline=1` 的开放折线替代。
