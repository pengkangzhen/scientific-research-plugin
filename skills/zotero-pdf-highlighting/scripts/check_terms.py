#!/usr/bin/env python3
"""候选关键词信号层（zotero-pdf-highlighting 管线 Step 4.5）。

在写 plan 之前跑：识别不适合高亮的词——结构性元词（case study）、领域泛词
（supply chain，说的是领域名而非这篇论文）、高频泛词（optimization）——
并把方法专名（two-stage stochastic programming）标为绿灯。
**只建议、不拦截**，边界词的最终裁决按 SKILL.md 三测试（换文/笔记/专指）由 agent 做。

四信号：
  1. 结构/仪表黑名单（子串匹配，中英）：case study、CPU time…
  2. 领域泛词表（整词匹配，中英，可在 references/term-lexicon.yaml 扩充）：supply chain、机器学习…
  3. 库内 DF：词出现在 Zotero 库多少篇的标题/摘要/标签里；≥15% 视为泛词（数据自适应兜底）
  4. 方法构词模式：`修饰语 + 方法通名`（two-stage stochastic **programming**、组合**预测**）

数据源：zotero.sqlite（默认从 category-colors.yaml 的 data_dir 解析）。
每次运行复制到独立临时快照并以只读方式打开——只读连接不 checkpoint、不建 wal，
多进程并发也不会互相踩（tmpfs 上共享可写快照曾引发页损坏/OOM）。

用法：
    uv run check_terms.py --plan /tmp/plan.json
    uv run check_terms.py --words "case study,supply chain,two-stage stochastic programming" [--item-key G9U84WSY]
"""
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(SCRIPT_DIR, "..", "references", "category-colors.yaml")
LEXICON_PATH = os.path.join(SCRIPT_DIR, "..", "references", "term-lexicon.yaml")

# 结构性元词（章节/实验组织）与测量仪表词：子串匹配。命中=红旗；
# 唯一例外：论文贡献本身就是该词（专讲加速的论文，runtime 就是发现对象）
BLACKLIST = [
    "case study", "case studies", "numerical example", "numerical experiment",
    "experiment", "experimental result", "computational result", "instance",
    "test problem", "problem statement", "model formulation", "introduction",
    "literature review", "conclusion", "sensitivity analysis", "performance comparison",
    "cpu time", "runtime", "running time", "computation time", "computational time",
    "solution quality", "training time", "elapsed time",
    "案例研究", "案例分析", "数值实验", "数值算例", "仿真实验", "实验分析",
    "算例分析", "问题提出", "问题描述", "模型构建", "文献综述", "总结与展望",
    "绪论", "引言", "结论", "运行时间", "计算时间", "求解时间",
]

# 领域泛词（整词匹配）：说的是领域/行业名，不是这篇论文做了什么。
# 与方法通名组合后不算泛词（stochastic programming ≠ programming）。
FIELD_GENERIC = [
    "supply chain", "supply chain management", "logistics", "liner shipping",
    "maritime transport", "transportation", "operations research",
    "machine learning", "deep learning", "artificial intelligence",
    "optimization", "heuristic", "network design", "container",
    "供应链", "物流", "海运", "交通运输", "运筹学", "机器学习", "深度学习",
    "人工智能", "优化", "启发式", "集装箱", "铁路运输",
]

# 方法通名：出现在词尾且前面带修饰语 → 方法专名（绿灯）
METHOD_HEADS = [
    "programming", "optimization", "decomposition", "heuristic", "algorithm",
    "regression", "learning", "simulation", "forecasting",
    "规划", "分解", "启发式", "算法", "回归", "学习", "仿真", "预测",
]

DF_GENERIC = 0.15  # 库内 DF ≥ 15% → 泛词红旗（校准数据：optimization 30%/container 27%/network 20%，其余全部 ≤9%）
DF_GRAY = 0.08     # 8%–15% → 灰区


def load_data_dir(config_path):
    if not os.path.exists(config_path):
        return None
    with open(config_path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"\s*data_dir:\s*(\S+)", line)
            if m:
                return os.path.expanduser(m.group(1))
    return None


