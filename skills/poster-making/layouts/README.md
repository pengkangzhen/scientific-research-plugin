# 版式样张库（layouts/）

每种卡片版式一张代表样张（默认 academic 主题），用「预览」直接翻看即可判断版式长什么样。**此目录只放样张，版式功能代码在 `scripts/render_xhs.py`。**

| 目录 | 版式（`--layout`） | 样张内容 | 输入示例 |
|---|---|---|---|
| `default/` | `default` 全要素图文 | 封面 + 正文首页（完整 Markdown，多页） | `demos/content.md` |
| `ranking/` | `ranking` 榜单 | 马卡龙色排行榜，单张卡 | `demos/content_ranking.md` |

## 更新样张

改了版式代码或想换主题重渲时：

```bash
cd ~/.agents/skills/redbook-publish
uv run --no-sync python scripts/render_xhs.py demos/content.md -o layouts/default -m separator
uv run --no-sync python scripts/render_xhs.py demos/content_ranking.md --layout ranking -o layouts/ranking

# 换主题看另一套配色（加 -s warm-cream；多出的旧图先删再渲）
```

> `default` 会产出 `cover.png` + 多张 `card_N.png`，样张库只保留 `cover.png` 和 `card_1.png` 作代表，多余的分页卡渲完删掉即可。
