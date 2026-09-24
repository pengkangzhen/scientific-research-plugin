#!/usr/bin/env python3
"""把 pdftoppm 渲染出的整页 PNG 拼成一张网格 contact sheet（总览图）。

slide-making 技能 §4 视觉验证循环第 2 步：低分辨率扫全貌找溢出/截断/空页，
再对最密几页读原图复核。每格上方标注页码文件名，避免扫图时数错页。

用法：
    python contact_sheet.py <PNG目录或glob模式> -o sheet.png [--cols N] [--tile-width 420]

    pdftoppm -png -r 120 presentation.pdf /tmp/slide-png
    python contact_sheet.py /tmp/slide-png -o /tmp/sheet.png

假设所有输入图同尺寸（同一份 PDF 的渲染页必然如此）。依赖 Pillow：
    uv run --with pillow python contact_sheet.py ...
"""
import argparse
import math
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def natural_key(path: Path):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", path.name)]


def collect_inputs(spec: str) -> list[Path]:
    p = Path(spec)
    if p.is_dir():
        files = sorted(p.glob("*.png"), key=natural_key)
    else:
        files = sorted(Path().glob(spec), key=natural_key)
    if not files:
        sys.exit(f"contact_sheet: 没有找到 PNG：{spec}")
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("inputs", help="PNG 目录或 glob 模式（如 '/tmp/slide-png'）")
    ap.add_argument("-o", "--output", required=True, help="输出 contact sheet 路径")
    ap.add_argument("--cols", type=int, default=0, help="列数，默认 ceil(sqrt(n)) 自动")
    ap.add_argument("--tile-width", type=int, default=420, help="单格缩略图宽（像素）")
    args = ap.parse_args()

    files = collect_inputs(args.inputs)
    thumbs = [Image.open(f) for f in files]
    tw = args.tile_width
    th = round(tw * thumbs[0].height / thumbs[0].width)
    label_h = 18
    cols = args.cols or math.ceil(math.sqrt(len(files)))
    rows = math.ceil(len(files) / cols)
    pad, margin = 6, 12

    sheet_w = margin * 2 + cols * tw + (cols + 1) * pad
    sheet_h = margin * 2 + rows * (th + label_h) + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), "#d9d9d9")
    draw = ImageDraw.Draw(sheet)

    for i, (f, im) in enumerate(zip(files, thumbs)):
        r, c = divmod(i, cols)
        x = margin + pad + c * (tw + pad)
        y = margin + pad + r * (th + label_h + pad)
        sheet.paste(im.resize((tw, th)), (x, y))
        draw.rectangle([x, y, x + tw, y + th], outline="#888888")
        draw.text((x + 2, y + th + 3), f.name, fill="#222222")

    sheet.save(args.output)
    print(f"contact_sheet: {len(files)} 页 → {args.output} "
          f"（{sheet_w}x{sheet_h}, {cols} 列）")


if __name__ == "__main__":
    main()
