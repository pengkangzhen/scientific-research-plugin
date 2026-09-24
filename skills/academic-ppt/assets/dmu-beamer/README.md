# DMU Beamer 主题（beamerthemeDMU）+ 开题答辩骨架

由 `docs/开题报告/开题报告.pptx`（2026-09 版）复刻的 LaTeX Beamer 主题，用于开题报告、答辩与组会演示。
包内 `defense.tex` 是**脱敏的开题答辩骨架**（25 页全帧型，与实战 deck 帧型结构、组件几何完全一致，
内容为占位文本，占位即填写说明）；实战原版（真实题目、姓名、图片）留在 Mac 侧项目，不入仓库。

## 文件

| 文件 | 说明 |
|------|------|
| `beamerthemeDMU.sty` | 主题文件 v1.1（颜色/横幅/标题/进度条/目录/分节页/封面，字体已全量守护） |
| `dmu-emblem.png` | 圆形校徽（源：PPTX 渲染图裁剪，透明底） |
| `defense.tex` | 开题答辩骨架（脱敏，25 页：封面/目录/5 节转场/dmucard 三卡/dmupoint+dmualert 综述/研究框架 tikz/技术路线/进度表/结束页；图文页含占位框与引用注释行） |
| `defense.pdf` | 上者编译预览（WSL 回退字体版：正文黑体、横幅楷体；macOS 编译出鸿蒙+行楷原版效果） |

> 横幅上的校名、学院名（含中英文）为**文字排版**（中文行楷 + 英文 Zapfino 花体），
> 竖线位置由 tikz calc 锚定字标实际宽度，改文案无需重算坐标。

## 用法

把 `beamerthemeDMU.sty` 与 `dmu-emblem.png` 放在文稿同目录，然后：

```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{DMU}

% 底部进度条条目名（英文逗号分隔，与 \section 顺序一致；
% 当前节深蓝高亮、其余灰色；不配置则底部只显示页码）
\dmusetprogress{选题背景,文献综述,研究内容,难点}

% 转场页副述（英文逗号分隔，与 \section 顺序一致；不配置则无副述行）
\dmusetsectiondesc{第一节一句话副述,第二节,第三节,第四节}

\title{论文题目}
\subtitle{博士学位论文开题报告}   % 封面顶部小字
\author{答辩人：××× \and 导师：××× 教授}
\institute{大连海事大学 · 交通运输工程学院}
\date{2026 年 9 月}

\AtBeginSection[]{\frame{\sectionpage}}   % 每节自动插入过渡页（可选）

\begin{document}
\begin{coverframe}          % 封面：保留横幅，隐藏进度条与页码
  \titlepage
\end{coverframe}
\begin{frame}{目录}
  \begin{dmuoutline}        % 目录条目：编号自动；副述为一句话说明
    \dmuoutlineitem{选题背景}{一句话副述。}
    \dmuoutlineitem{文献综述}{一句话副述。}
    \dmuoutlineitem{研究内容}{一句话副述。}
    \dmuoutlineitem{难点}{一句话副述。}
  \end{dmuoutline}
\end{frame}
...
```

编译必须用 **xelatex**（字体经 fontspec/xeCJK 加载）：`latexmk -xelatex defense.tex`。
论文图放 `figures/` 子目录后，取消图文页中 `\includegraphics` 注释行并删除占位框。

## 实战帧型速查（见 defense.tex）

| 帧型 | 位置 | 用法 |
|------|------|------|
| 三卡片并列 | 选题背景/研究目的/创新点 | `columns[0.325]` × 3 + `dmucard` |
| 综述页（脉络+不足） | 文献综述Ⅰ/Ⅱ/Ⅲ | `dmupoint` 分组要点 + `dmualert` 不足警示 |
| 研究缺口+切入 | 研究缺口帧 | `dmupoint` 编号项 `\item[Ⅰ]` + `dmuband` 切入点横幅 |
| 全链条框架图 | 研究框架总览 | 纯 tikz `stage` 节点链 + 虚线反馈弧 |
| 图文页 | 研究内容Ⅰ/Ⅱ | 左 `dmupoint`×2 右图占位框（真实图放 `figures/` 后换回注释中的 includegraphics 行） |
| 难点对策表 | 预期难点与对策 | booktabs 两列表 + `\addlinespace` |
| 技术路线五段 | 技术路线 | tikz `dmucap`+`dmubody` 上下贴合并排 |
| 进度表 | 工作计划 | 三列 booktabs 表 |

## 视觉规格（三色制科研配色）

全片仅用三种颜色（主色 + 强调色 + 中性灰，蓝橙互补、色盲友好）：

| 角色 | 色值 | 用途 |
|------|------|------|
| 主色 深海军蓝 | `#1F3864` | 顶部横幅、标题字色、目录/编号、进度条、block 标题条、结论横幅 |
| 强调色 暖橙 | `#E87722` | 标题下横线、转场页大编号与短线、关键词强调、不足/警示提示 |
| 中性 灰 | `#595959` | 次级文字、副述 |

| 元素 | 取值 |
|------|------|
| 顶部横幅 | 主色 `#1F3864`，高 8.3mm |
| 标题下横线 | 强调橙 `#E87722`，0.7pt 全宽 |
| 底部进度条 | 主色 `#1F3864`，当前节白字高亮、其余灰字；页码在右端 |

可调宏：`\dmuuniv{...}`/`\dmuuniven{...}`（横幅校名中/英文）、`\dmucollege{...}`/`\dmucollegeen{...}`（横幅学院名中/英文）、`\dmubannerheight`（横幅高度长度）。

## 字体（v1.1 起自动回退）

主题字体已全量 `\IfFontExistsTF` 守护，按平台自动回退，缺字体也能编译：

| 平台 | 正文中西文 | 横幅字标中文 | 横幅字标英文 |
|------|-----------|--------------|--------------|
| macOS（原版效果） | HarmonyOS Sans SC | Xingkai SC Bold 行楷 | Zapfino 花体 |
| Windows | SimHei 或 HarmonyOS Sans SC | KaiTi 楷体（仿粗） | 当前西文字体 |
| Linux/WSL | SimHei（仿粗） | KaiTi 楷体（仿粗） | 当前西文字体 |

手动替换仍改 `beamerthemeDMU.sty` 中「字体」一节。**注意**：探测单词名字体（如 `Zapfino`）
缺失时 fontspec 会在日志留 kpathsea 错误，主题已用多词名 `HarmonyOS Sans SC` 做平台探测规避。

## 来源

- 主题：Mac `~/Documents/code/sc_resilience_geo/docs/开题报告/beamer-dmu/`（sty、校徽同源）。
- 骨架：按同目录实战版 `defense.tex` 逐帧脱敏而来（题目/姓名/研究内容/图片/经费 → 占位符）；
  实战原版及其图片（`docs/开题报告/figures/`）留在 Mac 侧，**不入本仓库**。
