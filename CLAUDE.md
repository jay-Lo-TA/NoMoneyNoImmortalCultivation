# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this repository.

## 仓库性质

这是一个 **Obsidian 知识库**（中文 Markdown 语料），用于把熊狼狗的网络小说《没钱修什么仙？》前 200 章改编为 26 集 × 15 分钟的 TV 半年番。仓库本身只装语料，不装程序——没有 `package.json` / `requirements.txt` / 构建步骤 / 测试套件。所有内容按 Obsidian 规范管理（双链、frontmatter、标签、MOC）。

## Obsidian 环境

- **社区插件**：仅 `obsidian-git`（已启用，`.obsidian/plugins/obsidian-git/`）
- **核心插件启用**（来自 `.obsidian/core-plugins.json`）：`file-explorer` `global-search` `switcher` `graph` `backlink` `canvas` `outgoing-link` `tag-pane` `properties` `page-preview` `daily-notes` `templates` `note-composer` `command-palette` `editor-status` `bookmarks` `outline` `word-count` `file-recovery` `sync` `bases`
- **未启用**：`markdown-importer` `zk-prefixer` `random-note` `slides` `audio-recorder` `publish` `webviewer`
- **未配置项**：`app.json` 为空；尚未建立 `templates/` 目录；`daily-notes` 已启用但未见每日笔记目录
- **配置目录**：`.obsidian/`（含 `app.json` `appearance.json` `core-plugins.json` `community-plugins.json` `workspace.json` `graph.json` 与 `plugins/`）。改配置时改这里，不要手改 `obsidian-git` 之外的插件目录

## 角色

我是**导演**，与作者（你）协作推进改编。常规工作：章节摘要校对、事实纠错、角色/招数/场景卡细化、26 集分集大纲、CG 资产清单、美术风格、风险红线，并维护 `00-质检清单.md` `90-TODO.md` 状态。事实性内容以 `30-剧情/章节原文/` 为准，与摘要冲突时回原文核对。

## 10 大分区（编号即目录前缀）

| 编号 | 分区 | 入口 |
|---|---|---|
| `00-` | 项目元文档 | `00-MOC总览.md`（总入口，必读）→ `00-项目立项书.md` → `00-番剧制作总览.md` → `00-质检清单.md` |
| `10-` | 世界观 | `10-核心设定.md` + `招数/` 67+ 张 |
| `20-` | 角色 | `主角/` `师承/` `反派/` `同学/` `配角/` + `配角图鉴.md` |
| `30-` | 剧情 | `30-时间线.md` `30-关键冲突.md` `30-人物弧光.md` + `章节摘要/` 200 + `章节原文/` 200 |
| `40-` | 场景 | `00-场景去重表.md`（主索引 1407 行）+ `通用/` 114 + `第NNN章/` 单章目录 |
| `50-` | 美术风格 | 视觉风格 / 关键场景 / 服装造型 / 色彩情绪 |
| `60-` | 改编策略 | 番剧结构 / 节奏高潮 / 删改增补 / 风险红线 |
| `70-` | CG 资产 | 角色 / 场景 / 特效 / 动捕 4 类 |
| `80-` | 参考资料 | 原文链接 / 百度百科摘要 |
| `90-` | 进度追踪 | `90-TODO.md` + 维护脚本 |

## Obsidian 规范

**语言**：全简体中文（正文 / 文件名 / frontmatter / 链接）。

**YAML frontmatter**（`properties` 核心插件读取）：每篇顶部一块。常用字段：
- 通用：`title` `type` `work`（恒为 `没钱修什么仙-番剧制作`）`tags` `priority`（`P0`–`P3`）`created` `modified` `status`（`skeleton` / `filled` / `active`）
- 招数卡专有：`chapter_appearances` `first_appearance` `category` `cultivation_level_required` `source_work`
- 章节摘要专有：`chapter_number` `chapter_title` `main_characters` `key_events` `cg_scenes`
- 场景卡专有：`scene_id` `location` `time` `characters` `cg_priority`

