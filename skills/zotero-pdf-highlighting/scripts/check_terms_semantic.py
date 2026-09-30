#!/usr/bin/env python3
"""候选关键词语义层（zotero-pdf-highlighting 管线 Step 4.5b，算法二）。

用多语嵌入（fastembed + paraphrase-multilingual-MiniLM，中英通吃）把候选词投向
term-lexicon.yaml 里三簇种子的质心，按语义相似度判级——不依赖词表穷举，
没见过的词（maritime logistics、分层优化）也能判。

判定规则（原型 26 词校准）：
  - max(元词簇, 泛词簇) ≥ 0.60 且高出方法簇 0.02 以上 → 红旗（元词/泛词）
  - 方法簇 ≥ 0.55 → 术语（方法名）
  - max(坏簇) ≥ 0.55 → 灰区（边界词，人工过三测试）
  - 其余 → 术语（专名/低相似，绿灯）

只建议不拦截；与 check_terms.py 的静态信号互补，两表都跑取并集。
嵌入/质心/缓存机制见共享模块 lexicon_embed.py（判色原型 classify_color.py 同源）。

模型已缓存到本地后可离线运行；首次下载需代理（WSL 实测）：
  HTTPS_PROXY=http://100.122.3.64:7890 uv run check_terms_semantic.py --words "supply chain"
种子改动后自动重算质心缓存（~/.cache/zotero-pdf-highlighting/）。

用法：
    uv run check_terms_semantic.py --plan /tmp/plan.json
    uv run check_terms_semantic.py --words "case study,supply chain,two-stage stochastic programming"
"""
# /// script
# requires-python = ">=3.10"
# dependencies = ["fastembed"]
# ///

import argparse
import json
import sys

from lexicon_embed import MODEL, cos, embed_one, get_centroids, load_model, load_seed_sections

RED_SIM, RED_MARGIN, METHOD_SIM, GRAY_SIM = 0.60, 0.02, 0.55, 0.55

FALLBACK_SEEDS = {  # term-lexicon.yaml 缺失各簇时的兜底（与 yaml 同步维护）
    "meta": ["case study", "numerical example", "experiment", "instance", "test problem",
             "problem statement", "model formulation", "computational results", "CPU time",
             "solution quality", "案例研究", "数值实验", "运行时间", "计算时间"],
    "generic": ["supply chain", "logistics", "liner shipping", "transportation",
                "machine learning", "deep learning", "optimization", "container",
                "供应链", "物流", "机器学习", "集装箱", "优化"],
    "method": ["Benders decomposition", "two-stage stochastic programming", "linear programming",
               "tabu search", "genetic algorithm", "DQN", "LSTM-SVR", "Markov decision process",
               "dynamic programming", "组合预测", "混合整数规划", "蒙特卡洛模拟"],
}


def load_filter_seeds():
    """三簇过滤种子：yaml 的 *_seeds 段去后缀，缺失/空段落回兜底表。"""
    raw = load_seed_sections(("meta_seeds", "generic_seeds", "method_seeds"))
    seeds = {name.removesuffix("_seeds"): words for name, words in raw.items()}
    for key, default in FALLBACK_SEEDS.items():
        if not seeds.get(key):
            seeds[key] = default
    return seeds


def main():
    ap = argparse.ArgumentParser(description="候选关键词语义层（嵌入种子质心，只建议不拦截）")
    ap.add_argument("--plan", help="plan JSON（按 spans 逐词检查）")
    ap.add_argument("--words", help="逗号分隔的候选词")
    args = ap.parse_args()
    if not args.plan and not args.words:
        sys.exit("错误：需要 --plan 或 --words 之一")

    spans = []
    if args.plan:
        plan = json.load(open(args.plan, encoding="utf-8"))
        spans = plan.get("spans") or []
    else:
        spans = [{"category": "", "text": w.strip()} for w in args.words.split(",") if w.strip()]
    terms = [s["text"].strip() for s in spans if s.get("text", "").strip()]
    if not terms:
        sys.exit("错误：没有待检词")

    model = load_model()
    seeds = load_filter_seeds()
    centroids = get_centroids(model, seeds)

    print("| 词 | 类别 | 元词簇 | 泛词簇 | 方法簇 | 建议 |")
    print("|---|---|---|---|---|---|")
    n_red = n_gray = 0
    for span in spans:
        term = span.get("text", "").strip()
        if not term:
            continue
        vec = embed_one(model, term)
        sims = {k: cos(vec, c) for k, c in centroids.items()}
        bad = max(sims["meta"], sims["generic"])
        bad_name = "元词" if sims["meta"] >= sims["generic"] else "泛词"
        if bad >= RED_SIM and bad - sims["method"] >= RED_MARGIN:
            verdict, n_red = f"红旗：{bad_name}簇语义相近", n_red + 1
        elif sims["method"] >= METHOD_SIM:
            verdict = "术语（方法名）"
        elif bad >= GRAY_SIM:
            verdict, n_gray = "灰区：边界词，过三测试", n_gray + 1
        else:
            verdict = "术语（专名/低相似）"
        print(f"| {term} | {span.get('category', '')} | {sims['meta']:.3f} | "
              f"{sims['generic']:.3f} | {sims['method']:.3f} | {verdict} |")

    print()
    print(f"- 候选 {len(spans)} 个：红旗 {n_red}，灰区 {n_gray}（模型 {MODEL.split('/')[-1]}，"
          f"种子 {sum(len(v) for v in seeds.values())} 个，改 term-lexicon.yaml 后自动重算质心）")
    print("- 语义层与 check_terms.py 静态信号互补：两表都跑，红旗取并集，最终按 SKILL.md 三测试裁决")


if __name__ == "__main__":
    main()
