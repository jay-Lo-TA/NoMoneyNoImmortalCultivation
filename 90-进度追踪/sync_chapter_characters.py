#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量同步章节摘要「关联」区域的角色链接。

流程：
  1. 扫描 20-角色/ 建立角色名称路径索引，路径不带 .md 后缀（Obsidian wikilink 格式）
  2. 对 30-剧情/章节摘要/ 下每个摘要文件：
     - 解析「出场角色」板块，提取所有角色路径
     - 解析「关联」板块，提取已有链接
     - 将缺失的角色路径以 - [[path]] 格式追加到关联区末尾
  3. 支持 --dry-run 试运行模式（仅输出 diff，不修改文件）

用法：
  python 90-进度追踪/sync_chapter_characters.py              # 正式执行
  python 90-进度追踪/sync_chapter_characters.py --dry-run    # 试运行
"""

import argparse
import re
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHAR_DIR = PROJECT_ROOT / "20-\u89d2\u8272"
SUMMARY_DIR = PROJECT_ROOT / "30-\u5267\u60c5" / "\u7ae0\u8282\u6458\u8981"


# ---- 角色索引构建 ----

def build_character_index():
    """
    构建角色名称索引。
    路径格式：不带 .md 后缀（Obsidian wikilink 格式）
    
    返回:
      name_index: {显示名称: "20-角色/xxx/xxx"}
      path_index: {文件stem(无扩展名): "20-角色/xxx/xxx"}
    """
    path_index = {}
    name_index = {}

    # 硬编码常用角色显示名称 -> 路径（含子目录）
    special_map = {
        # ====== 主角 ======
        "\u5f20\u7fbd":        "20-\u89d2\u8272/\u4e3b\u89d2/\u5f20\u7fbd",
        "\u767d\u771f\u771f":  "20-\u89d2\u8272/\u4e3b\u89d2/\u767d\u771f\u771f",
        # ====== 反派 ======
        "\u90aa\u795e\u5e03\u5a03\u5a03": "20-\u89d2\u8272/\u53cd\u6d3e/\u90aa\u795e\u5e03\u5a03\u5a03",
        "\u94fe\u67a2\u795e\u541b":       "20-\u89d2\u8272/\u53cd\u6d3e/\u94fe\u67a2\u795e\u541b",
        # ====== 同学 ======
        "\u591c\u661f\u7409":  "20-\u89d2\u8272/\u540c\u5b66/\u591c\u661f\u7409",
        "\u7d20\u4e91\u8679":  "20-\u89d2\u8272/\u540c\u5b66/\u7d20\u4e91\u8679",
        "\u4e91\u8679":        "20-\u89d2\u8272/\u540c\u5b66/\u7d20\u4e91\u8679",
        "\u9053\u4e91\u7424":  "20-\u89d2\u8272/\u540c\u5b66/\u9053\u4e91\u7424",
        # ====== 师承 ======
        "\u8427\u7389\u5bb9":         "20-\u89d2\u8272/\u5e08\u627f/\u8427\u7389\u5bb9-\u78c1\u6781\u795e\u541b",
        "\u78c1\u6781\u795e\u541b":   "20-\u89d2\u8272/\u5e08\u627f/\u8427\u7389\u5bb9-\u78c1\u6781\u795e\u541b",
        "\u9ad8\u5d07\u5149":         "20-\u89d2\u8272/\u5e08\u627f/\u9ad8\u5d07\u5149-\u9752\u6728\u795e\u541b",
        "\u9752\u6728\u795e\u541b":   "20-\u89d2\u8272/\u5e08\u627f/\u9ad8\u5d07\u5149-\u9752\u6728\u795e\u541b",
        # ====== 常见配角 ======
        "\u4e25\u8001\u5e08":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-01-\u4e25\u8001\u5e08",
        "\u96f7\u94a7":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-02-\u96f7\u94a7",
        "\u82cf\u6d77\u5cf0":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-03-\u82cf\u6d77\u5cf0",
        "\u738b\u6d77":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-04-\u738b\u6d77",
        "\u5468\u6f88\u5c18":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-05-\u5468\u6f88\u5c18",
        "\u84dd\u5cad":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-06-\u84dd\u5cad",
        "\u6881\u52e4":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-07-\u6881\u52e4",
        "\u6b66\u9752\u9752":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-08-\u6b66\u9752\u9752",
        "\u91ce\u7ea4\u4e91":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-09-\u91ce\u7ea4\u4e91",
        "\u4e50\u6c90\u5d9a":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-10-\u4e50\u6c90\u5d9a",
        "\u70bc\u5929\u6781":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-11-\u70bc\u5929\u6781",
        "\u5b8b\u6d77\u9f99":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-12-\u5b8b\u6d77\u9f99",
        "\u718a\u4e0d\u51e1":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-13-\u718a\u4e0d\u51e1",
        "\u58a8\u5929\u9038":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-14-\u58a8\u5929\u9038",
        "\u5bd2\u661f\u91ce":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-15-\u5bd2\u661f\u91ce",
        "\u674e\u661f\u5b87":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-16-\u674e\u661f\u5b87",
        "\u5f20\u7fe9\u7fe9":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-20-\u5f20\u7fe9\u7fe9",
        "\u5468\u5929\u7fbf":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-21-\u5468\u5929\u7fbf",
        "\u8d75\u5929\u884c":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-22-\u8d75\u5929\u884c",
        "\u94b1\u6df1":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-23-\u94b1\u6df1",
        "\u5b59\u7532\u4e59":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-24-\u5b59\u7532\u4e59",
        "\u674e\u96ea\u83b2":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-24-\u674e\u96ea\u83b2",
        "\u53cc\u5e7d\u670b":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-25-\u53cc\u5e7d\u670b",
        "\u695a\u627f\u5ba3":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-26-\u695a\u627f\u5ba3",
        "\u695a\u79cb\u6cb3":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-27-\u695a\u79cb\u6cb3",
        "\u864e\u4e91\u6d9b":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-28-\u864e\u4e91\u6d9b",
        "\u718a\u6587\u6b66":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-29-\u718a\u6587\u6b66",
        "\u9b4f\u99a8":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-30-\u9b4f\u99a8",
        "\u4f55\u5927\u6709":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-31-\u4f55\u5927\u6709",
        "\u661f\u706b\u771f\u4eba":    "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-32-\u661f\u706b\u771f\u4eba",
        "\u52a9\u7406\u8001\u5e08":    "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-32-\u52a9\u7406\u8001\u5e08",
        "\u7389\u661f\u5bd2":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-66-\u7389\u661f\u5bd2",
        "\u674e\u52c7":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-67-\u674e\u52c7",
        "\u9093\u4e19\u4e01":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-67-\u9093\u4e19\u4e01-\u9093\u6e38\u795e-\u516d\u7b49\u56db\u65b9\u6e38\u795e\u7b51\u57fa\u8003\u5b98",
        "\u9ec4\u5b50\u4e11":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-68-\u9ec4\u5b50\u4e11-\u4e5d\u7b49\u529f\u66f9\u5c0f\u795e",
        "\u53f6\u6d77\u6843":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-68-\u53f6\u6d77\u6843",
        "\u4e91\u666f":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-69-\u4e91\u666f-\u4ed9\u4e91\u9ad8\u4e2d\u9ad8\u4e8c\u9996\u5e2d-\u6606\u589f\u4e00\u5c42\u6700\u5f3a\u9ad8\u4e2d\u751f",
        "\u591c\u51cc\u9704":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-70-\u591c\u51cc\u9704-\u7eff\u6d32\u96c6\u56e2\u6700\u5b8c\u7f8e\u8089\u4f53\u8840\u8109-\u7ea2\u5305\u7b26\u7ec3\u4e60\u8005",
        "\u6234\u884c\u4e4b":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-71-\u6234\u884c\u4e4b",
        "\u5b89\u5b89":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-72-\u5b89\u5b89-\u5c0f\u718a\u732b-\u7ea2\u5854\u7267\u4e1a\u7e41\u80b2\u57fa\u5730\u6700\u4f73\u5458\u5de5",
        "\u798f\u59ec":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-73-\u798f\u59ec",
        "\u963f\u897f":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-75-\u963f\u897f-\u6697\u5b66\u5e2e",
        "\u90d1\u5728\u660e":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-77-\u90d1\u5728\u660e",
        "\u8521\u5934":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-78-\u8521\u5934-\u6697\u5b66\u5e2e",
        "\u8499\u6d9b":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-79-\u8499\u6d9b-\u4ed9\u90fd\u58ee\u6c49-\u66b4\u98df\u8003\u573a\u9009\u624b",
        "\u53f8\u66b4\u96e8":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-80-\u53f8\u66b4\u96e8-\u5f20\u7fbd\u76d1\u89c6\u8005-\u5468\u5bb6\u5916\u56f4",
        "\u5468\u9633":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-81-\u5468\u9633-\u5468\u5bb6\u5341\u4ee3\u6700\u6770\u51fa-\u950b\u538b\u90aa\u795e\u5931\u53bb\u4e0b\u534a\u8eab",
        "\u8f66\u5973":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-82-\u8f66\u5973-\u6697\u5b66\u5e2e\u6559\u5934-\u8dd1\u8f66\u817f10\u7ea7",
        "\u6bcd\u4eb2":                "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-41-\u6bcd\u4eb2",
        "\u9762\u8bd5\u5b98\u4e09\u4eba":  "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-42-\u5d69\u9633\u9ad8\u4e2d\u9762\u8bd5\u5b98\u4e09\u4eba",
        "\u5d69\u9633\u9ad8\u4e2d\u9762\u8bd5\u5b98\u4e09\u4eba": "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-42-\u5d69\u9633\u9ad8\u4e2d\u9762\u8bd5\u5b98\u4e09\u4eba",
        "\u6cd5\u8d5b\u4e3b\u6301\u4eba":  "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-65-\u6cd5\u8d5b\u4e3b\u6301\u4eba",
        "\u4e50\u666f\u8fb0":          "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-69-\u4e50\u666f\u8fb0",
        "\u795e\u79d8\u7535\u8bdd\u4eba":  "20-\u89d2\u8272/\u914d\u89d2/\u4eba\u7269-63-\u795e\u79d8\u7535\u8bdd\u4eba",
    }
    name_index.update(special_map)

    # 补充扫描 20-角色/ 下的实际文件
    for md_file in CHAR_DIR.rglob("*.md"):
        rel_path = md_file.relative_to(PROJECT_ROOT).as_posix()
        # 跳过非角色文件（索引、模板等）
        skip_markers = ["\u914d\u89d2\u56fe\u9274", "00-\u914d\u89d2\u6863\u6848", "/00-", "\u7269\u7d22\u5f15"]
        if any(m in rel_path for m in skip_markers):
            continue

        # 路径不带 .md 后缀（Obsidian wikilink 格式）
        path_no_ext = rel_path.replace(".md", "")
        stem = md_file.stem
        path_index[stem] = path_no_ext

        # 非配角的 stem 直接作为显示名
        if not rel_path.startswith("20-\u89d2\u8272/\u914d\u89d2/"):
            name_index.setdefault(stem, path_no_ext)
        else:
            # 配角文件：提取纯角色名（如 "严老师" 来自 "人物-01-严老师"）
            m = re.match(r'\u4eba\u7269-\d+-(.+)', stem)
            if m:
                pure_name = m.group(1)
                # 只取第一个"-"之前的部分作为纯名
                pure_name_simple = pure_name.split("-")[0]
                if pure_name_simple not in name_index:
                    name_index[pure_name_simple] = path_no_ext

    return name_index, path_index


# ---- 解析出场角色板块 ----

def extract_character_refs(text, name_index, path_index):
    """从「出场角色」板块文本中提取所有角色路径。

    返回: 完整相对路径的集合（不带 .md 后缀）
    """
    result = set()

    # 1. 提取 [[wikilink]] 中的 20-角色/ 路径
    for wl in re.findall(r'\[\[([^\]]+)\]\]', text):
        wl = wl.strip()
        # 去掉 # 锚点（#heading）和 | 显示名（|display）
        wl_base = wl.split("#")[0].split("|")[0].strip()
        if wl_base.startswith("20-\u89d2\u8272/"):
            result.add(wl_base)
        elif wl_base in name_index:
            result.add(name_index[wl_base])

    # 2. 提取裸路径 20-角色/xxx（排除 []#| 和各类逗号括号）
    for bp in re.findall(r'20-\u89d2\u8272/[^\]\[,#|\s\u3001\uff0c\uff09)]+', text):
        bp = bp.strip()
        # 去掉末尾可能的 
        if bp.endswith('\\') or bp.endswith('\u2014'):
            pass  # keep as is
        # 去除括号内描述
        bp_clean = bp.split("\uff08")[0].split("(")[0]

        if bp_clean in result:
            continue

        if "/\u4eba\u7269-" in bp_clean:
            parts = bp_clean.split("/")
            stem = parts[-1]
            if stem in path_index:
                result.add(path_index[stem])
            elif bp_clean.startswith("20-\u89d2\u8272/"):
                result.add(bp_clean)
        elif bp_clean.startswith("20-\u89d2\u8272/"):
            result.add(bp_clean)

    return result


# ---- 解析关联板块 ----

# 板块标题匹配：支持 ### / ## / # 以及可选 emoji
RE_CHAR_SECTION = re.compile(r'^#{1,3}\s*\U0001f465?\s*\u51fa\u573a\u89d2\u8272\s*$', re.MULTILINE)
RE_LINK_SECTION = re.compile(r'^#{1,3}\s*\U0001f517?\s*\u5173\u8054\s*$', re.MULTILINE)


def get_section(content, title_pattern):
    """提取从标题匹配到下一个同级标题之间的内容"""
    match = title_pattern.search(content)
    if not match:
        return None
    start = match.end()
    next_match = re.search(r'^#{1,3}\s', content[start:], re.MULTILINE)
    end = start + next_match.start() if next_match else len(content)
    return content[start:end]


def extract_existing_links(section_text):
    """从关联区文本中提取所有 20-角色/ 路径（去重）"""
    result = set()
    if not section_text:
        return result

    # [[20-角色/xxx]]（含 #锚点 和 |显示名）
    for link in re.findall(r'\[\[(20-\u89d2\u8272/[^\]]+)\]\]', section_text):
        link = link.strip().split("#")[0].split("|")[0].strip()
        result.add(link.rstrip("\uff09").rstrip(")"))

    # - 20-角色/xxx 或 20-角色/xxx（裸路径）
    for link in re.findall(r'(?:^|\n)\s*-\s*(20-\u89d2\u8272/[^\s\n]+)', section_text):
        link = link.strip().split("#")[0].split("|")[0].strip()
        result.add(link.rstrip("\uff09").rstrip(")"))

    return result


# ---- 核心处理逻辑 ----

def process_summary(summary_path, name_index, path_index, dry_run):
    """处理单个章节摘要文件，补充缺失的角色关联。

    返回: diff 行列表
    """
    diffs = []
    filename = summary_path.name

    try:
        content = summary_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            content = summary_path.read_text(encoding="gbk")
        except Exception as e:
            return [f"[ERR] \u7f16\u7801\u9519\u8bef: {filename} - {e}"]
    except Exception as e:
        return [f"[ERR] \u8bfb\u53d6\u5931\u8d25: {filename} - {e}"]

    # 1) 提取出场角色板块
    char_section = get_section(content, RE_CHAR_SECTION)
    if not char_section:
        diffs.append(f"[SKIP] {filename} --- \u65e0\u300c\u51fa\u573a\u89d2\u8272\u300d\u677f\u5757")
        return diffs

    # 2) 提取角色路径
    char_paths = extract_character_refs(char_section, name_index, path_index)
    # 只保留 20-角色/ 开头的路径
    char_paths = {p for p in char_paths if p.startswith("20-\u89d2\u8272/")}

    if not char_paths:
        diffs.append(f"[SKIP] {filename} --- \u51fa\u573a\u89d2\u8272\u4e3a\u7a7a\u6216\u65e0\u53ef\u8bc6\u522b\u89d2\u8272")
        return diffs

    # 3) 提取关联区已有链接
    link_section = get_section(content, RE_LINK_SECTION)
    link_section_content = link_section if link_section else ""
    existing_links = extract_existing_links(link_section_content)

    # 4) 找出缺失的角色链接
    missing = char_paths - existing_links
    # 过滤：确保只保留 20-角色/ 路径，且不是其它类型链接
    missing = {p for p in missing if p.startswith("20-\u89d2\u8272/")}

    if not missing:
        diffs.append(f"[OK] {filename} --- \u5df2\u6709\u5168\u90e8\u89d2\u8272\u94fe\u63a5")
        return diffs

    # 5) 插入缺失链接到关联区末尾
    new_lines = sorted("- [[{0}]]".format(p) for p in missing)
    insert_text = "\n" + "\n".join(new_lines)

    if link_section is not None:
        # 有关联板块：找到标题行，在其内容末尾插入
        title_match = RE_LINK_SECTION.search(content)
        assert title_match is not None, "RE_LINK_SECTION matched but search failed"

        # 找关联板块的结束位置
        after_title = content[title_match.end():]
        next_section = re.search(r'^#{1,3}\s', after_title, re.MULTILINE)
        if next_section:
            insert_pos = title_match.end() + next_section.start()
        else:
            insert_pos = len(content)

        new_content = content[:insert_pos] + insert_text + content[insert_pos:]
    else:
        # 无关联板块：在文件末尾新增
        new_content = content.rstrip("\n") + "\n\n## \U0001f517 \u5173\u8054\n" + insert_text + "\n"

    # 6) 写回或 dry-run 输出
    if new_content != content:
        if dry_run:
            diffs.append("[DIFF] {0} --- \u9700\u65b0\u589e {1} \u4e2a\u89d2\u8272\u94fe\u63a5: {2}".format(
                filename, len(missing), ", ".join(sorted(missing))))
        else:
            summary_path.write_text(new_content, encoding="utf-8")
            diffs.append("[UPD] {0} --- \u65b0\u589e {1} \u4e2a\u89d2\u8272\u94fe\u63a5: {2}".format(
                filename, len(missing), ", ".join(sorted(missing))))
    else:
        diffs.append("[SAME] {0} --- \u65e0\u53d8\u5316".format(filename))

    return diffs


# ---- 主入口 ----

def main():
    parser = argparse.ArgumentParser(description="\u540c\u6b65\u7ae0\u8282\u6458\u8981\u5173\u8054\u533a\u7684\u89d2\u8272\u94fe\u63a5")
    parser.add_argument("--dry-run", action="store_true", help="\u8bd5\u8fd0\u884c\u6a21\u5f0f\uff0c\u4e0d\u4fee\u6539\u6587\u4ef6")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=200)
    args = parser.parse_args()

    sep = "=" * 60
    print(sep)
    print("  \u7ae0\u8282-\u89d2\u8272\u5173\u8054\u540c\u6b65\u5de5\u5177")
    print("  {}".format("\u8bd5\u8fd0\u884c\u6a21\u5f0f" if args.dry_run else "\u6b63\u5f0f\u6267\u884c"))
    print("  \u8303\u56f4: \u7b2c{:03d}\u7ae0 ~ \u7b2c{:03d}\u7ae0".format(args.start, args.end))
    print(sep)

    # 1) 构建角色索引
    print()
    print("[1/3] \u6784\u5efa\u89d2\u8272\u7d22\u5f15...")
    name_index, path_index = build_character_index()
    print("       name_index: {} \u6761, path_index: {} \u6761".format(len(name_index), len(path_index)))

    # 2) 获取章节摘要文件列表
    print()
    print("[2/3] \u83b7\u53d6\u7ae0\u8282\u6458\u8981\u6587\u4ef6\u5217\u8868...")
    summary_files = []
    for ch in range(args.start, args.end + 1):
        found = list(SUMMARY_DIR.glob("\u7b2c{:03d}\u7ae0-*.md".format(ch)))
        if not found:
            found = list(SUMMARY_DIR.glob("\u7b2c{:03d}\u7ae0.md".format(ch)))
        if found:
            summary_files.append(found[0])

    print("       \u627e\u5230 {} \u4e2a\u7ae0\u8282\u6458\u8981\u6587\u4ef6".format(len(summary_files)))

    # 3) 逐个处理
    print()
    print("[3/3] \u5904\u7406\u7ae0\u8282\u6458\u8981...")
    total_updated = 0
    total_skipped = 0
    total_ok = 0

    for sf in sorted(summary_files, key=lambda p: p.name):
        diffs = process_summary(sf, name_index, path_index, args.dry_run)
        for d in diffs:
            print("  {}".format(d))
            if d.startswith("[UPD]") or d.startswith("[DIFF]"):
                total_updated += 1
            elif d.startswith("[SKIP]"):
                total_skipped += 1
            elif d.startswith("[OK]"):
                total_ok += 1

    # 4) 汇总
    print()
    print(sep)
    print("  \u5904\u7406\u5b8c\u6210")
    print("  - \u603b\u6587\u4ef6\u6570:      {}".format(len(summary_files)))
    print("  - \u5df2\u540c\u6b65(\u6709\u53d8\u66f4): {}".format(total_updated))
    print("  - \u8df3\u8fc7(\u65e0\u51fa\u573a\u89d2\u8272): {}".format(total_skipped))
    print("  - \u65e0\u9700\u53d8\u66f4:    {}".format(total_ok))

    if args.dry_run:
        print()
        print("  [!] \u8fd9\u662f\u8bd5\u8fd0\u884c\uff0c\u672a\u4fee\u6539\u4efb\u4f55\u6587\u4ef6\u3002")
        print("  \u786e\u8ba4\u65e0\u8bef\u540e\u8fd0\u884c: python 90-\u8fdb\u5ea6\u8ffd\u8e2a/sync_chapter_characters.py")
    else:
        print()
        print("  [OK] \u5df2\u5199\u5165\u6587\u4ef6\u3002")

    print(sep)


if __name__ == "__main__":
    main()
