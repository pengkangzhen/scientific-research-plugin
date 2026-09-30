#!/usr/bin/env python3
"""PDF → 逐页归一化文本 JSON（zotero-pdf-highlighting 管线第 1 步）。

输出供 agent 挑选高亮片段：片段必须从本脚本的输出里**逐字复制**，
highlight_pdf.py 才能在同一套归一化文本上匹配命中。

归一化规则（与 highlight_pdf.py 的匹配端保持一致，两处必须同步修改）：
- 行内连续空白折叠为单个空格；
- 行尾断词连字符（"-" 或软连字符 U+00AD）删除，与下一行直接拼接；
- 行与行之间以单个空格连接。

用法：
    uv run extract_pages.py --pdf /path/to/paper.pdf [--out /tmp/pages.json]
"""
# /// script
# requires-python = ">=3.10"
# dependencies = ["pymupdf"]
# ///

import argparse
import json
import os
import sys

import pymupdf


def is_cjk(ch):
    """CJK 汉字与全角符号（行拼接时不插入连接空格的判定依据）。"""
    return ("\u4e00" <= ch <= "\u9fff" or "\u3000" <= ch <= "\u303f"
            or "\uff00" <= ch <= "\uffef" or "\u3400" <= ch <= "\u4dbf")


LIGATURES = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl"}


def line_chars(page):
    """rawdict → 按行分组的 [(字符, bbox), ...] 列表；连字（ﬁ/ﬂ…）展开为普通字母（共享原字符框）。"""
    lines = []
    raw = page.get_text("rawdict")
    for block in raw["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block["lines"]:
            chars = []
            for span in line["spans"]:
                for ch in span["chars"]:
                    c, bbox = ch["c"], tuple(ch["bbox"])
                    if c in LIGATURES:
                        chars.extend((part, bbox) for part in LIGATURES[c])
                    else:
                        chars.append((c, bbox))
            if chars:
                lines.append(chars)
    return lines


def normalize_lines(lines):
    """行列表 → (归一化文本, 条目列表)。

    条目为 (字符, bbox)；bbox=None 表示归一化插入的行间连接空格，无对应字符框。
    行内空格保留其真实字符框；行首/行尾空格丢弃。
    行间连接空格只在两侧都是西文时插入——汉字之间没有空格，跨行拼接直接相连。
    """
    norm = []
    for line in lines:
        cleaned = []           # 行内空白折叠后的 (字符, bbox)
        pending_space = None   # 待落空格的字符框（行首/行尾的丢弃）
        for c, bbox in line:
            if c.isspace():
                if cleaned and pending_space is None:
                    pending_space = bbox
            else:
                if pending_space is not None:
                    cleaned.append((" ", pending_space))
                    pending_space = None
                cleaned.append((c, bbox))
        if not cleaned:
            continue
        if norm:
            if norm[-1][0] in ("-", "\u00ad"):
                norm.pop()  # 行尾断词连字符：删除后与下一行直接拼接
            elif not (is_cjk(norm[-1][0]) or is_cjk(cleaned[0][0])):
                norm.append((" ", None))
        norm.extend(cleaned)
    text = "".join(c for c, _ in norm)
    return text, norm


def extract(pdf_path):
    doc = pymupdf.open(pdf_path)
    if doc.needs_pass:
        sys.exit("错误：PDF 已加密，无法抽取文本")
    pages = []
    for i, page in enumerate(doc):
        text, _ = normalize_lines(line_chars(page))
        pages.append({"page": i + 1, "text": text})
    return {"pdf": os.path.abspath(pdf_path), "page_count": len(pages), "pages": pages}


def main():
    ap = argparse.ArgumentParser(description="PDF → 逐页归一化文本 JSON")
    ap.add_argument("--pdf", required=True, help="PDF 文件路径（Zotero storage 中的文献 PDF）")
    ap.add_argument("--out", help="输出 JSON 路径；缺省打印到 stdout")
    args = ap.parse_args()

    payload = extract(args.pdf)
    dumped = json.dumps(payload, ensure_ascii=False, indent=1)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(dumped + "\n")
        print(f"已写出 {args.out}（{payload['page_count']} 页）", file=sys.stderr)
    else:
        print(dumped)


if __name__ == "__main__":
    main()
