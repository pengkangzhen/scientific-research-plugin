# 数据图规范（第五章实验分析，Python/matplotlib）

> 触发场景：收敛曲线、方法×单指标对比、场景×方法热力图、Pareto 前沿、双参数灵敏度、分布对比（箱线/小提琴）、网络方案可视化。
> 路由到数据图路线时先读本文件再动手；共享硬性规范（尺寸与字号、色盲安全配色、字体、图例政策）与交付前检查清单见 SKILL.md。

## 版面细节

- 去掉上、右边框（`spines['top'/'right'].set_visible(False)`），图例无边框（`frameon=False`）。
- **图例是默认要求，不是可选项**：凡靠颜色、线型、marker 形状、实心/空心、填充任一维度区分出 ≥2 组序列的子图，必须配图例逐项说明每组的语义；只有全部序列都已在数据旁就地标注（direct label）时才可免图例。轴标签、行标签（如 y 轴刻度写行名）只定位不释义，不能替代图例（实测教训：fsm Figure 4 面板 b 双行散点只有行标签、实心/空心语义无图例，被用户退回补加，且两状态合并成两 entry 仍被要求拆全四项——每个 (形状×填充) 组合一个 entry，不要合并语义）。
- **写法约定**：每条 `plot` / `scatter` / `bar` / `fill_between` 调用都带 `label=`；不进图例的辅助元素（参考线、显著性括号、误差棒帽）显式 `label="_nolegend_"`；收尾统一 `ax.legend(loc=...)`。多面板共享一套序列语义时，图例可只放主角面板一个，其余面板不重复——`save_fig` 的图例审计按全图颜色/款式匹配识别这种共享图例，不会误报。图例位置与样式跨面板一致（如统一轴内右上、顶边同高）。
- 窄面板放多列图例极易横向越界压到纵轴（相邻面板的轴）：导出前在脚本内 `fig.canvas.draw()` 后用 `legend.get_window_extent()` 与 `ax.get_window_extent()` 比对四边 slack，为负即 fail 报错（fsm fig5 实测：单行四项越界约 4pt 被用户发现；收敛方案是改 2×2 按 marker 形状分组——上圆下方对应数据行——而非缩字号）。
- 多面板：用 `GridSpec` 对齐；每个面板左上角加粗体字母 A、B、C…；各面板样式保持一致。
- 轴标签必须带单位，如 `Cost ($10^6$ USD)`、`Time (h)`。

## 数据图图型速查（第五章实验分析）

| 数据模式 | 图型 | 建议宽度 |
|---|---|---|
| 求解收敛 / optimality gap 随迭代 | 折线（必要时对数轴） | 89 mm |
| 方法 × 单指标对比 | 柱状 + 柱顶数值标注 | 89 mm |
| 场景 × 方法大表 | 热力图 | 183 mm |
| 成本–服务双目标权衡 | Pareto 散点 + 支配区底纹 | 89 mm |
| 双参数灵敏度 | 等值线 / 热力图 | 89 mm |
| 网络方案可视化 | networkx + netgraph（静态出版）/ kepler.gl（探索） | 183 mm |
| 分布对比（多场景成本） | 箱线/小提琴 + 个体散点 | 89 mm |

## 统计要素（有实验数据时）

- 误差棒注明类型（SD / SEM / 95% CI），并在图注中说明；多次运行的收敛曲线用均值 + 置信带（`fill_between`）。
- 柱状图 y 轴从零开始；离散点少时同时展示个体点（散点 + 汇统计）。

## 共享样式模块（样式唯一事实源）

样式集中在技能目录 `assets/publication.mplstyle`，加载与验证经 `scripts/figstyle.py`；图脚本禁止再复制 rcParams 块。每个图脚本开头：

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".agents/skills/figure-plotting/scripts"))
from figstyle import load_style, save_fig

load_style()            # 中文图：load_style(zh=True)
# 绘图：每条序列带 label=；辅助元素显式 label="_nolegend_"
ax.plot(iters, ddro, color="#0072B2", marker="o", markevery=10, label="DDRO")
ax.plot(iters, saa, color="#D55E00", marker="s", markevery=10, label="SAA")
ax.set_xlabel("Iteration")
ax.set_ylabel("Optimality gap (%)")
ax.legend(loc="upper right")
save_fig(fig, "fig5_convergence", outdir="figures")
```

- `save_fig` 导出前先做**图例审计**：同轴 ≥2 组视觉可分的序列无图例、或图例缺 entry（有序列没写 `label=`）都报错拒绝导出；`check_legends=False` 豁免仅限单序列或全部序列已就地标注的图。随后导出 `figures/<name>.pdf`、校验非空、核对字体全部嵌入（pdffonts emb=yes），通过后回显绝对路径。
- 论文仓库需脱离本机自包含（合作者复现/投稿）时，把 `figstyle.py` 与 `publication.mplstyle` 拷入仓库 `figures/` 目录，此后以仓库内副本为该论文的唯一事实源。
- 上面 `sys.path` 里的 `~/.agents/skills/...` 是 install.sh 软链安装的路径；经插件市场直装（没跑过 install.sh）的机器上，改为插件缓存内的对应目录（如 `~/.zcode/cli/plugins/cache/scientific-research-plugin/<版本>/skills/figure-plotting/scripts`）。
