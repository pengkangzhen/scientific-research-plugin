#!/usr/bin/env python3
"""关键词判色原型：输入一个词，输出该词在五色高亮体系里应标的颜色。

  🔴 红 #ff6666 研究问题 | 🟡 黄 #ffd400 数学模型 | 🟢 绿 #5fb236 求解方法
  🔵 蓝 #2ea8e5 案例研究 | 🟣 紫 #a28ae5 实验结果

为什么不是一层三分类：meta/generic/method（check_terms_semantic.py）回答
"该不该高亮"，输出空间里没有颜色信息；本脚本在其上加判色层，三级串联：

  1. 静态层（词表即事实源，命中免嵌入）：词在 field_generic / 元词 / 泛词
     表里 → 无颜色；在某色种子簇里 → 该色；
  2. 过滤层（未见词走语义）：max(元词,泛词)质心 ≥ 0.60 且高于最佳色簇
     → 无颜色（噪音）；
  3. 判色层：最高色簇 ≥ COLOR_SIM 判色，否则 ⚪ 灰区（人工裁决）。

已知边界（原型如实暴露，不掩盖）：
  - 案例专名（AEU6 类）语义上互不成簇，未见专名预期落灰区；
    正式管线里蓝色应优先来自笔记「案例研究」章节的结构信号（词的出处）。
  - 裸词天然歧义（uncertainty 挂红还是黄？），红/黄两簇语义相邻，
    低置信词应落灰区交人工，这正是灰区存在的意义。

用法：
    uv run classify_color.py --words "two-stage stochastic programming,network vulnerability,supply chain"
"""
# /// script
# requires-python = ">=3.10"
# dependencies = ["fastembed"]
# ///

import argparse
import sys

from check_terms_semantic import load_filter_seeds
from lexicon_embed import cos, embed_one, get_centroids, load_model, load_seed_sections

NOISE_SIM = 0.60     # 噪音线，与过滤层 RED_SIM 同源
COLOR_SIM = 0.45     # 判色线：五簇比三簇更专指，相似度整体偏低（测试批校准）

# 展示顺序 = SKILL.md 五色表顺序；method 色复用 method_seeds，不另设簇
COLOR_CLUSTERS = [
    ("rq", "🔴红 #ff6666", "rq_seeds"),
    ("model", "🟡黄 #ffd400", "model_seeds"),
    ("method", "🟢绿 #5fb236", "method_seeds"),
    ("case", "🔵蓝 #2ea8e5", "case_seeds"),
    ("result", "🟣紫 #a28ae5", "result_seeds"),
]
NO_COLOR_SECTIONS = ("field_generic", "meta_seeds", "generic_seeds")


def load_all_seeds():
    """静态无色表 + 过滤三簇（含兜底）+ 判色五簇（yaml 是唯一事实源，缺簇报错）。"""
    seeds = load_filter_seeds()
    static = load_seed_sections(NO_COLOR_SECTIONS)
    for name, words in static.items():
        seeds[name] = words
    color = load_seed_sections([sec for _, _, sec in COLOR_CLUSTERS])
    for _, _, sec in COLOR_CLUSTERS:
        if not color[sec]:
            sys.exit(f"错误：term-lexicon.yaml 缺 {sec}（判色簇无兜底，请在 yaml 中补种子）")
    seeds.update(color)
    return seeds


def classify_one(model, centroids, seeds, term):
    """三级判定；返回 (判定串, 各相似度 dict 或 None=静态命中免嵌入)。"""
    low = term.lower()
    no_color = {w.lower() for sec in NO_COLOR_SECTIONS for w in seeds[sec]}
    if low in no_color:
        return "无颜色（静态命中：元词/泛词表）", None
    for name, label, sec in COLOR_CLUSTERS:
        if low in {w.lower() for w in seeds[sec]}:
            return f"{label}（{name} 簇，静态命中）", None

    vec = embed_one(model, term)
    sims = {k: cos(vec, c) for k, c in centroids.items()}
    bad = max(sims["meta"], sims["generic"])
    bad_name = "元词" if sims["meta"] >= sims["generic"] else "泛词"
    color_name, color_sim = max(
        ((name, sims[sec]) for name, _, sec in COLOR_CLUSTERS),
        key=lambda kv: kv[1])
    label = dict((name, lab) for name, lab, _ in COLOR_CLUSTERS)[color_name]

    if bad >= NOISE_SIM and color_sim < bad:
        verdict = f"无颜色（{bad_name}噪音）"
    elif color_sim >= COLOR_SIM:
        verdict = f"{label}（{color_name} 簇）"
    else:
        verdict = f"⚪ 灰区（人工；最近 {label} {color_name} 簇）"
    return verdict, sims


def main():
    ap = argparse.ArgumentParser(description="关键词五簇判色原型（静态 + 过滤 + 判色三级）")
    ap.add_argument("--words", required=True, help="逗号分隔的候选词")
    args = ap.parse_args()
    terms = [w.strip() for w in args.words.split(",") if w.strip()]
    if not terms:
        sys.exit("错误：没有待判词")

    model = load_model()
    seeds = load_all_seeds()
    centroids = get_centroids(model, seeds)

    header = "| 词 | 判定 | " + " | ".join(lab for _, lab, _ in COLOR_CLUSTERS) + " | 元词 | 泛词 |"
    print(header)
    print("|---|---|" + "---|" * 7)
    n_color = n_none = n_gray = 0
    for term in terms:
        verdict, sims = classify_one(model, centroids, seeds, term)
        if "无颜色" in verdict:
            n_none += 1
        elif "灰区" in verdict:
            n_gray += 1
        else:
            n_color += 1
        if sims is None:
            row = " | ".join("—" for _ in COLOR_CLUSTERS) + " | — | —"
        else:
            row = " | ".join(f"{sims[sec]:.3f}" for _, _, sec in COLOR_CLUSTERS) \
                + f" | {sims['meta']:.3f} | {sims['generic']:.3f}"
        print(f"| {term} | {verdict} | {row} |")

    print()
    print(f"- 判色 {n_color}，无颜色 {n_none}，灰区 {n_gray}"
          f"（阈值 噪音≥{NOISE_SIM}、判色≥{COLOR_SIM}；"
          f"改 term-lexicon.yaml 后自动重算质心）")
    print("- 静态命中免嵌入；案例专名（AEU6 类）语义不成簇，未见专名预期落灰区，"
          "正式管线蓝色应来自笔记章节出处")


if __name__ == "__main__":
    main()
