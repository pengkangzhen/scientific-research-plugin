# Academic Writing Toolkit

OR / ML+OR / 供应链方向的科研全流程技能包：文献获取 → 结构化阅读 → 论文出图 → 写作润色 → 投稿前评审 → 审稿回复。

一份 `skills/` 事实源，多端分发：Claude Code / ZCode 插件、Codex 插件、以及任何支持 `~/.agents/skills` 的助手（经 halter 分发）。

## 科研流水线

| 阶段 | Skill / Agent | 形态 | 一句话 |
|---|---|---|---|
| ① 检索 | `zotero-paper-fetch` | skill | 文献清单 → CrossRef 补全 → Zotero 入库 → 分层下载 PDF（OA 直链 / 仓库反爬 / 校园 VPN 付费墙）|
| ② 阅读 | `zotero-paper-note` | skill | Zotero 条目 → 深度阅读 → 结构化笔记回写 Zotero + `literature.jsonl` |
| ③ 实验 | `figure-plot` | skill | 图契约 → Times New Roman / 色盲安全 → 矢量 PDF 嵌字体验证；数据图 + 示意图 |
| ④ 写作 | `paper-polish` | skill | LaTeX 语言润色，保留全部标记；附术语审计 follow-up |
| ④ 写作 | `jargon-check` | **subagent** | 隔离上下文 + 独立模型的黑话审计——陌生审稿人视角，避免同模型自我盲区 |
| ⑤ 投稿前 | `scientific-review` | skill | 三角色对抗审稿：Reviewer 质疑 → Author 辩护 → Judge 判定 |
| ⑤ 投稿前 | `academic-paper-reviewer` | skill | 五审稿人（EIC + 3 领域审稿 + Devil's Advocate）完整期刊评审模拟 |
| ⑥ 回复 | `rebuttal` | skill | 逐条定位审稿意见 → 修改方案确认 → `\changed{}` 标注 → 编译 PDF → 更新回复信 |

### Skill 与 Subagent 的分界

- **skill**：描述自动触发，主对话内运行——适合流程编排（检索、润色、审稿、回复）。
- **subagent**：显式点名调用，隔离会话——适合需要"局外人视角"的审计（`jargon-check` 的核心价值正在于此：换模型、换上下文，专查写作模型的用词盲区）。

### 两个审稿 skill 的边界

| | `scientific-review` | `academic-paper-reviewer` |
|---|---|---|
| 来源 | 自建 | [academic-research-skills](https://github.com/) 上游，保留原名便于对齐更新 |
| 机制 | Reviewer/Author/Judge 三角色对抗 | 5 审稿人多角色模拟 |
| 定位 | 单维度科学性检查，聚焦 OR/ML+OR | 完整期刊评审流程，跨领域 |
| 重量 | 32K，日常快速 | 336K，投稿前全流程 |

## 安装

### 方式一：插件（Claude Code / ZCode）

```bash
claude plugin install pengkangzhen/academic-writing-toolkit
```

Codex 侧在 `~/.codex/config.toml` 启用：

```toml
[plugins."academic-writing-toolkit@academic-writing-toolkit"]
enabled = true
```

### 方式二：裸装（全部助手通用）

```bash
git clone git@github.com:pengkangzhen/academic-writing-toolkit.git
cd academic-writing-toolkit
./install.sh          # skills/agents -> ~/.agents/{skills,agents}，幂等
halter sync --apply   # 可选：分发到所有已装助手
```

## 目录结构

```
├── skills/                      # 7 个自动触发技能（唯一事实源）
│   ├── zotero-paper-fetch/
│   ├── zotero-paper-note/
│   ├── figure-plot/
│   ├── paper-polish/
│   ├── scientific-review/
│   ├── academic-paper-reviewer/
│   └── rebuttal/
├── agents/
│   └── jargon-check.md          # 隔离审计 subagent
├── .claude-plugin/plugin.json   # Claude Code / ZCode 插件清单
├── .codex-plugin/plugin.json    # Codex 插件清单
├── .agents/plugins/marketplace.json
└── install.sh                   # 裸装回退
```

## 维护约定

- 修改任何 skill 一律改本仓库，`install.sh` 是 symlink——本机即时生效，推送即发布。
- `academic-paper-reviewer` 有上游，重大改动前先对比上游版本；其余 skill 自研自主迭代。
- 本仓库为 v2：v1 只含 4 个写作技能（scientific-review / language-polish / jargon-check / rebuttal）；v2 扩展为科研全流程 7 skill + 1 subagent，并将 `language-polish` 演进更名为 `paper-polish`（含术语审计段）。

## License

MIT
