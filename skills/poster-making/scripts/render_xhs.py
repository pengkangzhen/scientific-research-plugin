#!/usr/bin/env python3
"""
小红书卡片渲染脚本 - 智能分页版
将 Markdown 文件渲染为小红书风格的图片卡片

特性：
1. 智能分页：自动检测内容高度，超出时自动拆分到多张卡片
2. 多主题：主题清单外置于 assets/themes/themes.yaml
3. 代码高亮：依据主题清单的 highlight_style 注入 Pygments 样式
4. 卡片版式：--layout 选择版式（default 全要素图文 / list 标题+序号清单）

使用方法:
    uv run --no-sync python scripts/render_xhs.py <markdown_file> [options]

依赖安装:
    uv sync
    uv run --no-sync playwright install chromium
"""

import argparse
import asyncio
import os
import re
import sys
from html import escape
from pathlib import Path
from typing import Dict, List

try:
    import markdown
    import yaml
    from pygments.formatters import HtmlFormatter
    from pygments.util import ClassNotFound
    from playwright.async_api import (
        TimeoutError as PlaywrightTimeoutError,
        async_playwright,
        Page,
    )
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("请运行: uv sync && uv run --no-sync playwright install chromium")
    sys.exit(1)


# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent.parent
ASSETS_DIR = SCRIPT_DIR / "assets"

# 卡片尺寸配置 (3:4 比例)
CARD_WIDTH = 1080
CARD_HEIGHT = 1440

# 内容区域安全高度（考虑 padding 和 margin）
# card-inner padding: 60px * 2 = 120px
# card-container padding: 50px * 2 = 100px
# 页码区域: ~80px
# 安全边距: ~40px
SAFE_HEIGHT = CARD_HEIGHT - 120 - 100 - 80 - 40  # ~1100px

# 基础字体栈：主题未声明对应字体角色时回退使用（角色定义见 themes.yaml 字段说明）
DEFAULT_DISPLAY_FONT = "'Helvetica Neue', 'Noto Sans SC', 'Source Han Sans CN', 'PingFang SC', 'Microsoft YaHei', sans-serif"
DEFAULT_BODY_FONT = DEFAULT_DISPLAY_FONT
DEFAULT_UTILITY_FONT = DEFAULT_BODY_FONT


def load_themes() -> Dict[str, dict]:
    """从 assets/themes/themes.yaml 加载主题清单（唯一事实源），并校验配套文件与取值"""
    themes_file = ASSETS_DIR / "themes" / "themes.yaml"
    if not themes_file.exists():
        print(f"❌ 错误：主题清单不存在 - {themes_file}")
        sys.exit(1)

    with open(themes_file, "r", encoding="utf-8") as f:
        themes = yaml.safe_load(f) or {}

    if not themes:
        print(f"❌ 错误：主题清单为空 - {themes_file}")
        sys.exit(1)

    for key, theme in themes.items():
        css_file = ASSETS_DIR / "themes" / theme.get("css", "")
        if not css_file.exists():
            print(f"❌ 错误：主题 {key} 的样式文件不存在 - {css_file}")
            sys.exit(1)
        highlight_style = theme.get("highlight_style")
        if highlight_style:
            try:
                HtmlFormatter(style=highlight_style)
            except ClassNotFound:
                print(
                    f"❌ 错误：主题 {key} 的 highlight_style 无效 - {highlight_style}"
                )
                sys.exit(1)

    return themes


# 主题清单：外置于 assets/themes/themes.yaml，启动时加载并校验
THEMES = load_themes()


def load_theme_css(style: dict) -> str:
    """读取主题 CSS 文件内容（封面与正文卡片共用）；未配置或文件缺失时返回空串"""
    theme_css_path = style.get("css", "")
    if not theme_css_path:
        return ""
    theme_css_file = ASSETS_DIR / "themes" / theme_css_path
    if not theme_css_file.exists():
        return ""
    with open(theme_css_file, "r", encoding="utf-8") as f:
        return f.read()


