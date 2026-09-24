# data/ — term-audit 种子数据（外部事实源，勿手改）

两个词表均为外部公开数据，本目录只做分发缓存；更新时替换文件并在下表登记来源与版本。

| 文件 | 来源 | 许可证 | 用途 |
|---|---|---|---|
| `excess_words.csv` | [berenslab/llm-excess-vocab](https://github.com/berenslab/llm-excess-vocab) `results/excess_words.csv`（Kobak et al., *Science Advances* 2025 的 900 个超额词，含 content/style 标注与词性） | MIT | 单词级 AI 味黑名单（style 子集为默认侧道） |
| `common_words_10k.txt` | [first20hours/google-10000-english](https://github.com/first20hours/google-10000-english) `google-10000-english-no-swears.txt` | MIT | 通用高频英文词表，计算候选术语的「日常词拼接比」 |

列格式：

- `excess_words.csv`：`序号,word,type(content|style),part_of_speech,comment`——脚本读取 word/type 两列。
- `common_words_10k.txt`：一行一词，按频率降序。
