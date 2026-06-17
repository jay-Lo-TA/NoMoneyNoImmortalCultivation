#!/usr/bin/env python3
"""Find the 3 remaining broken links."""
import re
from pathlib import Path
from collections import Counter

BASE = Path(r"E:\Personal\KownledgeBase\没钱修什么仙-番剧制作")

patterns = [
    r"\[\[20-角色/配角/张翩翩\]\]",
    r"\[\[20-角色/配角/王海\]\]",
    r"\[\[20-角色/法宝\]\]",
    r"\[\[20-角色/配角\]\]",
    r"\[\[20-角色/配角/\]\]",
    r"\[\[20-角色/法宝/[^\]]+\]\]",
]

results = {}
for pat in patterns:
    matches = []
    for md_file in BASE.rglob("*.md"):
        if any(part.startswith(".") for part in md_file.parts):
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except:
            continue
        for m in re.finditer(pat, content):
            line_num = content[:m.start()].count("\n") + 1
            line = content.split("\n")[line_num - 1].strip()
            matches.append((str(md_file.relative_to(BASE)), line_num, m.group(0), line))
    results[pat] = matches
    print(f"=== {pat} : {len(matches)} matches ===")
    for path, ln, match, line in matches[:5]:
        print(f"  {path}:{ln}: {line[:100]}")
    print()