def load_lexicon():
    """term-lexicon.yaml 的 field_generic 列表可扩充内置词表（简单 '- 词' 行解析）。"""
    extra = []
    if os.path.exists(LEXICON_PATH):
        with open(LEXICON_PATH, encoding="utf-8") as f:
            in_list = False
            for line in f:
                if re.match(r"^\s*field_generic\s*:", line):
                    in_list = True
                    continue
                if in_list:
                    m = re.match(r"^\s*-\s*(.+?)\s*$", line)
                    if m:
                        extra.append(m.group(1))
                    elif line.strip() and not line.startswith((" ", "\t", "-")):
                        break
    return extra


def build_corpus(db_path, attempts=5):
    """独立临时快照 + 只读连接 → {itemID: 小写化标题+摘要+标签}、{itemID: 标题+标签}。

    /mnt/c（drvfs）上拷贝 80MB 级库偶发撕裂：quick_check 仍 ok 但 join 行数爆炸
    （实测 3 千行变 2900 万行）。因此拷贝后过完整性门禁——全量 integrity_check +
    行数合理性校验，失败重拷；门禁不过的副本绝不进入语料构建。
    """
    join_sql = """SELECT COUNT(*) FROM itemData id
        JOIN fields f ON f.fieldID = id.fieldID
        JOIN itemDataValues idv ON id.valueID = id.valueID
        WHERE f.fieldName IN ('title', 'abstractNote')"""
    for _ in range(attempts):
        snap = tempfile.mktemp(suffix=".db", prefix="zmeta_")
        shutil.copy(db_path, snap)
        con = sqlite3.connect(f"file:{snap}?mode=ro", uri=True)
        cur = con.cursor()
        sane = cur.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        if sane:
            n_items = cur.execute("SELECT COUNT(*) FROM items").fetchone()[0]
            n_join = cur.execute(join_sql).fetchone()[0]
            sane = n_join <= max(10000, 5 * n_items)
        if not sane:
            # 源库索引可能损坏（quick_check 查不出，坏索引会让 JOIN 爆到千万行）：
            # 在副本上 REINDEX 重建，再重新过门禁；源库不被改动。
            con.close()
            fix = sqlite3.connect(snap)
            try:
                fix.execute("REINDEX")
                fix.commit()
            finally:
                fix.close()
            con = sqlite3.connect(f"file:{snap}?mode=ro", uri=True)
            cur = con.cursor()
            sane = cur.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            if sane:
                n_items = cur.execute("SELECT COUNT(*) FROM items").fetchone()[0]
                n_join = cur.execute(join_sql).fetchone()[0]
                sane = n_join <= max(10000, 5 * n_items)
        if sane:
            break
        con.close()
        os.remove(snap)
    else:
        return {}, {}, {}
    child_ids = {r[0] for r in cur.execute(
        "SELECT itemID FROM itemAttachments UNION SELECT itemID FROM itemNotes")}
    blob, own = {}, {}
    for item_id, field, value in cur.execute("""
            SELECT id.itemID, f.fieldName, idv.value FROM itemData id
            JOIN fields f ON f.fieldID = id.fieldID
            JOIN itemDataValues idv ON id.valueID = id.valueID
            WHERE f.fieldName IN ('title', 'abstractNote')"""):
        if item_id in child_ids:
            continue
        blob.setdefault(item_id, []).append((value or "").lower())
        if field == "title":
            own.setdefault(item_id, []).append((value or "").lower())
    for item_id, name in cur.execute(
            "SELECT it.itemID, t.name FROM itemTags it JOIN tags t ON t.tagID = it.tagID"):
        if item_id in child_ids:
            continue
        blob.setdefault(item_id, []).append((name or "").lower())
        own.setdefault(item_id, []).append((name or "").lower())
    item_key_id = dict(cur.execute("SELECT key, itemID FROM items"))
    con.close()
    os.remove(snap)
    corpus = {i: " \n ".join(p) for i, p in blob.items()}
    own_corpus = {i: " \n ".join(p) for i, p in own.items()}
    return corpus, own_corpus, item_key_id


