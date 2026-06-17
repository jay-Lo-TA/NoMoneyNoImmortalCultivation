#!/usr/bin/env python3
"""第六轮修复: 移除/替换 [[20-角色/配角#xxx]] 形式的 section 链接.

策略:
1. 已知角色 → 替换为 [[20-角色/配角/人物-XX-xxx]] 保留 section
2. 通用描述 → 转为纯文本 xxx
3. 错文件名 [[20-角色/配角/张翩翩#xxx]] → 改为 [[20-角色/配角/人物-20-张翩翩#xxx]]
4. [[20-角色/配角图鉴]] → 纯文本
"""
import re
from pathlib import Path

BASE = Path(r"E:\Personal\KownledgeBase\没钱修什么仙-番剧制作")

# === 已知角色映射: section name → (相对路径, 是否保留 section) ===
# 格式: (section_name) -> (target_path, keep_section)
CHARACTER_MAP = {
    # 主角
    "白真真": ("20-角色/主角/白真真", True),
    "张羽": ("20-角色/主角/张羽", True),
    # 配角
    "严老师": ("20-角色/配角/人物-01-严老师", True),
    "乐景辰": ("20-角色/配角/人物-69-乐景辰", True),
    "乐沐岚": ("20-角色/配角/人物-10-乐沐岚", True),
    "云景": ("20-角色/配角/人物-69-云景-仙云高中高二首席-昆墟一层最强高中生", True),
    "何大有": ("20-角色/配角/人物-31-何大有", True),
    "周澈尘": ("20-角色/配角/人物-05-周澈尘", True),
    "墨天逸": ("20-角色/配角/人物-14-墨天逸", True),
    "墨天逸（邙山高中）": ("20-角色/配角/人物-14-墨天逸", False),
    "夜凌霄": ("20-角色/配角/人物-70-夜凌霄-绿洲集团最完美肉体血脉-红包符练习者", True),
    "妙云": ("20-角色/配角/人物-71-妙云-仙韵集团化妆师-形象设计师", True),
    "安安": ("20-角色/配角/人物-72-安安-小熊猫-红塔牧业繁育基地最佳员工", True),
    "宋海龙": ("20-角色/配角/人物-12-宋海龙", True),
    "张翩翩": ("20-角色/配角/人物-20-张翩翩", True),
    "张翩翩（白龙高中，张羽姐姐）": ("20-角色/配角/人物-20-张翩翩", False),
    "戴行之": ("20-角色/配角/人物-71-戴行之", True),
    "梁勤": ("20-角色/配角/人物-07-梁勤", True),
    "楚秋河": ("20-角色/配角/人物-27-楚秋河", True),
    "武青青": ("20-角色/配角/人物-08-武青青", True),
    "炼天极": ("20-角色/配角/人物-11-炼天极", True),
    "熊文武": ("20-角色/配角/人物-29-熊文武", True),
    "玉星寒": ("20-角色/配角/人物-66-玉星寒", True),
    "王海": ("20-角色/配角/人物-04-王海", True),
    "王海（体育老师）": ("20-角色/配角/人物-04-王海", False),
    "福姬": ("20-角色/配角/人物-73-福姬", True),
    "苏海峰": ("20-角色/配角/人物-03-苏海峰", True),
    "苏海峰（班主任）": ("20-角色/配角/人物-03-苏海峰", False),
    "蒙涛": ("20-角色/配角/人物-79-蒙涛-仙都壮汉-暴食考场选手", True),
    "蓝岭": ("20-角色/配角/人物-06-蓝岭", True),
    "虎云涛": ("20-角色/配角/人物-28-虎云涛", True),
    "赵天行": ("20-角色/配角/人物-22-赵天行", True),
    "邓丙丁": ("20-角色/配角/人物-67-邓丙丁-邓游神-六等四方游神筑基考官", True),
    "野纤云": ("20-角色/配角/人物-09-野纤云", True),
    "钱深": ("20-角色/配角/人物-23-钱深", True),
    "黄子丑": ("20-角色/配角/人物-68-黄子丑-九等功曹小神", True),
    "老王（人力资源中介）": ("20-角色/配角/人物-46-老王-中介", False),
    "仙韵集团指导老师": ("20-角色/配角/人物-33-仙韵集团指导老师", True),
    "仙韵集团研究员（老师）": ("20-角色/配角/人物-33-仙韵集团指导老师", False),
    "小熊猫（红塔高中）": ("20-角色/配角/人物-72-安安-小熊猫-红塔牧业繁育基地最佳员工", False),
    "云霓": ("20-角色/同学/素云霓", True),  # 同学/子目录
    "刚山": (None, False),  # 无文件, 转纯文本
}

# 通用描述 (无对应文件, 转纯文本)
GENERIC_NAMES = {
    "买到假药的学生", "其他修仙者", "其他学校学生", "其他高中生",
    "嵩阳高中老师", "巡察队员", "对手", "紫云高中接待老师",
    "老大", "研究员助手", "神秘女生（白龙高中）", "计费卖票员",
}

# 错文件名前缀 [[20-角色/配角/张翩翩#xxx]] 和 [[20-角色/配角/王海#xxx]]
WRONG_FILENAME_MAP = {
    "20-角色/配角/张翩翩": "20-角色/配角/人物-20-张翩翩",
    "20-角色/配角/王海": "20-角色/配角/人物-04-王海",
}

# === 错文件路径 → 正确路径 (人物-XX- 前缀) ===
# 形式 [[20-角色/配角/xxx]] 中 xxx 不是 人物-XX- 开头的, 尝试在 CHARACTER_MAP 中找到 xxx
def fix_role_path(match):
    full = match.group(0)  # 完整 [[...]]
    # 处理 [[20-角色/配角图鉴]] (无对应目录, 转纯文本)
    if full == "[[20-角色/配角图鉴]]":
        return "配角图鉴"
    # 处理 [[20-角色/配角#section]]
    m_sec = re.match(r"\[\[20-角色/配角#([^\]]+)\]\]$", full)
    if m_sec:
        section = m_sec.group(1)
        if section in CHARACTER_MAP:
            path, keep_sec = CHARACTER_MAP[section]
            if path is None:
                return section  # 转纯文本
            if keep_sec:
                return f"[[{path}#{section}]]"
            else:
                return f"[[{path}]]"
        elif section in GENERIC_NAMES:
            return section
        else:
            return section  # 默认转纯文本
    # 处理 [[20-角色/配角/张翩翩#xxx]] 或 [[20-角色/配角/王海#xxx]]
    m_wrong = re.match(r"\[\[20-角色/配角/(张翩翩|王海)#([^\]]+)\]\]$", full)
    if m_wrong:
        wrong_name = m_wrong.group(1)
        section = m_wrong.group(2)
        correct_path = WRONG_FILENAME_MAP.get(f"20-角色/配角/{wrong_name}")
        if correct_path:
            return f"[[{correct_path}#{section}]]"
    # 其他形式: 直接转纯文本
    return full[2:-2]

total_files = 0
changed_files = 0
total_replacements = 0

pat = re.compile(r"\[\[20-角色/配角[^\]\|#]*[^\]]*?\]\]")

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
    counter = [0]

    def repl(m):
        counter[0] += 1
        return fix_role_path(m)

    content = pat.sub(repl, content)

    if content != original:
        md_file.write_text(content, encoding="utf-8")
        changed_files += 1
        total_replacements += counter[0]
        print(f"  [{counter[0]:3d}] {md_file.name}")

print()
print("=" * 50)
print(f"扫描文件: {total_files}")
print(f"修改文件: {changed_files}")
print(f"总替换数: {total_replacements}")
