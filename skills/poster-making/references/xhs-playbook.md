# Xiaohongshu (RedBook) Playbook — poster-making 的 xhs 子管线操作手册

本文是 `poster-making` 技能中小红书卡片产线的完整操作手册（中文平台，中文写作方法论，故以中文书写）。
覆盖：创作模式、渲染命令与参数、版式文案契约、创作指南、主题系统、发布流程。
SKILL.md §4.5 是本产线的路由入口；**版式文案契约一节是契约的唯一事实源**。

---

## 两种工作模式

**模式一：用户已提供完整内容 → 原样渲染**

- 直接使用用户提供的原始 Markdown，**不改写、不增删、不调整任何文字**
- 用户交了完整稿子 = 创作权在用户，本管线只负责视觉呈现
- 不创建中间文件，直接渲染原稿

**模式二：用户只给主题/素材 → 创作 + 渲染一体**

按「创作指南」写稿 → 对照「版式文案契约」自检 → 渲染 → 有 ⚠️ 警告则改稿重渲。
警告意味着内容问题，回稿子改，不动渲染代码、不放任截断上线。

## 首次使用

```bash
cd <poster-making 技能目录>
uv sync
# 首次运行需安装 Chromium；网络受限时可设置镜像：
# PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
uv run --no-sync playwright install chromium
```

环境依赖记录在 `pyproject.toml`、锁定于 `uv.lock`（uv 是 Python 包管理器，负责可复现环境）。

## 渲染

```bash
cd <poster-making 技能目录>

# 渲染卡片（自动分页，推荐）
uv run --no-sync python scripts/render_xhs.py /path/to/your/note.md -o ./xhs_cards/{topic_slug}/ -m auto-split
```

**输出：** 自动生成的封面 `cover.png` + 正文卡片 `card_1.png`、`card_2.png`…

**输出目录：** `-o` 相对当前工作目录解析（缺省即当前工作目录）。始终输出到调用方的工作目录下（如 `./xhs_cards/{topic_slug}/`），不要写进技能目录。

### 渲染参数

| 参数 | 简写 | 说明 | 默认值 |
|---|---|---|---|
| `--output-dir` | `-o` | 输出目录 | 当前工作目录 |
| `--style` | `-s` | 主题（可选值见 `--list-styles`） | `academic` |
| `--mode` | `-m` | 分页模式 | `separator` |
| `--layout` | `-l` | 卡片版式：`default` / `ranking` | `default` |
| `--content` | `-c` | 直接传入笔记内容字符串 | - |
| `--title` | `-t` | 指定笔记标题 | - |
| `--subtitle` | | 指定笔记副标题 | 空 |
| `--emoji` | `-e` | 封面 Emoji（空则不显示） | 空 |
| `--no-paginate` | | 禁用分页，内容保持完整 | 关 |
| `--list-styles` | | 列出全部主题 | - |

### 分页模式（`--mode` / `-m`）

| 模式 | 说明 | 推荐场景 |
|------|------|----------|
| `separator` | 按 `---` 手动分页 | 内容已排版好 |
| `auto-split` | 按高度自动切分 | 长文拆分（推荐） |
| `auto-fit` | 固定高度整页渲染（当前行为与 `separator` 一致） | 短内容 |
| `dynamic` | 按内容动态收缩图片高度 | 短内容 |

## 卡片版式

`--layout` / `-l` 选择版式（主题照常生效，配色字体跟随 `-s`）：

- `default` **全要素图文**（默认）：完整 Markdown 渲染（段落、嵌套列表、代码块、表格、公式…），支持全部分页模式
- `ranking` **榜单版式**：单张卡片 = 页眉（品牌块+手写体标语）+ 笔刷高亮大标题 + 副标题 + 马卡龙色排行榜（序号徽章、第 1 名皇冠、emoji 图标、标题+介绍+标签胶囊、右侧数值）+ 手写体页脚。输入格式：

  ```markdown
  ---
  brand: skills.sh
  brand_sub: "Build with Skills\nBuild a Better You."
  slogan: "让 AI 更懂你，\n从一个好用的 Skill 开始！"
  tip: "小提示寄语…（YAML 五个装饰字段全部可选，\\n 换行）"
  corner: "More Skills\nA More Capable You."
  ---
  # 世界下载量最高的 ==10== 个 Skill

  > 按 skills.sh 累计安装量排序 ｜ 数据更新：2026.09.17

  1. 🔍 条目标题｜一句话介绍｜340万+ 次安装｜#标签1 #标签2 #标签3
  ```

  条目按 `｜` 切四段：标题（可带开头 emoji 作图标）／介绍／数值（空格前主数值后单位）／标签；介绍段之后均可省略。标题与页脚支持 `==文本==` 笔刷高亮语法。马卡龙色板为版式自带（与主题无关），3~10 条自适应行距。

各版式的成品样张在 `layouts/`（每版式一张代表图，改版式后重渲更新，见其 README）。

## 版式文案契约

创作（模式二）时按下表写稿；校验用户来稿（模式一）时只提示不修改。渲染器按此实现，**本节是契约的唯一事实源**。