def parse_markdown_file(file_path: str) -> dict:
    """解析 Markdown 文件，提取 YAML 头部和正文内容"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 解析 YAML 头部
    yaml_pattern = r"^---\s*\n(.*?)\n---\s*\n"
    yaml_match = re.match(yaml_pattern, content, re.DOTALL)

    metadata = {}
    body = content

    if yaml_match:
        try:
            metadata = yaml.safe_load(yaml_match.group(1)) or {}
        except yaml.YAMLError:
            metadata = {}
        body = content[yaml_match.end() :]

    return {"metadata": metadata, "body": body.strip()}


def split_content_by_separator(body: str) -> list:
    """按照 --- 分隔符拆分正文为多张卡片内容"""
    parts = re.split(r"\n---+\n", body)
    return [part.strip() for part in parts if part.strip()]


def convert_markdown_to_html(md_content: str) -> str:
    """将 Markdown 转换为 HTML"""

    # 处理 tags（以 # 开头的标签）
    tags_pattern = r"((?:#[\w\u4e00-\u9fa5]+\s*)+)$"
    tags_match = re.search(tags_pattern, md_content, re.MULTILINE)
    tags_html = ""

    if tags_match:
        tags_str = tags_match.group(1)
        md_content = md_content[: tags_match.start()].strip()
        tags = re.findall(r"#([\w\u4e00-\u9fa5]+)", tags_str)
        if tags:
            tags_html = '<div class="tags-container">'
            for tag in tags:
                tags_html += f'<span class="tag">#{tag}</span>'
            tags_html += "</div>"

    # 预处理：将2空格缩进的列表项转换为4空格（标准Markdown嵌套列表要求）
    lines = md_content.split("\n")
    processed_lines = []
    for line in lines:
        # 匹配以 "- " 或 "* " 或数字 ". " 开头的列表项，前面有2空格缩进
        # 将2空格缩进转换为4空格
        if re.match(r"^  [-*+] ", line) or re.match(r"^  \d+\. ", line):
            # 2空格 -> 4空格
            line = "  " + line
        elif re.match(r"^    [-*+] ", line) or re.match(r"^    \d+\. ", line):
            # 已经是4空格，检查是否需要更深层级（6空格 -> 8空格）
            pass
        elif re.match(r"^      [-*+] ", line) or re.match(r"^      \d+\. ", line):
            # 6空格 -> 8空格（三级嵌套）
            line = "  " + line
        processed_lines.append(line)

    md_content = "\n".join(processed_lines)

    # 转换 Markdown 为 HTML
    html = markdown.markdown(
        md_content, extensions=["extra", "codehilite", "tables", "nl2br"]
    )

    # 后处理：将表格单元格内的标签转换为带样式
    # 匹配 <td>中包含多个#标签的内容</td>
    def replace_tags_in_td(match):
        content = match.group(1)
        # 检查是否包含标签格式
        if re.search(r"(#[\w\u4e00-\u9fa5]+\s*)+", content):
            # 提取所有标签
            tags = re.findall(r"#([\w\u4e00-\u9fa5]+)", content)
            if tags:
                tags_html_inner = '<div class="tags-container" style="margin-top:0;padding-top:0;border-top:none;">'
                for tag in tags:
                    tags_html_inner += f'<span class="tag">#{tag}</span>'
                tags_html_inner += "</div>"
                return f"<td>{tags_html_inner}</td>"
        return match.group(0)

    # 处理表格单元格内的标签
    html = re.sub(
        r"<td>([^<]*((?:#[\w\u4e00-\u9fa5]+\s*)+)[^<]*)</td>", replace_tags_in_td, html
    )

    def strip_html_tags(content: str) -> str:
        return re.sub(r"<[^>]+>", "", content).replace("&nbsp;", " ").strip().lower()

    def render_metadata_panel(match):
        heading = match.group(1)
        table_html = match.group(2)

        rows = re.findall(r"<tr>(.*?)</tr>", table_html, flags=re.DOTALL)
        metadata_rows = []

        for row in rows:
            cells = re.findall(r"<t[hd]>(.*?)</t[hd]>", row, flags=re.DOTALL)
            if len(cells) != 2:
                continue

            first_text = strip_html_tags(cells[0])
            second_text = strip_html_tags(cells[1])
            if first_text in {"字段", "field", "key", "label"} and second_text in {
                "内容",
                "content",
                "value",
            }:
                continue

            metadata_rows.append((cells[0].strip(), cells[1].strip()))

        if not metadata_rows:
            return match.group(0)

        panel_parts = ['<div class="metadata-panel">']
        last_index = len(metadata_rows) - 1

        for index, (label, value) in enumerate(metadata_rows):
            row_class = "metadata-row"
            if index == last_index:
                row_class += " is-last"
            panel_parts.append(
                f'<div class="{row_class}">'
                f'<div class="metadata-label">{label}</div>'
                f'<div class="metadata-value">{value}</div>'
                "</div>"
            )

        panel_parts.append("</div>")
        return heading + "".join(panel_parts)

    html = re.sub(
        r"(<h2>[^<]*(?:基本信息|Metadata)[^<]*</h2>\s*)(<table>.*?</table>)",
        render_metadata_panel,
        html,
        flags=re.DOTALL,
    )

    return html + tags_html


def generate_cover_html_v2(metadata: dict, style_key: str = "academic") -> str:
    """生成封面 HTML - 增强版小红书风格

    新增特性：
    1. 装饰性背景元素（几何形状、点阵）
    2. 动态标题渐变色随主题变化
    3. 更精致的排版层次
    """
    style = THEMES[style_key]
    theme_css = load_theme_css(style)
    emoji = metadata.get("emoji", "📝")
    title = metadata.get("title", "标题")
    subtitle = metadata.get("subtitle", "")

    title_gradient = style["title_gradient"]

    # 动态调整标题字体大小
    title_len = len(title)
    if title_len <= 6:
        title_size = 140  # 极大
    elif title_len <= 10:
        title_size = 120  # 大
    elif title_len <= 18:
        title_size = 95  # 中
    elif title_len <= 30:
        title_size = 75  # 小
    else:
        title_size = 58  # 极小

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width:1080, height:1440">
    <title>小红书封面</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: {style.get('font_body', DEFAULT_BODY_FONT)};
            width: 1080px; height: 1440px; overflow: hidden;
        }}

        /* 主容器 */
        .cover-container {{
            width: 1080px; height: 1440px;
            background: {style['cover_bg']};
            position: relative; overflow: hidden;
        }}

        /* 装饰性背景元素 */
        .deco-circle {{
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.08);
        }}
        .deco-circle-1 {{ width: 600px; height: 600px; top: -200px; right: -150px; }}
        .deco-circle-2 {{ width: 400px; height: 400px; bottom: 100px; left: -100px; }}
        .deco-circle-3 {{ width: 200px; height: 200px; top: 50%; right: 50px; opacity: 0.5; }}

        /* 点阵装饰 */
        .deco-dots {{
            position: absolute;
            width: 100%; height: 100%;
            background-image: radial-gradient(circle, rgba(255,255,255,0.1) 2px, transparent 2px);
            background-size: 40px 40px;
            pointer-events: none;
        }}

        /* 波浪装饰线 */
        .deco-wave {{
            position: absolute;
            bottom: 300px;
            left: 0; right: 0;
            height: 100px;
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 120' preserveAspectRatio='none'%3E%3Cpath d='M0,60 C150,120 350,0 600,60 C850,120 1050,0 1200,60 L1200,120 L0,120 Z' fill='rgba(255,255,255,0.05)'/%3E%3C/svg%3E") repeat-x;
            background-size: 1200px 100px;
        }}

        /* 内容卡片 */
        .cover-inner {{
            position: absolute; width: 950px; height: 1310px;
            left: 65px; top: 65px;
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(250,250,250,0.95) 100%);
            border-radius: 32px;
            display: flex; flex-direction: column;
            padding: 80px 85px;
            box-shadow: 0 25px 80px rgba(0, 0, 0, 0.15);
        }}

        /* 顶部装饰条 */
        .cover-inner::before {{
            content: '';
            position: absolute;
            top: 40px; left: 85px; right: 85px;
            height: 6px;
            background: {title_gradient};
            border-radius: 3px;
            opacity: 0.6;
        }}

        /* Emoji 区域 */
        .cover-emoji {{
            font-size: 160px;
            line-height: 1;
            margin-bottom: 60px;
            margin-top: 40px;
            filter: drop-shadow(0 8px 16px rgba(0,0,0,0.1));
        }}

        /* 标题样式 */
        .cover-title {{
            font-family: {style.get('font_display', DEFAULT_DISPLAY_FONT)};
            font-weight: 900;
            font-size: {title_size}px;
            line-height: 1.35;
            background: {title_gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            flex: 1;
            display: flex; align-items: flex-start;
            word-break: break-word;
            overflow-wrap: break-word;
            letter-spacing: -0.02em;
            text-shadow: none;
        }}

        /* 副标题样式 */
        .cover-subtitle {{
            font-weight: 400;
            font-size: 64px;
            line-height: 1.5;
            color: #374151;
            margin-top: auto;
            padding-top: 30px;
            border-top: 2px solid rgba(0,0,0,0.06);
            position: relative;
        }}

        /* 副标题装饰 */
        .cover-subtitle::before {{
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 80px; height: 2px;
            background: {style['accent_color']};
        }}

        /* 底部装饰 */
        .cover-footer {{
            position: absolute;
            bottom: 40px; right: 60px;
            display: flex; align-items: center; gap: 12px;
        }}
        .cover-footer-dot {{
            width: 12px; height: 12px;
            border-radius: 50%;
            background: {style['accent_color']};
            opacity: 0.6;
        }}

        /* === 主题覆盖样式（含封面签名元素） === */
        {theme_css}
    </style>
</head>
<body>
    <div class="cover-container">
        <!-- 装饰元素 -->
        <div class="deco-dots"></div>
        <div class="deco-circle deco-circle-1"></div>
        <div class="deco-circle deco-circle-2"></div>
        <div class="deco-circle deco-circle-3"></div>
        <div class="deco-wave"></div>

        <!-- 主内容 -->
        <div class="cover-inner">
            <div class="cover-emoji">{emoji}</div>
            <div class="cover-title">{title}</div>
            <div class="cover-subtitle">{subtitle}</div>
        </div>

        <!-- 底部装饰 -->
        <div class="cover-footer">
            <div class="cover-footer-dot"></div>
            <div class="cover-footer-dot" style="opacity: 0.4;"></div>
            <div class="cover-footer-dot" style="opacity: 0.2;"></div>
        </div>
    </div>
</body>
</html>"""


