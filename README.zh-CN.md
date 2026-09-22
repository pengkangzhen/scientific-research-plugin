# Scientific Research Plugin

[English](README.md) | **简体中文**

任何任务都是一次科学研究，论文只是最完整的实例。`research-before-build` 纪律层把先例调研带到一切项目；论文管线——文献获取 → 结构化阅读 → 论文出图 → 写作润色 → 投稿前评审 → 审稿回复 → 会议汇报——是它的完整落地。面向 OR / ML+OR / 供应链研究者。

一份 `skills/` 事实源，多端分发：Claude Code / ZCode 插件、Codex 插件、以及任何支持 `~/.agents/skills` 的助手（经 halter 分发）。

## 科研流水线

| 阶段 | Skill / Agent | 形态 | 一句话 |
|---|---|---|---|
| ⓪ 调研 | `research-before-build` | skill | 纪律层，适用于**任何**非琐碎任务：L0–L3 分级触发，动手前先查人类先例（官方文档 / 成熟开源 / GitHub issues / 文献）；决定"是否调研、调研什么" |
| ① 检索 | `zotero-paper-fetch` | skill | 文献清单 → CrossRef 补全 → Zotero 入库 → 分层下载 PDF（OA 直链 / 仓库反爬 / 校园 VPN 付费墙）|
| ② 阅读 | `zotero-paper-note` | skill | Zotero 条目 → 深度阅读 → 结构化笔记回写 Zotero + `literature.jsonl` |
| ③ 实验 | `figure-plot` | skill | 图契约 → Times New Roman / 色盲安全 → 矢量 PDF 嵌字体验证；数据图 + 示意图 |
| ④ 写作 | `paper-polish` | skill | LaTeX 语言润色，保留全部标记；附术语审计 follow-up |
| ④ 写作 | `jargon-check` | **subagent** | 隔离上下文 + 独立模型的黑话审计——陌生审稿人视角，避免同模型自我盲区 |
| ⑤ 投稿前 | `paper-review` | skill | 三角色对抗审稿：Reviewer 质疑 → Author 辩护 → Judge 判定 |
| ⑤ 投稿前 | `academic-paper-reviewer` | skill | 五审稿人（EIC + 3 领域审稿 + Devil's Advocate）完整期刊评审模拟 |
| ⑥ 回复 | `rebuttal` | skill | 逐条定位审稿意见 → 修改方案确认 → `\changed{}` 标注 → 编译 PDF → 更新回复信 |
| ⑦ 汇报 | `academic-ppt` | skill | 论文（LaTeX/PDF）→ Beamer + 视觉设计系统（官方模板提取或自建）→ 按时长写讲稿 → 合规 pptx 包装与演讲者备注 |

### 纪律层与管线层

- **纪律层（⓪）**：`research-before-build` 作用于任何非琐碎任务——写代码、部署、架构选型皆然，不限于论文。它是整个技能包的世界观：动手前先查先例、按风险分级检索、按信任层级采信、以决策影响验收。
- **管线层（①–⑦）**：论文生命周期，是这套纪律最完整的实例化——从一份参考文献清单到会议演讲。

⓪ → ① 是上下游而非包含：`research-before-build` 决定"是否调研、调研什么"；`zotero-paper-fetch` 把确定的文献清单获取入库。

### Skill 与 Subagent 的分界

- **skill**：描述自动触发，主对话内运行——适合流程编排（检索、润色、审稿、回复）。
- **subagent**：显式点名调用，隔离会话——适合需要"局外人视角"的审计（`jargon-check` 的核心价值正在于此：换模型、换上下文，专查写作模型的用词盲区）。

### 两个审稿 skill 的边界

| | `paper-review` | `academic-paper-reviewer` |
|---|---|---|
| 来源 | 自建 | [academic-research-skills](https://github.com/) 上游，保留原名便于对齐更新 |
| 机制 | Reviewer/Author/Judge 三角色对抗 | 5 审稿人多角色模拟 |
| 定位 | 单维度科学性检查，聚焦 OR/ML+OR | 完整期刊评审流程，跨领域 |
| 重量 | 32K，日常快速 | 336K，投稿前全流程 |

## 安装

### 方式一：插件（Claude Code / Codex / ZCode）

Claude Code：

```bash
claude plugin install pengkangzhen/scientific-research-plugin
```

Codex 侧在 `~/.codex/config.toml` 启用：

```toml
[plugins."scientific-research-plugin@scientific-research-plugin"]
enabled = true
```

ZCode——本仓库自带插件市场清单（`.claude-plugin/marketplace.json`，source 解析到仓库根）：

1. 克隆仓库到本地，取其根目录路径。
2. 插件市场 → 添加 → 添加插件市场，粘贴仓库根目录。
3. 个人 → scientific-research-plugin → 科研流水线插件 → 安装。

`jargon-check` subagent 不随 ZCode 插件包分发（ZCode 插件清单目前只声明 skills / commands / hooks / MCP servers，不含 subagent）——需要时执行 `./install.sh` 安装。

### 方式二：裸装（全部助手通用）

```bash
git clone https://github.com/pengkangzhen/scientific-research-plugin.git
cd scientific-research-plugin
./install.sh          # skills/agents -> ~/.agents/{skills,agents}，幂等
halter sync --apply   # 可选：分发到所有已装助手
```

## 目录结构

```
├── skills/                      # 9 个自动触发技能（唯一事实源）
│   ├── research-before-build/
│   ├── zotero-paper-fetch/
│   ├── zotero-paper-note/
│   ├── figure-plot/
│   ├── paper-polish/
│   ├── paper-review/
│   ├── academic-paper-reviewer/
│   ├── rebuttal/
│   └── academic-ppt/
├── agents/
│   └── jargon-check.md          # 隔离审计 subagent
├── .claude-plugin/
│   ├── plugin.json              # Claude Code 插件清单
│   └── marketplace.json         # Claude Code / ZCode 市场清单（source 指向仓库根）
├── .zcode-plugin/plugin.json    # ZCode 插件清单
├── .codex-plugin/plugin.json    # Codex 插件清单
├── .agents/plugins/marketplace.json  # Codex（~/.agents）市场清单
└── install.sh                   # 裸装回退
```

## 维护约定

- 修改任何 skill 一律改本仓库，`install.sh` 是 symlink——本机即时生效，推送即发布。
- 版本号变更需同步四处并保持一致：三个插件清单（`.claude-plugin/`、`.zcode-plugin/`、`.codex-plugin/`）与 `.claude-plugin/marketplace.json` 条目。
- `academic-paper-reviewer` 有上游，重大改动前先对比上游版本；其余 skill 自研自主迭代。
- 本仓库为 v3：v1 只含 4 个写作技能（scientific-review / language-polish / jargon-check / rebuttal）；v2 扩展为科研全流程 7 skill + 1 subagent，并将 `language-polish` 演进更名为 `paper-polish`（含术语审计段）；v3 加入纪律层 `research-before-build`（⓪）与汇报层 `academic-ppt`（⑦），并将 `scientific-review` 更名为 `paper-review`——共 9 skill + 1 subagent，定位从「论文工具包」升级为「一切任务皆科学研究」。

## License

MIT
