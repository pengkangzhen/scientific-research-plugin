#!/usr/bin/env python3
"""
小红书笔记发布脚本

使用方法:
    uv run --no-sync python scripts/publish_xhs.py --title "标题" --desc "描述" --images cover.png card_1.png

环境变量:
    在同目录或项目根目录下创建 .env 文件，配置：

    # 必需：小红书 Cookie
    XHS_COOKIE=your_cookie_string_here
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List

try:
    from dotenv import load_dotenv
except ImportError as e:
    print(f"缺少依赖: {e}")
    print("请运行: uv sync")
    sys.exit(1)


def utf16_code_units(text: str) -> int:
    """UTF-16 码元数：平台按 JS 字符串长度校验，emoji 等增补平面字符占 2 个码元"""
    return len(text.encode("utf-16-le")) // 2


def load_cookie() -> str:
    """从 .env 文件加载 Cookie"""
    # 尝试从多个位置加载 .env
    env_paths = [
        Path.cwd() / ".env",
        Path(__file__).parent.parent / ".env",
        Path(__file__).parent.parent.parent / ".env",
    ]

    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break

    cookie = os.getenv("XHS_COOKIE")
    if not cookie:
        print("❌ 错误: 未找到 XHS_COOKIE 环境变量")
        print("请创建 .env 文件，添加以下内容：")
        print("XHS_COOKIE=your_cookie_string_here")
        print("\nCookie 获取方式：")
        print("1. 在浏览器中登录小红书（https://www.xiaohongshu.com）")
        print("2. 打开开发者工具（F12）")
        print("3. 在 Network 标签中查看任意请求的 Cookie 头")
        print("4. 复制完整的 cookie 字符串")
        sys.exit(1)

    return cookie


def parse_cookie(cookie_string: str) -> Dict[str, str]:
    """解析 Cookie 字符串为字典"""
    cookies = {}
    for item in cookie_string.split(";"):
        item = item.strip()
        if "=" in item:
            key, value = item.split("=", 1)
            cookies[key.strip()] = value.strip()
    return cookies


def validate_cookie(cookie_string: str) -> bool:
    """验证 Cookie 是否包含必要的字段"""
    cookies = parse_cookie(cookie_string)

    # 检查必需的 cookie 字段
    required_fields = ["a1", "web_session"]
    missing = [f for f in required_fields if f not in cookies]

    if missing:
        print(f"⚠️ Cookie 可能不完整，缺少字段: {', '.join(missing)}")
        print("这可能导致签名失败，请确保 Cookie 包含 a1 和 web_session 字段")
        return False

    return True


def validate_images(image_paths: List[str]) -> List[str]:
    """验证图片文件是否存在"""
    valid_images = []
    for path in image_paths:
        if os.path.exists(path):
            valid_images.append(os.path.abspath(path))
        else:
            print(f"⚠️ 警告: 图片不存在 - {path}")

    if not valid_images:
        print("❌ 错误: 没有有效的图片文件")
        sys.exit(1)

    return valid_images


def print_error_hints(e: Exception) -> None:
    """按 xhs 库的结构化异常类型输出排查建议"""
    try:
        from xhs.exception import (
            DataFetchError,
            IPBlockError,
            NeedVerifyError,
            SignError,
        )
    except ImportError:
        return

    if isinstance(e, SignError):
        print("\n💡 签名错误排查建议：")
        print("1. 确保 Cookie 包含有效的 a1 和 web_session 字段")
        print("2. Cookie 可能已过期，请重新获取")
    elif isinstance(e, NeedVerifyError):
        print("\n💡 触发平台验证排查建议：")
        print("1. 发布频率可能过高触发风控，请降低频率或延长间隔")
        print("2. 更换网络环境后重试")
    elif isinstance(e, IPBlockError):
        print("\n💡 IP 受限排查建议：")
        print("1. 当前 IP 已被平台限制，更换网络环境后重试")
        print("2. 等待限制解除期间不要重试，避免加重限制")
    elif isinstance(e, DataFetchError):
        print("\n💡 数据请求失败排查建议：")
        print("1. 检查网络连接")
        print("2. Cookie 可能已过期，请重新获取")


class LocalPublisher:
    """本地发布：直接使用 xhs 库本地签名"""

    def __init__(self, cookie: str):
        self.cookie = cookie
        self.client = None

    def init_client(self):
        """初始化 xhs 客户端"""
        try:
            from xhs import XhsClient
            from xhs.help import sign as local_sign
        except ImportError:
            print("❌ 错误: 缺少 xhs 库")
            print("请运行: uv sync")
            sys.exit(1)

        # 解析 a1 值
        cookies = parse_cookie(self.cookie)
        a1 = cookies.get("a1", "")

        # 保存 cookie 中的 a1 值供闭包使用
        cookie_a1 = a1

        def sign_func(uri, data=None, ctime=None, a1="", b1="", **kwargs):
            # 使用 cookie 中的 a1 值（如果传入的 a1 为空则使用 cookie 中的）
            effective_a1 = a1 if a1 else cookie_a1
            return local_sign(uri, data, ctime=ctime, a1=effective_a1, b1=b1)

        self.client = XhsClient(cookie=self.cookie, sign=sign_func)

    def publish(
        self,
        title: str,
        desc: str,
        images: List[str],
        is_private: bool = False,
        post_time: str = None,
    ) -> dict:
        """发布图文笔记"""
        print("\n🚀 准备发布笔记...")
        print(f"  📌 标题: {title}")
        print(f"  📝 描述: {desc[:50]}..." if len(desc) > 50 else f"  📝 描述: {desc}")
        print(f"  🖼️ 图片数量: {len(images)}")

        try:
            result = self.client.create_image_note(
                title=title,
                desc=desc,
                files=images,
                is_private=is_private,
                post_time=post_time,
            )

            print("\n✨ 笔记发布成功！")
            if isinstance(result, dict):
                note_id = result.get("note_id") or result.get("id")
                if note_id:
                    print(f"  📎 笔记ID: {note_id}")
                    print(f"  🔗 链接: https://www.xiaohongshu.com/explore/{note_id}")

            return result

        except Exception as e:
            print(f"\n❌ 发布失败: {e}")
            print_error_hints(e)
            raise


def main():
    parser = argparse.ArgumentParser(
        description="将图片发布为小红书笔记",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 先验证（不做任何网络请求）
  uv run --no-sync python scripts/publish_xhs.py -t "我的标题" -d "正文内容" -i cover.png card_1.png --dry-run

  # 私密试发
  uv run --no-sync python scripts/publish_xhs.py -t "我的标题" -d "正文内容" -i *.png --private

  # 定时发布
  uv run --no-sync python scripts/publish_xhs.py -t "我的标题" -d "正文内容" -i *.png --post-time "2024-12-01 10:00:00"
""",
    )
    parser.add_argument(
        "--title",
        "-t",
        required=True,
        help="笔记标题（不超过 20 字，按 UTF-16 码元计，emoji 占 2）",
    )
    parser.add_argument(
        "--desc",
        "-d",
        default="",
        help="笔记描述/正文内容（不超过 1000 字，按 UTF-16 码元计）",
    )
    parser.add_argument(
        "--images",
        "-i",
        nargs="+",
        required=True,
        help="图片文件路径（可以多个）",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="是否设为私密笔记",
    )
    parser.add_argument(
        "--post-time",
        default=None,
        help="定时发布时间（格式：2024-01-01 12:00:00）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅验证，不实际发布、不做网络请求",
    )

    args = parser.parse_args()

    # 硬校验标题/描述长度（平台按 UTF-16 码元计，emoji 等增补平面字符占 2）
    title_units = utf16_code_units(args.title)
    if title_units > 20:
        print(
            f"❌ 错误: 标题超长（{title_units} 个 UTF-16 码元 > 上限 20，emoji 按 2 码元计），"
            "请缩短标题后重试"
        )
        sys.exit(1)

    desc_units = utf16_code_units(args.desc)
    if desc_units > 1000:
        print(
            f"❌ 错误: 描述超长（{desc_units} 个 UTF-16 码元 > 上限 1000），请缩短描述后重试"
        )
        sys.exit(1)

    # 加载 Cookie
    cookie = load_cookie()

    # 验证 Cookie 格式
    validate_cookie(cookie)

    # 验证图片
    valid_images = validate_images(args.images)

    if args.dry_run:
        print("\n🔍 验证模式 - 不会实际发布")
        print(f"  📌 标题: {args.title}")
        print(f"  📝 描述: {args.desc}")
        print(f"  🖼️ 图片: {valid_images}")
        print(f"  🔒 私密: {args.private}")
        print(f"  ⏰ 定时: {args.post_time or '立即发布'}")
        print("\n✅ 验证通过，可以发布")
        return

    # 初始化客户端并发布
    publisher = LocalPublisher(cookie)
    publisher.init_client()

    try:
        publisher.publish(
            title=args.title,
            desc=args.desc,
            images=valid_images,
            is_private=args.private,
            post_time=args.post_time,
        )
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