def generate_card_html_v2(
    content: str,
    page_number: int = 1,
    total_pages: int = 1,
    style_key: str = "academic",
    mode: str = "separator",
) -> str:
    """生成正文卡片 HTML - 增强版小红书风格

    Args:
        content: Markdown 内容
        page_number: 页码
        total_pages: 总页数
        style_key: 样式键
        mode: 分页模式 - 'separator'(固定高度), 'dynamic'(动态高度)

    新增特性：
    1. 支持加载外部主题 CSS 文件
    2. 优化代码块、引用块样式
    3. 增加装饰元素
    """
    style = THEMES[style_key]
    html_content = convert_markdown_to_html(content)

    # Pygments 代码高亮样式：依据主题清单的 highlight_style 注入
    highlight_css = ""
    if style.get("highlight_style"):
        highlight_css = HtmlFormatter(style=style["highlight_style"]).get_style_defs(
            ".codehilite"
        )
    page_text = f"{page_number}/{total_pages}" if total_pages > 1 else ""

    # 动态高度模式：不使用固定的最小高度
    # 只有 dynamic 模式去掉 min-height
    min_height_css = "min-height: auto;" if mode == "dynamic" else "min-height: 1340px;"

    # 外部主题 CSS（含签名元素）
    theme_css = load_theme_css(style)

    # 基础样式 + 主题覆盖
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width:1080">
    <title>小红书卡片</title>
    <!-- KaTeX for LaTeX rendering -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: {style.get('font_body', DEFAULT_BODY_FONT)};
            width: 1080px; min-height: 1440px; overflow: hidden; background: transparent;
        }}

        /* === 卡片容器 === */
        .card-container {{
            width: 1080px; min-height: 1440px;
            background: {style['card_bg']};
            position: relative; padding: 50px; overflow: hidden;
        }}

        /* 装饰性背景 */
        .card-container::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: radial-gradient(circle at 20% 80%, rgba(255,255,255,0.1) 0%, transparent 50%),
                              radial-gradient(circle at 80% 20%, rgba(255,255,255,0.08) 0%, transparent 40%);
            pointer-events: none;
        }}

        /* === 内容卡片 === */
        .card-inner {{
            background: rgba(255, 255, 255, 0.97);
            border-radius: 28px;
            padding: 60px;
            {min_height_css}
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12), 0 8px 24px rgba(0, 0, 0, 0.08);
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }}

        /* 卡片顶部装饰线 */
        .card-inner::before {{
            content: '';
            position: absolute;
            top: 0; left: 60px; right: 60px;
            height: 5px;
            background: {style['title_gradient']};
            border-radius: 0 0 3px 3px;
        }}

        /* === 内容样式 === */
        .card-content {{
            color: #475569;
            font-size: 42px;
            line-height: 1.75;
        }}

        /* 标题样式 */
        .card-content h1 {{
            font-family: {style.get('font_display', DEFAULT_DISPLAY_FONT)};
            font-size: 68px; font-weight: 800; color: #1e293b;
            margin-bottom: 40px; line-height: 1.3;
            padding-bottom: 20px;
            border-bottom: 3px solid {style['accent_color']};
        }}
        .card-content h2 {{
            font-family: {style.get('font_display', DEFAULT_DISPLAY_FONT)};
            font-size: 54px; font-weight: 700; color: #334155;
            margin: 50px 0 25px 0; line-height: 1.4;
            padding-left: 24px;
            border-left: 6px solid {style['accent_color']};
        }}
        .card-content h3 {{
            font-size: 46px; font-weight: 600; color: #475569;
            margin: 40px 0 20px 0;
            position: relative;
            padding-left: 20px;
        }}
        .card-content h3::before {{
            content: '▸';
            position: absolute;
            left: 0;
            color: {style['accent_color']};
        }}

        .card-content p {{ margin-bottom: 35px; }}
        .card-content strong {{ font-weight: 700; color: #1e293b; }}
        .card-content em {{ font-style: italic; color: {style['accent_color']}; }}

        /* 链接样式 */
        .card-content a {{
            color: {style['accent_color']}; text-decoration: none;
            border-bottom: 2px solid {style['accent_color']};
            padding-bottom: 2px;
        }}

        /* 列表样式 */
        .card-content ul, .card-content ol {{
            margin: 30px 0; padding-left: 60px;
        }}
        /* 嵌套列表缩进 */
        .card-content ul ul, .card-content ol ol,
        .card-content ul ol, .card-content ol ul {{
            margin: 15px 0; padding-left: 50px;
        }}
        .card-content li {{
            margin-bottom: 20px; line-height: 1.6;
        }}
        .card-content li::marker {{
            color: {style['accent_color']};
            font-weight: 700;
        }}
        /* 嵌套列表标记样式 */
        .card-content ul ul li::marker {{
            content: '◦';  /* 空心圆点 */
            font-size: 36px;
        }}
        .card-content ul ul ul li::marker {{
            content: '▪';  /* 实心方块 */
            font-size: 32px;
        }}
        .card-content ol ol li::marker {{
            font-size: 36px;
            font-weight: 600;
        }}

        /* 引用块样式 - 增强 */
        .card-content blockquote {{
            border-left: 6px solid {style['accent_color']};
            padding: 30px 40px;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.06) 0%, rgba(139, 92, 246, 0.04) 100%);
            margin: 35px 0;
            color: #475569;
            font-style: normal;
            border-radius: 0 16px 16px 0;
            position: relative;
        }}
        .card-content blockquote::before {{
            content: '"';
            position: absolute;
            top: 10px; left: 15px;
            font-size: 60px;
            color: {style['accent_color']};
            opacity: 0.2;
            font-family: Georgia, serif;
            line-height: 1;
        }}
        .card-content blockquote p {{ margin: 0; }}

        /* 行内代码样式 */
        .card-content code {{
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
            padding: 4px 14px; border-radius: 8px;
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
            font-size: 38px;
            color: {style['accent_color']};
            border: 1px solid rgba(0,0,0,0.05);
        }}

        /* 代码块样式 - 增强 */
        .card-content pre {{
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            color: #e2e8f0;
            padding: 40px;
            border-radius: 20px;
            margin: 35px 0;
            overflow-x: visible;
            overflow-wrap: break-word;
            word-wrap: break-word;
            word-break: normal;
            white-space: pre-wrap;
            font-size: 36px; line-height: 1.6;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.3);
            border-left: 5px solid {style['accent_color']};
        }}
        .card-content pre code {{
            background: transparent; color: inherit; padding: 0; font-size: inherit;
            border: none;
        }}

        /* 图片样式 */
        .card-content img {{
            max-width: 100%; height: auto; border-radius: 16px;
            margin: 35px auto; display: block;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        }}

        /* 分割线样式 */
        .card-content hr {{
            border: none; height: 3px;
            background: linear-gradient(90deg, transparent 0%, {style['accent_color']} 50%, transparent 100%);
            margin: 50px 0;
        }}

        /* 表格样式 - 无边框条纹式 */
        .card-content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 40px 0;
            font-size: 38px;
            font-family: {style.get('font_utility', DEFAULT_UTILITY_FONT)};
        }}
        .card-content th {{
            background: #f8fafc;
            font-weight: 600;
            color: #1e293b;
            padding: 20px 24px;
            text-align: left;
            border-bottom: 2px solid #e2e8f0;
        }}
        .card-content td {{
            padding: 18px 24px;
            border-bottom: 1px solid #f1f5f9;
            color: #475569;
            line-height: 1.5;
        }}
        .card-content tr:last-child td {{
            border-bottom: none;
        }}
        .card-content tr:nth-child(even) {{
            background: {style.get('zebra_color', 'rgba(248, 250, 252, 0.6)')};
        }}

        /* Metadata 信息面板 */
        .card-content .metadata-panel {{
            margin: 18px 0 8px;
            padding: 18px 20px;
            border-radius: 20px;
            background: linear-gradient(180deg, #f8fbff 0%, #f1f5f9 100%);
            border: 1px solid #e2e8f0;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
        }}
        .card-content .metadata-row {{
            padding: 14px 0;
            border-bottom: 1px solid #e2e8f0;
        }}
        .card-content .metadata-row:first-child {{
            padding-top: 0;
        }}
        .card-content .metadata-row.is-last {{
            padding-bottom: 0;
            border-bottom: none;
        }}
        .card-content .metadata-label {{
            margin-bottom: 6px;
            color: {style['accent_color']};
            font-size: inherit;
            font-weight: 700;
            line-height: 1.35;
        }}
        .card-content .metadata-value {{
            color: inherit;
            font-size: inherit;
            line-height: inherit;
        }}
        .card-content .metadata-value .tags-container {{
            margin-top: 0;
            padding-top: 0;
            border-top: none;
        }}

        /* 标签样式由主题CSS控制 */

        /* 页码样式 */
        .page-number {{
            position: absolute;
            bottom: 80px; right: 80px;
            font-size: 36px;
            font-family: {style.get('font_utility', DEFAULT_UTILITY_FONT)};
            color: rgba(255, 255, 255, 0.9);
            font-weight: 600;
            text-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}

        /* === 主题覆盖样式 === */
        {theme_css}

        /* === Pygments 代码高亮 === */
        {highlight_css}
    </style>
</head>
<body>
    <div class="card-container">
        <div class="card-inner">
            <div class="card-content">
                {html_content}
            </div>
        </div>
        {f'<div class="page-number">{page_text}</div>' if page_text else ''}
    </div>
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: '$$', right: '$$', display: true}},
                    {{left: '\\\\[', right: '\\\\]', display: true}},
                    {{left: '$', right: '$', display: false}},
                    {{left: '\\\\(', right: '\\\\)', display: false}}
                ],
                throwOnError: false
            }});
        }});
    </script>
