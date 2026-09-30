#!/usr/bin/env python3
"""共享嵌入工具：term-lexicon.yaml 种子解析 + 质心缓存 + 余弦相似度。

check_terms_semantic.py（过滤层：该不该高亮）与 classify_color.py
（判色层：标哪种颜色）共用；本模块只负责"文本 → 向量 → 与质心的相似度"，
不做任何判定。阈值与判级逻辑归各调用方。
"""
import hashlib
import json
import os

import numpy as np
from fastembed import TextEmbedding

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LEXICON_PATH = os.path.join(SCRIPT_DIR, "..", "references", "term-lexicon.yaml")
CACHE_DIR = os.path.expanduser("~/.cache/zotero-pdf-highlighting")
MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def load_model():
    """加载嵌入模型；首次使用需联网/代理下载，之后永久离线。"""
    try:
        return TextEmbedding(MODEL)
    except Exception as e:
        raise SystemExit(f"错误：嵌入模型不可用（{e}）。首次使用需联网/代理下载模型；"
                         "下载后永久离线可用。")


def load_seed_sections(sections):
    """解析 term-lexicon.yaml 里指定 `xxx_seeds` 段的 '- 词' 列表。

    重复段头会重置该段；段内 '#' 后为注释；顶格非列表行结束当前段。
    """
    seeds = {name: [] for name in sections}
    current = None
    if os.path.exists(LEXICON_PATH):
        with open(LEXICON_PATH, encoding="utf-8") as f:
            for line in f:
                head = line.split("#")[0].rstrip().rstrip(":")
                if head in seeds:
                    current = head
                    seeds[current] = []
                    continue
                if current:
                    item = line.split("#")[0].strip()
                    if item.startswith("- "):
                        seeds[current].append(item[2:].strip())
                    elif item and not line.startswith((" ", "\t")):
                        current = None
    return seeds


def get_centroids(model, seeds):
    """各簇种子质心；按 模型+种子 指纹分文件缓存，种子改动自动重算。"""
    fingerprint = hashlib.md5(
        json.dumps({"model": MODEL, "seeds": seeds}, ensure_ascii=False, sort_keys=True)
        .encode()).hexdigest()
    cache_file = os.path.join(CACHE_DIR, f"seed_centroids-{fingerprint[:12]}.json")
    if os.path.exists(cache_file):
        cached = json.load(open(cache_file, encoding="utf-8"))
        return {k: np.array(v) for k, v in cached.items()}
    centroids = {}
    for name, words in seeds.items():
        if not words:
            continue
        arr = np.array(list(model.embed(words)))
        centroids[name] = arr.mean(0)
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump({k: v.tolist() for k, v in centroids.items()}, f)
    return centroids


def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def embed_one(model, text):
    """嵌入单个文本（fastembed 返回迭代器，取首个）。"""
    return next(iter(model.embed([text])))
