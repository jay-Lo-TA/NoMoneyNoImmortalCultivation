# 修复章节摘要断链脚本
# 把 [[30-剧情/章节摘要/第XXX章]] 替换为完整文件名引用
# 把 [[第XXX章]] 替换为完整文件名引用（索引文件范围用法）

$ErrorActionPreference = "Stop"
$projectRoot = "E:\Personal\KownledgeBase\没钱修什么仙-番剧制作"
$chapterDir = "$projectRoot\30-剧情\章节摘要"

# 1) 构建章节号 -> 完整标题的映射
$map = @{}
Get-ChildItem -Path $chapterDir -Filter "*.md" -File | ForEach-Object {
    $name = $_.BaseName
    if ($name -match "^(第\d+章)(-(.+))?$") {
        $num = $matches[1]
        $map[$num] = $name
    }
}
Write-Host "章节映射表大小: $($map.Count)"

# 检查未在 map 中的引用
$missing = @{}

# 2) 收集所有 .md 文件（排除归档目录、.assets、进度追踪里的脚本本身）
$files = Get-ChildItem -Path $projectRoot -Recurse -Include "*.md" -File |
    Where-Object {
        $_.FullName -notmatch "\\\.assets\\" -and
        $_.FullName -notmatch "00-归档" -and
        $_.FullName -notmatch "00-第\d+-\d+章.*索引_归档" -and
        $_.FullName -ne "$projectRoot\90-进度追踪\90-TODO.md"
    }

Write-Host "待处理 .md 文件数: $($files.Count)"

# 3) 逐文件处理
$totalFiles = 0
$totalReplacements = 0
$report = @()

foreach ($file in $files) {
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    $original = $content
    $fileChanges = 0

    # Pass 1: [[30-剧情/章节摘要/第XXX章]] -> 完整
    $content = [regex]::Replace($content, '\[\[30-剧情/章节摘要/(第\d+章)\]\]', {
        param($m)
        $num = $m.Groups[1].Value
        if ($map.ContainsKey($num)) {
            return "[[30-剧情/章节摘要/$($map[$num])]]"
        } else {
            $script:missing[$num] = $true
            return $m.Value
        }
    })
    # 计算 pass1 替换数（差异对比不可靠，用脚本级变量累加）
    # 改用单独统计：跑两遍原内容对比
    $pass1Count = ([regex]::Matches($original, '\[\[30-剧情/章节摘要/第\d+章\]\]')).Count
    $fileChanges += $pass1Count

    # Pass 2: 独立的 [[第XXX章]] -> 完整（此时 path-prefix 的已被 pass1 替换）
    # 匹配前不是 / 或 \w 的 [[
    $content = [regex]::Replace($content, '(?<![\w/\-])\[\[(第\d+章)\]\]', {
        param($m)
        $num = $m.Groups[1].Value
        if ($map.ContainsKey($num)) {
            return "[[$($map[$num])]]"
        } else {
            $script:missing[$num] = $true
            return $m.Value
        }
    })
    $pass2Count = ([regex]::Matches($original, '(?<![\w/\-])\[\[第\d+章\]\]')).Count
    $fileChanges += $pass2Count

    if ($content -ne $original) {
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
        $totalFiles++
        $totalReplacements += $fileChanges
        $report += [PSCustomObject]@{
            File = $file.FullName.Replace($projectRoot + "\", "")
            Changes = $fileChanges
        }
    }
}

Write-Host ""
Write-Host "=== 修复完成 ==="
Write-Host "修改文件数: $totalFiles"
Write-Host "总替换处数: $totalReplacements"
Write-Host ""

if ($missing.Count -gt 0) {
    Write-Host "=== 警告：以下章节号在文件名映射中找不到 ==="
    $missing.Keys | Sort-Object | ForEach-Object { Write-Host "  - $_" }
} else {
    Write-Host "无遗漏章节号"
}

Write-Host ""
Write-Host "=== 变更文件列表 ==="
$report | Sort-Object Changes -Descending | Format-Table -AutoSize