</body>
</html>"""


def _highlight_html(text: str) -> str:
    """==文本== → <span class="hl">文本</span>（marker 笔刷高亮），其余内容 HTML 转义"""
    parts = re.split(r"==(.+?)==", text)
    out = []
    for index, part in enumerate(parts):
        escaped = escape(part)
        out.append(f'<span class="hl">{escaped}</span>' if index % 2 else escaped)
    return "".join(out)


# 榜单版式：条目开头可带一个 emoji 作图标
_RANKING_EMOJI_RE = re.compile(
    r"^([\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF][\uFE0F]?)\s*"
)

# 榜单版式马卡龙色板：(行底色, 序号徽章底色)，循环取用
_RANKING_PALETTE = [
    ("#fdf3d0", "#f7ce46"),
    ("#f3f1ec", "#e2dfd6"),
    ("#e4f0e0", "#bfe0b4"),
    ("#fdebd8", "#f8cba0"),
    ("#e9e6f8", "#c9c2f0"),
    ("#e2f0e6", "#b7dfc4"),
    ("#ddeefa", "#b3d4f2"),
    ("#fbe4e4", "#f4bdbd"),
    ("#eae6f5", "#cfc5ec"),
    ("#f6efdc", "#e8d28a"),
]


def parse_ranking_content(md_content: str) -> dict:
    """解析榜单版式输入：

        # 大标题（==文本== 标记笔刷高亮）
        > 副标题（可选，居中）
        1. 🔍 条目标题｜一句话介绍｜340万+ 次｜#标签1 #标签2

    条目按 ｜ 或 | 切四段：标题（可带开头 emoji 作图标）／介绍／数值（空格前
    为主数值后为单位）／行尾 #标签；介绍与数值段可空。YAML 头可选字段：
    brand、brand_sub、slogan、tip、corner（多行文本用 \\n）。
    """
    yaml_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", md_content, re.DOTALL)
    metadata = {}
    if yaml_match:
        try:
            metadata = yaml.safe_load(yaml_match.group(1)) or {}
        except yaml.YAMLError:
            metadata = {}
        md_content = md_content[yaml_match.end() :]

    title = ""
    subtitle = ""
    entries = []
    for raw_line in md_content.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        if not title and line.startswith("#"):
            title = line.lstrip("#").strip()
            continue
        if not subtitle and line.startswith(">"):
            subtitle = line.lstrip(">").strip()
            continue
        entry_match = re.match(r"^\d+\s*[.、)）]\s*(.+)$", line)
        if entry_match:
            entries.append(entry_match.group(1).strip())

    items = []
    for entry in entries:
        segments = [s.strip() for s in re.split(r"\s*[｜|]\s*", entry)]
        icon = ""
        emoji_match = _RANKING_EMOJI_RE.match(segments[0])
        if emoji_match:
            icon = emoji_match.group(1)
            segments[0] = segments[0][emoji_match.end() :].strip()
        metric = segments[2] if len(segments) > 2 else ""
        metric_main, metric_unit = (
            (metric.split(" ", 1) + [""])[:2] if metric else ("", "")
        )
        # 标签段：以 # 分界切分，标签内可含空格（如「#AI 代理」）
        tags = (
            [t.strip() for t in re.findall(r"#([^#]+)", segments[3] + " ") if t.strip()]
            if len(segments) > 3
            else []
        )
        items.append(
            {
                "icon": icon,
                "title": segments[0],
                "desc": segments[1] if len(segments) > 1 else "",
                "metric": metric_main,
                "unit": metric_unit,
                "tags": tags,
            }
        )

    def _meta(key: str) -> str:
        value = metadata.get(key, "")
        return str(value) if value is not None else ""

    return {
        "title": title,
        "subtitle": subtitle,
        "items": items,
        "brand": _meta("brand"),
        "brand_sub": _meta("brand_sub"),
        "slogan": _meta("slogan"),
        "tip": _meta("tip"),
        "corner": _meta("corner"),
    }


async def set_content_resilient(page: Page, html_content: str):
    """注入页面内容；CDN（Google Fonts 等）拖住 networkidle 时降级为固定等待

    networkidle 要求网络完全静默，字体 CDN 卡顿会让它超时——但此时内容早已
    注入 DOM，等一拍让脚本（KaTeX）跑完即可继续。
    """
    try:
        await page.set_content(html_content, wait_until="networkidle")
    except PlaywrightTimeoutError:
        await page.wait_for_timeout(2500)


def generate_ranking_card_html_v2(parsed: dict, style_key: str) -> str:
    """生成榜单版式卡片 HTML：页眉品牌/标语 + 笔刷高亮大标题 + 马卡龙色榜单行 + 手写体页脚

    行内五段：序号徽章（第 1 名戴皇冠）、emoji 图标、标题+介绍+标签胶囊、右侧数值。
    马卡龙色板为版式自带装饰（与主题无关）；条目越多行内尺寸越紧凑（10 条满编不溢出）。
    """
    style = THEMES[style_key]
    theme_css = load_theme_css(style)
    items = parsed["items"]
    count = len(items)

    handwriting_font = "'Hannotate SC', 'Xingkai SC', 'STKaiti', 'KaiTi', cursive"

    # 三档行内尺寸（条数越多越紧凑），10 条满编含页眉页脚不溢出 1440 高度
    if count <= 6:
        row_pad, badge_s, icon_s = 18, 68, 62
        title_s, desc_s, tag_s, metric_s = 32, 24, 20, 32
    elif count <= 8:
        row_pad, badge_s, icon_s = 10, 58, 52
        title_s, desc_s, tag_s, metric_s = 28, 21, 18, 28
    else:
        row_pad, badge_s, icon_s = 6, 50, 44
        title_s, desc_s, tag_s, metric_s = 25, 17, 15, 25

    title_len = len(parsed["title"])
    if title_len <= 12:
        card_title_size = 64
    elif title_len <= 20:
        card_title_size = 54
    else:
        card_title_size = 46

    rows_html = ""
    for index, item in enumerate(items):
        row_bg, badge_bg = _RANKING_PALETTE[index % len(_RANKING_PALETTE)]
        number = f"{index + 1:02d}"
        crown = '<div class="rank-crown">👑</div>' if index == 0 else ""
        icon_html = (
            f'<div class="rank-icon" style="font-size: {int(icon_s * 0.55)}px;">'
            f"{escape(item['icon'])}</div>"
            if item["icon"]
            else ""
        )
        tags_html = "".join(
            f'<span class="rank-tag">#{escape(t)}</span>' for t in item["tags"]
        )
        tags_block = f'<div class="rank-tags">{tags_html}</div>' if tags_html else ""
        desc_html = (
            f'<div class="rank-desc">{escape(item["desc"])}</div>'
            if item["desc"]
            else ""
        )
        metric_html = ""
        if item["metric"]:
            unit_html = (
                f'<div class="metric-unit">{escape(item["unit"])}</div>'
                if item["unit"]
                else ""
            )
            metric_html = (
                '<div class="rank-metric">'
                f'<div class="metric-main">⭐ {escape(item["metric"])}</div>'
                f"{unit_html}</div>"
            )
        rows_html += f"""            <div class="rank-row" style="background: {row_bg}; padding: {row_pad}px 22px;">
                <div class="rank-badge" style="width: {badge_s}px; height: {badge_s}px; background: {badge_bg}; font-size: {int(badge_s * 0.45)}px;">{crown}{number}</div>
                {icon_html}
                <div class="rank-body">
                    <div class="rank-title">{escape(item["title"])}</div>
                    {desc_html}
                    {tags_block}
                </div>
                {metric_html}
            </div>