**双链（`backlink` + `outgoing-link` + `graph` 联动）**：`[[...]]` 用相对路径，例如 `[[20-角色/主角/张羽]]` `[[10-世界观/10-核心设定]]` `[[30-剧情/章节摘要/第001章-面试]]`。路径必须与实际文件一致。`graph.json` 已存在，反向链接视图由 Obsidian 自动生成。

**标签**：使用 `tags: [一级, 二级, 状态]` 数组形式（如 `[角色, 主角, P0]`）。常用标签族：`MOC` / `索引` / `世界观` / `角色` / `招数` / `场景` / `剧情` / `CG` / `质检` / `TODO`。`tag-pane` 核心插件提供面板视图。

**MOC（Map of Content）**：`00-MOC总览.md` 是仓库总 MOC。各分区可视需要有自己的子 MOC（如 `20-角色/配角图鉴.md` 充当配角 MOC）。MOC 文档不写新内容，只做导航。

**Canvas**：核心插件已启用但暂未见 `.canvas` 文件。如要做关系图/时间线可视化可新建。

**Bases**：核心插件已启用（Obsidian 1.9+ 特性）。适合做结构化数据视图（招数索引、角色矩阵、CG 资产清单）。`10-世界观/招数/00-第26-50章招数索引.md` 是手写索引，可考虑迁移到 `.base` 文件。

**Note Composer**（已启用）：支持把多篇 md 合并 / 拆分。章节摘要与原文之间如需重组可走此插件。

**Templates**（已启用）：当前无 `templates/` 目录。如建立模板，建议放 `_templates/`（带下划线前缀不参与索引）或 `.obsidian/Templates/`。建议模板：招数卡 / 角色卡 / 场景卡 / 章节摘要。

## 命名与状态

- 章节：`第NNN章-标题.md`（3 位补零），如 `第001章-面试.md`
- 招数：`招数-NN-名称.md`（2 位补零），如 `招数-01-周天采气法.md`
- 场景：`SC-NNN-NN` ID 格式
- 状态流转：`skeleton`（占位骨架，不可信）→ `filled`（已填充）→ `active`（维护中）

## 关键事实校正（2026-06-17 已修，勿再写错）

- ch070 隐藏灵根主角 = **白真真**（非张羽）
- ch086 张羽 / 白真真 **未**被移植仿妖筋肉（被移植：赵天行 / 何大有 / 双幽朋）
- ch195 三大神药 = **道解缓释胶囊 / 法力脉络针剂 / 仿凤功能素**（非浑元丹 / 玄冥重水 / 圣体丹）
- ch202 "最完美的高中生肉体" = **夜凌霄**（非张羽，绿洲集团评）

详细见 `00-质检清单.md` "A2 重写阶段" 与 "项目最终战果"。

## 26 集关键节点（速查）

完整表见 `00-番剧制作总览.md` "26 集分集映射"。三个最关键节点：
- **第 13 集（季终钩子）**：ch49-50，无极云手 + 黑影 ⭐
- **第 26 集（结局）**：ch196-202，玄冥重水 + 筑基
- **P0 必做场景**：面试教室、邪神契约、羽书显化、10 级周天采气、飞剑、玉星寒首登场（ch88）、真灵根神经滋养（ch99-100）、玉星寒传授省钱（ch132）、妙云首登场（ch135）、辱蓝岭（ch150）、筑基决战（ch200）

## 维护脚本

`90-进度追踪/_fix_*.py` `_fix_*.ps1` 是 2026-06 多轮清理的产物（角色链修复、章节链修复等），是历史脚本。重跑前必须先读懂逻辑——很多是一次性修复，对应问题可能已解决。

## git 与 Obsidian

- 已启用 `obsidian-git` 插件（自动同步配置在 `.obsidian/plugins/obsidian-git/data.json`，如有）
- `.obsidian/workspace.json` 经常因窗口状态变化，不要人肉编辑，让 Obsidian 自动维护
- `graph.json` 同理
- 仓库根的 `README.md` 是占位（"hhhh"），不需维护
