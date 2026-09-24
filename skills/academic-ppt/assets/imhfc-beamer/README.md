# IMHFC 会议 Beamer 资产包（imhfc-beamer）

IMHFC 2026（Istanbul, 2026-09-03/05）官方会议模板的提取成品，IMHFC 系会议再次投稿时直接复用；
也是 SKILL §2.1「官方 pptx 提取复用」路线的参照实现。

## 文件

| 文件 | 说明 |
|------|------|
| `template-original.pptx` | 会议官方模板原件（§6.1 交付包装的贴回底版） |
| `figs/beamer_bg/bg_cover.jpg` | 封面 / 转场页整页背景 |
| `figs/beamer_bg/bg_content.jpg` | 内容页整页背景（底部 9.76% ≈ 8.8mm 为品牌条带） |
| `figs/beamer_bg/bg_closing.jpg` | 封底整页背景 |

> 三张背景按 SKILL §2.1 从官方 pptx 解压 `ppt/media/` 提取；logo 与真页脚在 slide master
> 里、不在背景图中，内容页背景底部的淡色条带是真实页脚区，**勿删**（SKILL §7）。

## 用法 A：Beamer 官方模板模式

把 `figs/` 整目录复制到幻灯片工程根目录（与 `presentation.tex` 同级），以
`assets/beamer-deck-template.tex` 为底稿，改三处接线（色板不用动——模板默认五色即 IMHFC 色）：

```latex
\graphicspath{{figs/}}   % 取消注释

\newcommand{\BgCover}{\includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio=false]{beamer_bg/bg_cover}}
\newcommand{\BgContent}{\includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio=false]{beamer_bg/bg_content}}
\newcommand{\BgClosing}{\includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio=false]{beamer_bg/bg_closing}}
```

条带避让已在模板 footline 预装好（ht+dp = 11mm，正文止于条带上方 ~2mm，页码落在条带内），
无需再调。转场页沿用内容背景即可；封面照片亮度高时标题用 navy（模板默认已如此）。

## 用法 B：pptx 交付包装（SKILL §6.1）

Beamer PDF 定稿后按 §6.1 贴回：`pdftoppm -png -r 300` 出图 → python-pptx 以
`template-original.pptx` 为底版（先备份），删示例页、选空白版式、逐页满幅贴图。
⚠️ 目录里有 `~$xxx.pptx` 锁文件 = PowerPoint 正开着，不要写入。

## 视觉规格（模板五色的 IMHFC 出处）

| 角色 | 色值 | 用途 |
|------|------|------|
| 主色 navy | `#0E2841` | 标题、正文、结论块底 |
| 强调 orange | `#E97132` | 编号、细线、眉注、关键词点缀 |
| 辅助 teal | `#156082` | 分组小标题、次级结构元素 |
| 弱化灰 | `#5A6B7B` | 图例、脚注、副述 |
| 浅底 | `#F2F6F9` | 卡片填充 |

实例（填好的完整参照）：WSL `~/projects/research/imhfc-ecr-mcnf/presentation/`
（presentation_beamer.tex / presentation_beamer.pdf / presentation_speech.md）。