"""

    header_html = ""
    if parsed["brand"]:
        sub_html = (
            f'<div class="brand-sub">{escape(parsed["brand_sub"])}</div>'
            if parsed["brand_sub"]
            else ""
        )
        slogan_html = (
            f'<div class="slogan">{escape(parsed["slogan"])}</div>'
            if parsed["slogan"]
            else ""
        )
        header_html = f"""        <div class="header">
            <div class="header-left"><div class="brand">{escape(parsed["brand"])}</div>{sub_html}</div>
            {slogan_html}
        </div>"""

    footer_html = ""
    if parsed["tip"] or parsed["corner"]:
        tip_html = (
            '<div class="tip"><span class="tip-bulb">💡</span>'
            '<span class="tip-label">小提示：</span>'
            f'{escape(parsed["tip"])}</div>'
            if parsed["tip"]
            else "<div></div>"
        )
        corner_html = (
            f'<div class="corner">{escape(parsed["corner"])}</div>'
            if parsed["corner"]
            else "<div></div>"
        )
        footer_html = f"""        <div class="footer">
            {tip_html}
            {corner_html}
        </div>"""

    subtitle_html = (
        f'<div class="rank-subtitle">{escape(parsed["subtitle"])}</div>'
        if parsed["subtitle"]
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width:1080, height:1440">
    <title>小红书榜单卡片</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: {style.get('font_body', DEFAULT_BODY_FONT)};
            width: 1080px; height: 1440px; overflow: hidden; background: transparent;
        }}
        .card-container {{
            width: 1080px; height: 1440px;
            background: {style['card_bg']};
            position: relative; padding: 32px 44px; overflow: hidden;
            display: flex; flex-direction: column;
        }}
        /* === 页眉 === */
        .header {{
            display: flex; justify-content: space-between; align-items: flex-start;
            margin-bottom: 12px;
        }}
        .header-left {{ display: flex; align-items: center; gap: 18px; }}
        .brand {{
            background: #1f2937; color: #ffffff;
            border-radius: 14px; padding: 10px 22px;
            font-size: 26px; font-weight: 800;
        }}
        .brand-sub {{
            color: #6b7280; font-size: 19px; line-height: 1.45;
            white-space: pre-line;
        }}
        .slogan {{
            font-family: {handwriting_font};
            color: #374151; font-size: 25px; line-height: 1.4;
            white-space: pre-line;
            border-bottom: 3px solid {_RANKING_PALETTE[0][1]};
            padding-bottom: 2px;
        }}
        /* === 大标题与副标题 === */
        .rank-header-title {{
            text-align: center;
            font-family: {style.get('font_body', DEFAULT_BODY_FONT)};
            font-size: {card_title_size}px; font-weight: 900; color: #111827;
            line-height: 1.25;
            margin-bottom: 10px;
            word-break: break-word; overflow-wrap: break-word;
        }}
        .hl {{
            background: linear-gradient(180deg, transparent 52%, {_RANKING_PALETTE[0][1]} 52%, {_RANKING_PALETTE[0][1]} 94%, transparent 94%);
            padding: 0 8px;
            border-radius: 6px;
        }}
        .rank-subtitle {{
            text-align: center; color: #6b7280;
            font-size: 22px; line-height: 1.4;
            margin-bottom: 10px;
            white-space: pre-line;
        }}
        /* === 榜单行 === */
        .rank-rows {{
            flex: 1;
            display: flex; flex-direction: column;
            justify-content: space-evenly; gap: 6px;
        }}
        .rank-row {{
            border-radius: 22px;
            display: flex; align-items: center;
            gap: 18px;
            box-shadow: 0 3px 10px rgba(15, 23, 42, 0.05);
        }}
        .rank-badge {{
            flex-shrink: 0;
            border-radius: 18px;
            color: #1f2937; font-weight: 800;
            font-family: {style.get('font_body', DEFAULT_BODY_FONT)};
            display: flex; align-items: center; justify-content: center;
            position: relative;
        }}
        .rank-crown {{
            position: absolute; top: -34px; left: 50%;
            transform: translateX(-50%);
            font-size: 30px; line-height: 1;
        }}
        .rank-icon {{
            flex-shrink: 0;
            width: {icon_s}px; height: {icon_s}px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            display: flex; align-items: center; justify-content: center;
        }}
        .rank-body {{ flex: 1; min-width: 0; }}
        .rank-title {{
            font-size: {title_s}px; font-weight: 800; color: #111827;
            line-height: 1.3;
            word-break: break-word; overflow-wrap: break-word;
        }}
        .rank-desc {{
            font-size: {desc_s}px; color: #4b5563; line-height: 1.4;
            margin-top: 2px;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }}
        .rank-tags {{
            display: flex; flex-wrap: wrap; gap: 8px;
            margin-top: 5px;
        }}
        .rank-tag {{
            background: rgba(255, 255, 255, 0.65);
            color: #374151;
            border-radius: 999px;
            padding: 2px 14px;
            font-size: {tag_s}px; font-weight: 500; line-height: 1.4;
            white-space: nowrap;
        }}
        .rank-metric {{
            flex-shrink: 0; text-align: center;
            min-width: 130px;
        }}
        .metric-main {{
            font-size: {metric_s}px; font-weight: 900; color: #111827;
            white-space: nowrap;
        }}
        .metric-unit {{
            font-size: {int(metric_s * 0.58)}px; color: #6b7280;
            margin-top: 2px;
        }}
        /* === 页脚 === */
        .footer {{
            display: flex; justify-content: space-between; align-items: center;
            gap: 24px;
            margin-top: 12px;
        }}
        .tip {{
            font-family: {handwriting_font};
            color: #374151; font-size: 21px; line-height: 1.5;
            white-space: pre-line;
        }}
        .tip-bulb {{ font-size: 30px; }}
        .tip-label {{ font-weight: 700; }}
        .corner {{
            background: #374151; color: #f9fafb;
            font-family: {handwriting_font};
            border-radius: 18px; padding: 12px 24px;
            font-size: 20px; line-height: 1.5;
            white-space: pre-line;
            text-align: center;
        }}

        /* === 主题覆盖样式 === */
        {theme_css}
    </style>
</head>
<body>
    <div class="card-container">
{header_html}
        <div class="rank-header-title">{_highlight_html(parsed["title"])}</div>
        {subtitle_html}
        <div class="rank-rows">
{rows_html}        </div>
{footer_html}
    </div>
</body>
</html>"""


