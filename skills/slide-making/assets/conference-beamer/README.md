# 会议汇报 Beamer 接线包（conference-beamer）

「官方会议模板提取复用」路线的接线模板与参数表（SKILL §2.1 的参照实现）。
会议品牌资产（背景图、官方 pptx）因属会议方版权物**不入仓库**，按下方流程从
你收到的会议官方模板自备；接线方式、条带避让参数、封底印字避坑均已固化在本包
与包内 `conference.tex`（学术会议 Beamer 模板，字体已按实战 deck 设置：西文 Helvetica Neue / 数学 Fira Math，均守护回退）中。

## 文件

| 文件 | 说明 |
|------|------|
| `conference.tex` | 学术会议 Beamer 模板（自建模式零资产直接可编译；官方模板模式按下方接线） |
| `conference.pdf` | 上者编译预览（18 页全帧型） |
| `figs/beamer_bg/` | 会议背景图投放点：放入提取的三张整页背景 `bg_cover.jpg` / `bg_content.jpg` / `bg_closing.jpg` |
| `README.md` | 本文件：提取流程、接线、参数表 |

## 第一步：从官方 pptx 提取三张背景

pptx 即 zip：解压取 `ppt/media/` 内整页背景图，一般三张（封面 bg_cover / 内容页
bg_content / 封底 bg_closing），放入 `figs/beamer_bg/`。

- ⚠️ logo 和真页脚在 slide master 里，**不在**背景图片里；提取图可能带无意义淡色伪影条带。
- ⚠️ 内容页背景底部的品牌条带是真实页脚区，**勿删**（删背景属协作红线）。

## 第二步：接线（配包内 conference.tex）

把 `figs/` 整目录复制到幻灯片工程根目录（与 `presentation.tex` 同级），三行接线：

```latex
\graphicspath{{figs/}}   % 取消注释

\newcommand{\BgCover}{\includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio=false]{beamer_bg/bg_cover}}
\newcommand{\BgContent}{\includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio=false]{beamer_bg/bg_content}}
\newcommand{\BgClosing}{\includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio=false]{beamer_bg/bg_closing}}
```

色板从模板主题色提取进 `conference.tex` 的【色板】五处 `\definecolor`。
条带避让已在模板 footline 预装好（底部条带按百分比换算：Beamer 16:9 纸高仅 9cm，
9.76% 条带 ≈ 8.8mm；footline ht+dp = 11mm，正文止于条带上方 ~2mm，页码落在条带内），
条带高度不同时按同法换算重设，勿拿 pptx 绝对尺寸直接预留。

## 封底避坑

官方封底背景通常**自带致谢字样**（曾实测某会议 bg_closing 印有 "Thank you for your
attention!"，占页高 30–46%），叠字必乱码。`conference.tex` 的封底帧已做
模式自适应：官方背景模式只留单行联系信息；换新会议背景时按其留白区重调 yshift
（方法：mutool 把背景图转 PPM 后逐行像素实测空档），勿信默认居中。

## pptx 交付包装（SKILL §6.1）

Beamer PDF 定稿后贴回官方 pptx：`pdftoppm -png -r 300` 出图 → 运行技能根目录的
`scripts/package_pptx.py`（锁文件检查 → 自动备份原模板 → 删示例页 → 空白版式 →
满幅贴图 → 重开验证，出图目录混入杂图会因尺寸不齐被拒）。
⚠️ 目录里有 `~$xxx.pptx` 锁文件 = PowerPoint 正开着，脚本会拒绝写入。

## 来源

- 模板源自一次学术会议报告实战（2026-08，官方 pptx 模板提取复用路线，多轮视觉验收），
  已泛化：背景图等会议品牌资产不入仓库自备、色值为可重设宏。
- 骨架：按实战版 `conference.tex` 逐帧脱敏而来；实战原版（真实题目/内容/图片）留在
  来源项目中，**不入本仓库**。