| 维度 | 契约 | 超限后果 |
|---|---|---|
| 发布标题（`-t`） | ≤20 字（按 UTF-16 码元，emoji 占 2） | 发布脚本硬校验，直接报错 |
| ranking 条目 | 3~10 条；条目标题 ≤20 字；介绍 ≤32 字（单行显示） | 介绍超宽自动缩字号，仍超则省略号截断 |
| ranking 标签 | 每条 ≤3 个、每个 ≤6 字 | 过多挤压标题行宽 |
| ranking 数值 | 「主数值 单位」空格分隔（如「340万+ 次安装」） | 无空格则只显示主数值 |
| default 版式 | 无硬契约，任意 Markdown | - |

## 创作指南（模式二）

写小红书不是写论文，所有句子为「滑到停下来」设计：

1. **先定选题和版式**：盘点、榜单、清单类内容 → `ranking`；教程、深度解读、含代码/公式的笔记 → `default` 多页
2. **标题**：具体数字 + 利益点或悬念（「高效写作的 4 个方法」优于「谈谈写作效率」）；同时满足发布标题 ≤20 字
3. **清单体条目**：条目标题动词开头或结论先行，每条只说一件事；介绍是一句话，不是一段话——写完数字数，超 32 字就砍
4. **语气**：第二人称、短句、口语；术语第一次出现用大白话解释；不用「综上所述」式论文腔
5. **标签**（default 版式）：文末一行 `#标签1 #标签2`，3~6 个，渲染脚本自动识别为标签栏
6. **封面**：`---` YAML 头给 `title` / `subtitle` / `emoji`，emoji 一枚点睛即可

## 创作工作流（模式二）

```text
定选题与版式 → 按契约写稿 → 对照契约表自检 → 渲染 → 处理 ⚠️ 警告（改稿重渲）→ 交付
```

渲染日志的 `⚠️` 警告（介绍被截断等）= 稿子不合格，改稿后重渲；不修改渲染代码来迁就内容，也不发布带截断的卡片。

## 卡片主题

主题定义外置于 `assets/themes/themes.yaml`（唯一事实源），用 `--list-styles` 查看：

- `academic` **学术极简**（默认）：白底 + 蓝色强调 `#2563eb`，适合学术论文笔记
- `warm-cream` **暖奶油**：暖白底 + 橙色强调 `#ea580c`，适合生活方式/科普笔记

新增主题：在 `themes.yaml` 加条目并在 `assets/themes/` 下建同名 CSS，CSS 颜色值须取自清单字段（或其明度变体）。设计体系详见同目录 `DESIGN_GUIDE.md`。

## 图片规格

- 尺寸：1080×1440px（3:4 比例，硬编码于 `scripts/render_xhs.py`，不进 `assets/specs.json`——该文件只管海报/GA/社媒卡的出版规格）
- 封面：标题 + 副标题 + Emoji 装饰
- 正文：标题、段落、嵌套列表、引用、代码块（Pygments 高亮）、表格、标签、LaTeX 公式

### ⚠️ LaTeX 公式的网络依赖

公式渲染依赖在线资源，**离线或被墙环境下公式会渲染为原始 LaTeX 文本**（其余元素不受影响）：

- KaTeX 走 jsdelivr CDN（`scripts/render_xhs.py` 内 katex.min.js / auto-render）
- 中文字体走 Google Fonts `@import`（Noto Sans SC）

## 发布到小红书（可选）

渲染完成后可用 `scripts/publish_xhs.py` 发布（登录凭据 `XHS_COOKIE` 存于 `.env`，模板见 `env.example.txt`；`.env` 查找顺序：当前目录 → 技能目录 → 技能上级目录）：

```bash
# 1. 先验证（不做任何网络请求）：标题 ≤20 字、描述 ≤1000 字、图片路径
uv run --no-sync python scripts/publish_xhs.py -t "我的标题" -d "正文内容" -i cover.png card_1.png --dry-run

# 2. 私密试发确认效果
uv run --no-sync python scripts/publish_xhs.py -t "我的标题" -d "正文内容" -i cover.png card_1.png --private

# 3. 正式发布（可选 --post-time "2024-12-01 10:00:00" 定时发布）
uv run --no-sync python scripts/publish_xhs.py -t "我的标题" -d "正文内容" -i cover.png card_1.png
```

- 高频发布会触发平台风控，发布之间保持间隔
- 标题按 UTF-16 码元计 ≤20 字（emoji 占 2），发布脚本硬校验，超限直接报错
- Cookie 失效后需重新登录网页端抓取并更新 `.env`

## 管线资源

- `scripts/render_xhs.py` - 渲染脚本
- `scripts/publish_xhs.py` - 发布脚本
- `assets/themes/themes.yaml` - 主题清单（唯一事实源）
- `assets/themes/*.css` - 主题样式；`assets/themes/DESIGN_GUIDE.md` - 主题设计体系
- `layouts/` - 版式样张库
- `pyproject.toml` / `uv.lock` / `env.example.txt` - uv 环境与凭据模板

上游沿革：本管线源自独立技能 redbook-publish（上游仓库 comeonzhj/Auto-Redbook-Skills，经 09-24 ranking 版式迭代后并入本技能）。