async def measure_content_height(page, html_content: str) -> int:
    """使用 Playwright 测量实际内容高度"""
    await set_content_resilient(page, html_content)
    await page.wait_for_timeout(1500)

    height = await page.evaluate("""() => {
        // 测量实际内容高度，不受 min-height 影响
        const content = document.querySelector('.card-content');
        if (content) {
            return content.scrollHeight;
        }
        const inner = document.querySelector('.card-inner');
        if (inner) {
            return inner.scrollHeight;
        }
        const container = document.querySelector('.card-container');
        return container ? container.scrollHeight : document.body.scrollHeight;
    }""")

    return height


async def auto_split_content(
    body: str, style_key: str, width: int, height: int, dpr: int = 2
) -> List[str]:
    """自动切分内容：根据渲染后的实际高度自动分页

    核心逻辑：
    1. 按段落分割，但将标题和后续内容绑定在一起
    2. 使用 Playwright 真实渲染测量高度
    3. 只有超出时才切分到新卡片
    4. 智能填充优化：尝试填满每张卡片，减少空白
    """
    # 将内容按段落分割（双换行）
    raw_paragraphs = re.split(r"\n\n+", body)

    # 将标题和后续内容绑定：标题不单独成块，而是和下一段内容合并
    paragraphs = []
    pending_title = None

    for para in raw_paragraphs:
        if not para.strip():
            continue

        # 检查是否是标题行（以 # 开头）
        lines = para.strip().split("\n")
        is_all_title = all(
            line.strip().startswith("#") or not line.strip() for line in lines
        ) and any(line.strip().startswith("#") for line in lines)

        if is_all_title and len(lines) <= 3:  # 纯标题块（最多3行标题）
            pending_title = para
        else:
            if pending_title:
                # 将标题和当前内容合并
                paragraphs.append(pending_title + "\n\n" + para)
                pending_title = None
            else:
                paragraphs.append(para)

    # 处理末尾遗留的标题
    if pending_title:
        paragraphs.append(pending_title)

    # 内容区域的可用高度（去除 padding 等）
    available_height = height - 220

    # 第一轮：基础分页
    initial_cards = []
    current_content = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": width, "height": height * 2}, device_scale_factor=dpr
        )

        try:
            for para in paragraphs:
                if not para.strip():
                    continue

                # 尝试将当前段落加入
                test_content = current_content + [para]
                test_md = "\n\n".join(test_content)

                html = generate_card_html_v2(test_md, 1, 1, style_key, "auto-split")
                content_height = await measure_content_height(page, html)

                if content_height > available_height and current_content:
                    # 当前卡片已满，保存并开始新卡片
                    initial_cards.append("\n\n".join(current_content))
                    current_content = [para]
                else:
                    current_content = test_content

            # 保存最后一张卡片
            if current_content:
                initial_cards.append("\n\n".join(current_content))

            # 第二轮：智能填充优化
            # 如果某页填充率低于阈值，尝试从下一页移动内容上来
            MIN_FILL_RATIO = 0.70  # 填充率阈值

            for i in range(len(initial_cards) - 1):  # 不处理最后一页
                card_content = initial_cards[i]

                # 测量当前卡片实际内容高度
                html = generate_card_html_v2(
                    card_content, 1, 1, style_key, "auto-split"
                )
                content_height = await measure_content_height(page, html)
                fill_ratio = content_height / available_height

                # 如果填充率低于阈值，尝试从下一页借内容
                if fill_ratio < MIN_FILL_RATIO:
                    next_card = initial_cards[i + 1]
                    next_paragraphs = [
                        p.strip() for p in re.split(r"\n\n+", next_card) if p.strip()
                    ]

                    # 尝试从下一页移动段落到当前页
                    borrowed_indices = []
                    for idx, para in enumerate(next_paragraphs):
                        test_content = card_content + "\n\n" + para
                        test_html = generate_card_html_v2(
                            test_content, 1, 1, style_key, "auto-split"
                        )
                        test_height = await measure_content_height(page, test_html)

                        if test_height <= available_height:
                            card_content = test_content
                            borrowed_indices.append(idx)
                        else:
                            break

                    # 更新内容
                    if borrowed_indices:
                        initial_cards[i] = card_content
                        # 保留未被借走的段落
                        remaining = [
                            p
                            for j, p in enumerate(next_paragraphs)
                            if j not in borrowed_indices
                        ]
                        initial_cards[i + 1] = (
                            "\n\n".join(remaining) if remaining else ""
                        )

            # 移除空卡片
            optimized_cards = [c for c in initial_cards if c.strip()]

            # 移除空卡片
            final_cards = [c for c in optimized_cards if c.strip()]

        finally:
            await browser.close()

    return final_cards


