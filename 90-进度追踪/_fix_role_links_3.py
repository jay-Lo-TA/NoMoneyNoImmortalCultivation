#!/usr/bin/env python3
"""批量修复角色 wikilink 错误 - 第三轮 (剩余特殊链接)."""
from pathlib import Path

BASE = Path(r"E:\Personal\KownledgeBase\没钱修什么仙-番剧制作")

REPLACEMENTS = [
    # 车女 (后接文字)
    ("[[20-角色/配角/车女]]暗学帮老师", "[[20-角色/配角/人物-82-车女-暗学帮教头-跑车腿10级]]暗学帮老师"),
    ("[[20-角色/配角/车女]]暗学帮试听课老师", "[[20-角色/配角/人物-82-车女-暗学帮教头-跑车腿10级]]暗学帮试听课老师"),

    # 张翩翩/王海 的 #section 链接 (section 不存在, 删除 #section)
    ("[[20-角色/配角/张翩翩#剧情强化补充]]", "[[20-角色/配角/人物-20-张翩翩]]"),
    ("[[20-角色/配角/王海#体育老师王海]]", "[[20-角色/配角/人物-04-王海]]"),

    # 特殊 ] 字符 (用 【】 代替) - 这些是误用全角符号
    ("[[20-角色/配角/仙韵集团研究员（'老师'）】", "[[20-角色/配角/人物-33-仙韵集团指导老师]]"),
    ("[[20-角色/配角/高一试功学生群体】", "高一试功学生群体"),
]

total_files = 0
changed_files = 0
total_replacements = 0

for md_file in BASE.rglob("*.md"):
    if any(part.startswith(".") for part in md_file.parts):
        continue
    total_files += 1
    try:
        content = md_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            content = md_file.read_text(encoding="gbk")
        except Exception:
            print(f"  [SKIP] 编码错误: {md_file}")
            continue

    original = content
    file_replacements = 0
    for old, new in REPLACEMENTS:
        if old in content:
            n = content.count(old)
            content = content.replace(old, new)
            file_replacements += n

    if content != original:
        md_file.write_text(content, encoding="utf-8")
        changed_files += 1
        total_replacements += file_replacements
        print(f"  [{file_replacements:3d}] {md_file.name}")

print()
print("=" * 50)
print(f"扫描文件: {total_files}")
print(f"修改文件: {changed_files}")
print(f"总替换数: {total_replacements}")