def is_method_term(term):
    """`修饰语 + 方法通名`（词尾）判定：two-stage stochastic programming ✓、programming ✗。"""
    for head in METHOD_HEADS:
        if term.endswith(head) and len(term) > len(head) + 1:
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description="候选关键词元词/泛词/术语信号层（只建议不拦截）")
    ap.add_argument("--plan", help="plan JSON（按 spans 逐词检查，带类别与本篇命中）")
    ap.add_argument("--words", help="逗号分隔的候选词（无 plan 时的快速检查）")
    ap.add_argument("--item-key", help="本篇 Zotero 条目 key（--words 模式下启用本篇命中信号）")
    ap.add_argument("--db", help="zotero.sqlite 路径；缺省从 category-colors.yaml 的 data_dir 解析")
    ap.add_argument("--config", default=DEFAULT_CONFIG)
    args = ap.parse_args()

    if not args.plan and not args.words:
        sys.exit("错误：需要 --plan 或 --words 之一")

    spans, item_key = [], args.item_key
    if args.plan:
        with open(args.plan, encoding="utf-8") as f:
            plan = json.load(f)
        spans = plan.get("spans") or []
        item_key = plan.get("item_key") or item_key
    else:
        spans = [{"category": "", "text": w.strip()} for w in args.words.split(",") if w.strip()]

    field_generic = set(FIELD_GENERIC) | set(load_lexicon())
    db = args.db
    if not db:
        data_dir = load_data_dir(args.config)
        db = os.path.join(data_dir, "zotero.sqlite") if data_dir else None
    corpus, own_corpus, keymap = {}, {}, {}
    if db and os.path.exists(db):
        corpus, own_corpus, keymap = build_corpus(db)
    n_items = len(corpus)
    if not n_items:
        print(f"（未找到可用的 zotero.sqlite（{db}），库内 DF 信号跳过）", file=sys.stderr)
    own_id = keymap.get(item_key) if item_key else None

    print("| 词 | 类别 | 库内DF | 黑名单 | 泛词表 | 方法模式 | 本篇标题/标签 | 建议 |")
    print("|---|---|---|---|---|---|---|---|")
    n_red = n_gray = 0
    for span in spans:
        term = span.get("text", "").strip()
        if not term:
            continue
        low = term.lower()
        df = sum(1 for b in corpus.values() if low in b) if n_items else 0
        df_pct = f"{df}/{n_items}={df / n_items:.0%}" if n_items else "—"
        black = next((b for b in BLACKLIST if b in low), "")
        generic = low in field_generic
        method = is_method_term(low)
        own_hit = bool(own_id is not None and own_id in own_corpus and low in own_corpus[own_id])

        if black:
            verdict = f"红旗：元词「{black}」——除非论文贡献本身就是它"
            n_red += 1
        elif generic:
            verdict = "红旗：领域泛词（说的是领域名，不是这篇论文）"
            n_red += 1
        elif n_items and df / n_items >= DF_GENERIC:
            verdict = "红旗：库内高频泛词（换文测试未过）"
            n_red += 1
        elif method:
            verdict = "术语（方法专名模式）"
        elif n_items and df / n_items >= DF_GRAY:
            verdict = "灰区：领域常见词，套专指测试找更具体的表述"
            n_gray += 1
        else:
            verdict = "术语（专属本文/低频）"
        if own_hit and "红旗" not in verdict:
            verdict += "；本篇标题/标签命中 ✓"
        print(f"| {term} | {span.get('category', '')} | {df_pct} | {black or '—'} | "
              f"{'✓' if generic else '—'} | {'✓' if method else '—'} | {'✓' if own_hit else '—'} | {verdict} |")

    print()
    tail = f"- 候选 {len(spans)} 个：红旗 {n_red}，灰区 {n_gray}"
    if n_items:
        tail += f"（语料：Zotero 库 {n_items} 篇标题/摘要/标签；DF≥15% 泛词、8–15% 灰区）"
    print(tail)
    print("- 只建议不拦截：红旗/灰区逐个过 SKILL.md 三测试后再定稿；泛词表可在 references/term-lexicon.yaml 扩充")


if __name__ == "__main__":
    main()