async def render_html_to_image(
    html_content: str,
    output_path: str,
    width: int = 1080,
    height: int = 1440,
    mode: str = "separator",
    post_measure_js: str = None,
):
    """使用 Playwright 将 HTML 渲染为图片

    Args:
        html_content: HTML 内容
        output_path: 输出路径
        width: 图片宽度
        height: 图片高度（最大高度）
        mode: 分页模式 - 'separator'(固定高度), 'dynamic'(动态高度)
        post_measure_js: 可选；截图前在页面里执行的检测脚本，返回值透传给调用方
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height})

        try:
            await set_content_resilient(page, html_content)
            # 等待 KaTeX 渲染完成
            await page.wait_for_timeout(1500)

            extra_result = None
            if post_measure_js:
                extra_result = await page.evaluate(post_measure_js)

            # 动态高度模式：根据实际内容高度调整截图高度
            if mode == "dynamic":
                actual_height = await page.evaluate("() => document.body.scrollHeight")
                # 最小高度 800px，最大高度 1440px
                screenshot_height = max(800, min(height, actual_height))
            else:
                screenshot_height = height

            await page.screenshot(
                path=output_path,
                clip={"x": 0, "y": 0, "width": width, "height": screenshot_height},
                type="png",
            )
            print(f"  ✅ 已生成：{output_path} ({screenshot_height}px)")
            return extra_result
        finally:
            await browser.close()


def render_content_to_cards(
    card_contents: List[str],
    metadata: dict,
    output_dir: str,
    style_key: str,
    no_paginate: bool,
    mode: str = "separator",
):
    """渲染直接输入的内容到卡片"""
    print(f"\n🎨 开始渲染内容")
    print(f"🎨 使用样式：{THEMES[style_key]['name']}")
    print(f"🎨 分页模式：{mode}")

    os.makedirs(output_dir, exist_ok=True)

    if no_paginate:
        print(f"  📄 内容将保持完整，不分页")
        asyncio.run(
            render_single_card(card_contents[0], metadata, output_dir, style_key, mode)
        )
    else:
        asyncio.run(
            render_markdown_to_cards_common(
                card_contents, metadata, output_dir, style_key, mode
            )
        )


async def render_single_card(
    content: str,
    metadata: dict,
    output_dir: str,
    style_key: str,
    mode: str = "separator",
):
    """渲染单张卡片（不分页模式）"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 1440 * 3})

        try:
            if metadata.get("title"):
                print("  📷 生成封面...")
                cover_html = generate_cover_html_v2(metadata, style_key)
                cover_path = os.path.join(output_dir, "cover.png")
                await render_html_to_image(cover_html, cover_path, 1080, 1440, mode)

            print("  📷 生成内容卡片...")
            card_html = generate_card_html_v2(content, 1, 1, style_key, mode)
            card_path = os.path.join(output_dir, "card_1.png")

            await set_content_resilient(page, card_html)
            await page.wait_for_timeout(1500)

            actual_height = await page.evaluate("() => document.body.scrollHeight")

            # 动态高度模式：根据实际内容高度调整截图高度
            if mode == "dynamic":
                screenshot_height = max(800, min(1440, actual_height))
            else:
                screenshot_height = actual_height

            await page.screenshot(
                path=card_path,
                clip={"x": 0, "y": 0, "width": 1080, "height": screenshot_height},
                type="png",
            )
            print(f"  ✅ 已生成：{card_path} ({screenshot_height}px)")
        finally:
            await browser.close()

    print(f"\n✨ 渲染完成！保存到：{output_dir}")


async def render_fixed_card(
    parsed: dict,
    output_dir: str,
    style_key: str,
    generator,
    label: str,
):
    """渲染单张固定 1080×1440 版式卡片，输出 card_1.png（ranking 等单卡版式共用）

    generator: (parsed, style_key) -> HTML 的版式生成函数
    """
    print(f"\n🎨 {label}渲染")
    print(f"🎨 使用样式：{THEMES[style_key]['name']}")
    print(f"  📄 解析到 {len(parsed['items'])} 个条目")

    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        try:
            html = generator(parsed, style_key)
            card_path = os.path.join(output_dir, "card_1.png")
            # 检测缩到最小字号仍放不下的单行文本（已被省略号截断）
            truncation_js = """() => {
                const out = [];
                document.querySelectorAll('.rank-desc').forEach(el => {
                    if (el.scrollWidth > el.clientWidth) {
                        out.push(el.textContent.trim());
                    }
                });
                return out;
            }"""
            truncated = await render_html_to_image(
                html, card_path, 1080, 1440, post_measure_js=truncation_js
            )
            if truncated:
                preview = "；".join(t[:18] for t in truncated)
                print(
                    f"  ⚠️ {len(truncated)} 条介绍超宽且缩至最小字号仍放不下，"
                    f"已用省略号截断（建议缩短文案）：{preview}"
                )
        finally:
            await browser.close()

    print(f"\n✨ 渲染完成！保存到：{output_dir}")


