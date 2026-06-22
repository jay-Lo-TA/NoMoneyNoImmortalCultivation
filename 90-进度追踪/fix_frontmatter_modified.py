#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新所有章节摘要文件的 YAML frontmatter modified 字段为当前日期。
用于在批量内容修改后同步 Obsidian 的修改时间戳。

用法：
  python 90-进度追踪/fix_frontmatter_modified.py --dry-run
  python 90-进度追踪/fix_frontmatter_modified.py
"""

import argparse
import re
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUMMARY_DIR = PROJECT_ROOT / "30-\u5267\u60c5" / "\u7ae0\u8282\u6458\u8981"

# 今日日期
TODAY = date.today().isoformat()  # "2026-06-22"

# 匹配 YAML frontmatter 中的 modified 行
RE_MODIFIED = re.compile(r'^modified:\s*\S+.*$', re.MULTILINE)


def update_modified(content: str, new_date: str) -> str | None:
    """替换 YAML frontmatter 中的 modified 行为新日期。
    
    如果 modified 已等于 new_date 则返回 None（无需修改）。
    """
    match = RE_MODIFIED.search(content)
    if not match:
        return None  # 没有 modified 字段

    old_line = match.group(0)
    # 如果已经是新日期，跳过
    if f"modified: {new_date}" in old_line:
        return None

    new_line = f"modified: {new_date}"
    return content.replace(old_line, new_line, 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=200)
    args = parser.parse_args()

    sep = "=" * 60
    print(sep)
    print("  \u66f4\u65b0 summary frontmatter modified -> {}".format(TODAY))
    print("  {}".format("\u8bd5\u8fd0\u884c\u6a21\u5f0f" if args.dry_run else "\u6b63\u5f0f\u6267\u884c"))
    print(sep)

    summary_files = []
    for ch in range(args.start, args.end + 1):
        found = list(SUMMARY_DIR.glob("\u7b2c{:03d}\u7ae0-*.md".format(ch)))
        if not found:
            found = list(SUMMARY_DIR.glob("\u7b2c{:03d}\u7ae0.md".format(ch)))
        if found:
            summary_files.append(found[0])

    print("\n  \u627e\u5230 {} \u4e2a\u6587\u4ef6".format(len(summary_files)))

    updated = 0
    skipped_no_mod = 0
    skipped_same = 0

    for sf in sorted(summary_files, key=lambda p: p.name):
        try:
            content = sf.read_text(encoding="utf-8")
        except Exception as e:
            print("  [ERR] {} - {}".format(sf.name, e))
            continue

        new_content = update_modified(content, TODAY)
        if new_content is None:
            # 检查是没有 modified 还是已是最新
            if RE_MODIFIED.search(content):
                skipped_same += 1
            else:
                # 无法修改 modified
                print("  [NO-MOD] {} - \u65e0 modified \u5b57\u6bb5".format(sf.name))
                skipped_no_mod += 1
        elif new_content != content:
            if args.dry_run:
                print("  [DIFF] {} -> modified: {}".format(sf.name, TODAY))
            else:
                sf.write_text(new_content, encoding="utf-8")
                print("  [UPD]  {} -> modified: {}".format(sf.name, TODAY))
            updated += 1

    print()
    print(sep)
    print("  \u5b8c\u6210")
    print("  - \u66f4\u65b0: {}".format(updated))
    print("  - \u5df2\u6700\u65b0(\u65e0\u9700\u6539\u53d8): {}".format(skipped_same))
    print("  - \u65e0 modified \u5b57\u6bb5: {}".format(skipped_no_mod))

    if args.dry_run:
        print()
        print("  [!] \u8fd9\u662f\u8bd5\u8fd0\u884c")
    print(sep)


if __name__ == "__main__":
    main()
