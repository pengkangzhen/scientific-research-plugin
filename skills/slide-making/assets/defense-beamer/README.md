# 答辩 Beamer 主题（beamerthemeDefense）+ 开题答辩骨架

学术答辩 / 开题 / 组会通用 Beamer 主题：顶部深蓝横幅（可选校徽 + 校名/院名字标）+
底部章节进度条 + 目录/转场页/封面，配四个轻量内容组件。包内 `defense.tex` 是
**脱敏的开题答辩骨架**（25 页全帧型，帧型结构、组件几何为实战验证版，内容为占位文本，
占位即填写说明）。

## 文件

| 文件 | 说明 |
|------|------|
| `beamerthemeDefense.sty` | 主题文件 v2.1（横幅/进度条/目录/分节页/封面/组件，字体已全量守护；西文 Helvetica Neue、数学 Fira Math 均守护回退） |
| `defense.tex` | 开题答辩骨架（脱敏，25 页：封面/目录/5 节转场/三卡卡片/要点+警示综述/研究框架 tikz/技术路线/进度表/结束页） |
| `defense.pdf` | 上者编译预览（WSL 回退字体版：正文黑体、横幅楷体；macOS 编译出鸿蒙+行楷原版效果） |
| `campus-emblem.png` | **不入包，自备**：把自己的校徽 PNG 放文稿同目录即自动入横幅（高 5mm，反白效果最佳）；不放则横幅纯文字字标 |

## 快速开始

把 `beamerthemeDefense.sty` 放文稿同目录（校徽可选），改横幅校名/院名：

```latex
\documentclass[aspectratio=169]{beamer}
\usetheme{Defense}

% 横幅字标（默认占位，必须改成自己的）
\renewcommand{\DefenseUniv}{××大学}
\renewcommand{\DefenseUnivEn}{×× University}
\renewcommand{\DefenseCollege}{××学院}
\renewcommand{\DefenseCollegeEn}{College of ××}

% 底部进度条条目名（英文逗号分隔，与 \section 顺序一致；
% 当前节高亮、其余灰字；不配置则底部只显示页码）
\DefenseSetProgress{选题背景,文献综述,研究内容,难点,方案与计划}

% 转场页副述（英文逗号分隔，与 \section 顺序一致；不配置则无副述行）
\DefenseSetSectionDesc{第一节一句话副述,第二节,第三节,第四节,第五节}

\title{论文题目}
\subtitle{学位论文开题报告}   % 封面顶部小字
\author{答辩人：××× \and 导师：××× 教授}
\institute{××大学 · ××学院}
\date{2026 年 × 月}

\AtBeginSection[]{\frame{\sectionpage}}   % 每节自动插入过渡页（可选）

\begin{document}
\begin{coverframe}          % 封面：保留横幅，隐藏进度条与页码
  \titlepage
\end{coverframe}
\begin{frame}{目录}
  \begin{outlinelist}       % 目录条目：编号自动；副述为一句话说明
    \outlineitem{选题背景}{一句话副述。}
    \outlineitem{文献综述}{一句话副述。}
    \outlineitem{研究内容}{一句话副述。}
    \outlineitem{难点}{一句话副述。}
  \end{outlinelist}
\end{frame}
...
```

编译必须用 **xelatex**（字体经 fontspec/xeCJK 加载）：`latexmk -xelatex defense.tex`。
论文图放 `figures/` 子目录后，取消图文页中 `\includegraphics` 注释行并删除占位框。

## 内容组件（替代整页重色块的轻量组件，同页可多条堆叠）

| 环境 | 形态 | 用途 |
|------|------|------|
| `point{标题}` | 左橙竖条 + 深蓝粗标题 | 分组要点、方法脉络 |
| `warn{标题}` | 浅红底 + 左橙竖条 | 不足/风险警示 |
| `card{标题}` | 浅蓝底圆角卡片 | 多列并排（配 `columns[0.325]`×3） |
| `band` | 深蓝底白字横幅 | 结论/切入点收束 |

## 实战帧型速查（见 defense.tex）

| 帧型 | 位置 | 用法 |
|------|------|------|
| 三卡片并列 | 选题背景/研究目的/创新点 | `columns[0.325]` × 3 + `card` |
| 综述页（脉络+不足） | 文献综述Ⅰ/Ⅱ/Ⅲ | `point` 分组要点 + `warn` 不足警示 |
| 研究缺口+切入 | 研究缺口帧 | `point` 编号项 `\item[Ⅰ]` + `band` 切入点横幅 |
| 全链条框架图 | 研究框架总览 | 纯 tikz `stage` 节点链 + 虚线反馈弧 |
| 图文页 | 研究内容Ⅰ/Ⅱ | 左 `point`×2 右图占位框（真实图放 `figures/` 后换回 includegraphics） |
| 难点对策表 | 预期难点与对策 | booktabs 两列表 + `\addlinespace` |
| 技术路线五段 | 技术路线 | tikz `cnode`+`bnode` 上下贴合并排 |
| 进度表 | 工作计划 | 三列 booktabs 表 |

## 视觉规格（三色制科研配色）

全片仅用三种颜色（主色 + 强调色 + 中性灰，蓝橙互补、色盲友好）：

| 角色 | 色值 | 主题内名称 | 用途 |
|------|------|-----------|------|
| 主色 深海军蓝 | `#1F3864` | `primary` | 顶部横幅、标题字色、目录/编号、进度条、block 标题条、结论横幅 |
| 强调色 暖橙 | `#E87722` | `accent` | 标题下横线、转场页大编号与短线、关键词强调、警示提示 |
| 中性 灰 | `#595959` | `muted` | 次级文字、副述 |

| 元素 | 取值 |
|------|------|
| 顶部横幅 | 主色，高 8.3mm（`\DefenseBannerHeight` 可调） |
| 标题下横线 | 强调橙，0.7pt 全宽 |
| 底部进度条 | 主色，当前节白字高亮、其余灰字；页码在右端 |

## 字体（保留实战 deck 原版设置，自动回退）

主题字体已全量 `\IfFontExistsTF` 守护，按平台自动回退，缺字体也能编译：

| 平台 | 正文中西文 | 横幅字标中文 | 横幅字标英文 |
|------|-----------|--------------|--------------|
| macOS（原版效果） | HarmonyOS Sans SC | Xingkai SC Bold 行楷 | Zapfino 花体 |
| Windows | SimHei 或 HarmonyOS Sans SC | KaiTi 楷体（仿粗） | 当前西文字体 |
| Linux/WSL | SimHei（仿粗） | KaiTi 楷体（仿粗） | 当前西文字体 |

西文/数学不单独设字体（沿用 beamer 默认）；横幅字标中文行楷、英文 Zapfino 花体为
实战 deck 原版规格。

手动替换改 `beamerthemeDefense.sty` 中「字体」一节。**注意**：探测单词名字体（如 `Zapfino`）
缺失时 fontspec 会在日志留 kpathsea 错误，主题已用多词名 `HarmonyOS Sans SC` 做平台探测规避。

## 来源

- 主题视觉规格源自一次高校开题 pptx 复刻（2026-09，实战验证多轮视觉验收），已泛化：
  校徽不入仓库自备、校名/院名为可重设宏。
- 骨架：按实战版 `defense.tex` 逐帧脱敏而来；实战原版（真实题目/姓名/图片）留在
  Mac 侧来源项目中，**不入本仓库**。