async def render_markdown_to_cards_common(
    card_contents: List[str],
    metadata: dict,
    output_dir: str,
    style_key: str,
    mode: str = "separator",
):
    """通用渲染逻辑

    Args:
        card_contents: 卡片内容列表
        metadata: 元数据
        output_dir: 输出目录
        style_key: 样式键
        mode: 分页模式 - 'separator'(固定高度), 'auto-split'(智能分页), 'dynamic'(动态高度)
    """
    print(f"\n🎨 开始渲染")
    print(f"🎨 使用样式：{THEMES[style_key]['name']}")
    print(f"🎨 分页模式：{mode}")

    os.makedirs(output_dir, exist_ok=True)

    print(f"  📄 检测到 {len(card_contents)} 个内容块")

    # auto-split 模式：智能分页
    if mode == "auto-split":
        print("  🔍 分析内容高度并智能分页...")
        # 合并所有内容块，然后按实际渲染高度切分
        full_body = "\n\n".join(card_contents)
        processed_cards = await auto_split_content(
            full_body, style_key, CARD_WIDTH, CARD_HEIGHT
        )
    else:
        processed_cards = card_contents

    total_cards = len(processed_cards)
    print(f"  📄 将生成 {total_cards} 张卡片")

    if metadata.get("emoji") or metadata.get("title"):
        print("  📷 生成封面...")
        cover_html = generate_cover_html_v2(metadata, style_key)
        cover_path = os.path.join(output_dir, "cover.png")
        await render_html_to_image(cover_html, cover_path, mode=mode)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 1440})

        try:
            for i, content in enumerate(processed_cards, 1):
                print(f"  📷 生成卡片 {i}/{total_cards}...")
                card_html = generate_card_html_v2(
                    content, i, total_cards, style_key, mode
                )
                card_path = os.path.join(output_dir, f"card_{i}.png")

                await page.set_content(card_html, wait_until="networkidle")
                await page.wait_for_timeout(1500)

                # 测量实际内容高度（不受 min-height 影响）
                content_height = await page.evaluate("""() => {
                    const content = document.querySelector('.card-content');
                    return content ? content.scrollHeight : document.body.scrollHeight;
                }""")

                # 内容区域可用高度（去除 padding）
                available_height = CARD_HEIGHT - 220

                # 计算填充率（基于实际内容高度）
                fill_ratio = max(0, content_height) / available_height

                # 统一使用固定高度 1440px
                screenshot_height = CARD_HEIGHT

                await page.screenshot(
                    path=card_path,
                    clip={"x": 0, "y": 0, "width": 1080, "height": screenshot_height},
                    type="png",
                )
                print(
                    f"  ✅ 已生成：{card_path} ({screenshot_height}px, 填充率: {fill_ratio:.0%})"
                )
        finally:
            await browser.close()

    print(f"\n✨ 渲染完成！共生成 {total_cards} 张卡片，保存到：{output_dir}")
    return total_cards


async def render_markdown_to_cards(
    md_file: str, output_dir: str, style_key: str = "academic", mode: str = "separator"
):
    """主渲染函数：将 Markdown 文件渲染为多张卡片图片"""
    print(f"\n🎨 开始渲染：{md_file}")
    print(f"🎨 使用样式：{THEMES[style_key]['name']}")
    print(f"🎨 分页模式：{mode}")

    os.makedirs(output_dir, exist_ok=True)

    data = parse_markdown_file(md_file)
    metadata = data["metadata"]
    body = data["body"]

    card_contents = split_content_by_separator(body)

    await render_markdown_to_cards_common(
        card_contents, metadata, output_dir, style_key, mode
    )


def list_styles():
    """列出所有可用样式"""
    print("\n📋 可用样式列表：")
    print("-" * 40)
    for key, style in THEMES.items():
        print(f"  {key:12} - {style['name']}")
        if style.get("signature"):
            print(f"  {'':12}   签名：{style['signature']}")
    print("-" * 40)


def main():
    parser = argparse.ArgumentParser(
        description="将 Markdown 文件渲染为小红书风格的图片卡片（智能分页版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  uv run --no-sync python scripts/render_xhs.py note.md
  uv run --no-sync python scripts/render_xhs.py note.md -o ./output -s warm-cream
  uv run --no-sync python scripts/render_xhs.py --content "这里是笔记内容" --title "我的标题"
  uv run --no-sync python scripts/render_xhs.py --content "内容" --no-paginate
  uv run --no-sync python scripts/render_xhs.py --list-styles
        """,
    )
    parser.add_argument("markdown_file", nargs="?", help="Markdown 文件路径")
    parser.add_argument(
        "--output-dir", "-o", default=os.getcwd(), help="输出目录（默认为当前工作目录）"
    )
    parser.add_argument(
        "--style",
        "-s",
        default="academic",
        choices=sorted(THEMES.keys()),
        help="样式主题（默认：academic，可选值见 --list-styles）",
    )
    parser.add_argument("--list-styles", action="store_true", help="列出所有可用样式")
    parser.add_argument("--content", "-c", help="直接传入笔记内容字符串")
    parser.add_argument("--title", "-t", help="指定笔记标题")
    parser.add_argument("--subtitle", default="", help="指定笔记副标题")
    parser.add_argument(
        "--emoji", "-e", default="", help="指定封面 Emoji（空则不显示）"
    )
    parser.add_argument(
        "--no-paginate", action="store_true", help="禁用自动分页，保持内容完整性"
    )
    parser.add_argument(
        "--mode",
        "-m",
        default="separator",
        choices=["separator", "auto-split", "auto-fit", "dynamic"],
        help="分页模式: separator(按分隔符), auto-split(智能分页), auto-fit(固定尺寸), dynamic(动态高度)",
    )
    parser.add_argument(
        "--layout",
        "-l",
        default="default",
        choices=["default", "ranking"],
        help="卡片版式: default(全要素图文), ranking(排行榜单)",
    )

    args = parser.parse_args()

    if args.list_styles:
        list_styles()
        return

    if args.layout == "ranking":
        if args.content:
            md_source = args.content
        elif args.markdown_file:
            if not os.path.exists(args.markdown_file):
                print(f"❌ 错误：文件不存在 - {args.markdown_file}")
                sys.exit(1)
            with open(args.markdown_file, "r", encoding="utf-8") as f:
                md_source = f.read()
        else:
            print(f"❌ 错误：{args.layout} 版式需要 Markdown 文件或 --content")
            sys.exit(1)

        parsed = parse_ranking_content(md_source)

        if args.title:
            parsed["title"] = args.title
        if not parsed["items"]:
            print("❌ 错误：未解析到任何条目，请检查输入格式（见 SKILL.md 版式说明）")
            sys.exit(1)

        asyncio.run(
            render_fixed_card(
                parsed,
                args.output_dir,
                args.style,
                generate_ranking_card_html_v2,
                "榜单版式",
            )
        )
        return

    if args.content:
        metadata = {
            "title": args.title or "笔记",
            "subtitle": args.subtitle,
            "emoji": args.emoji,
        }
        card_contents = (
            [args.content]
            if args.no_paginate
            else split_content_by_separator(args.content)
        )
        render_content_to_cards(
            card_contents,
            metadata,
            args.output_dir,
            args.style,
            args.no_paginate,
            args.mode,
        )
    elif args.markdown_file:
        if not os.path.exists(args.markdown_file):
            print(f"❌ 错误：文件不存在 - {args.markdown_file}")
            sys.exit(1)
        asyncio.run(
            render_markdown_to_cards(
                args.markdown_file, args.output_dir, args.style, args.mode
            )
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
