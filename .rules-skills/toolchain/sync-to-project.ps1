<#
.SYNOPSIS
    LeeCommonSkills 三层模板同步脚本
.DESCRIPTION
    将 LeeCommonSkills 三层架构（共享层 + 技术栈层 + 项目层）的 rules 和 skills
    组合分发到目标项目的 .trae 目录。
.PARAMETER Target
    目标项目：server | web | all
.PARAMETER DryRun
    预览模式：只显示将要同步的文件差异，不实际复制
.PARAMETER ProjectRoot
    目标项目根目录路径（如未指定，则使用默认推断路径）
.EXAMPLE
    .\sync-to-project.ps1 -Target server
    .\sync-to-project.ps1 -Target web -DryRun
    .\sync-to-project.ps1 -Target all
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("server","web","all")]
    [string]$Target,

    [switch]$DryRun,

    [string]$ProjectRoot
)

$ErrorActionPreference = "Stop"
$base = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))

# --- 配置 ---
$configs = @{
    server = @{
        StackDir   = "python-stack"
        ProjectDir = "ai-server"
        Layers     = @("shared", "python-stack", "ai-server")
    }
    web = @{
        StackDir   = "react-stack"
        ProjectDir = "ai-web"
        Layers     = @("shared", "react-stack", "ai-web")
    }
}

# --- 工具函数 ---
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $color = switch ($Level) {
        "INFO"  { "Cyan" }
        "OK"    { "Green" }
        "WARN"  { "Yellow" }
        "ERROR" { "Red" }
        "DRY"   { "Magenta" }
    }
    Write-Host "[$Level] $Message" -ForegroundColor $color
}

function Sync-Directory {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$LayerName,
        [bool]$IsDryRun
    )

    if (-not (Test-Path $Source)) {
        Write-Log "源目录不存在，跳过: $Source" "WARN"
        return
    }

    # 确保目标目录存在
    if (-not $IsDryRun) {
        New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    }

    $copied = 0
    $skipped = 0

    $files = Get-ChildItem -Path $Source -Recurse -File
    foreach ($file in $files) {
        $relativePath = $file.FullName.Substring($Source.Length).TrimStart('\','/')
        $targetPath = Join-Path $Destination $relativePath

        $needCopy = $false
        $reason = ""

        if (-not (Test-Path $targetPath)) {
            $needCopy = $true
            $reason = "新增"
        } else {
            $srcHash = (Get-FileHash $file.FullName -Algorithm MD5).Hash
            $dstHash = (Get-FileHash $targetPath -Algorithm MD5).Hash
            if ($srcHash -ne $dstHash) {
                $needCopy = $true
                $reason = "更新"
            } else {
                $skipped++
            }
        }

        if ($needCopy) {
            if ($IsDryRun) {
                Write-Log "[$LayerName] ${reason}: $relativePath" "DRY"
            } else {
                $targetDir = Split-Path -Parent $targetPath
                New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
                Copy-Item -Path $file.FullName -Destination $targetPath -Force
                Write-Log "[$LayerName] ${reason}: $relativePath" "OK"
            }
            $copied++
        }
    }

    Write-Log ("[{0}] Done: copied {1}, skipped {2}" -f $LayerName, $copied, $skipped)
}

function Generate-AgentsMd {
    param([string]$TargetDir, [string[]]$Layers, [bool]$IsDryRun)

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

    $content = "# AGENTS.md — 自动生成`n`n"
    $content += "> 由 sync-to-project.ps1 于 $timestamp 生成`n"
    $content += "> 请勿手动修改此文件，修改源在 LeeCommonSkills/.trae/AGENTS.md`n`n"
    $content += "## 当前项目加载的规则层`n"

    foreach ($layer in $Layers) {
        $content += "- $layer`n"
    }

    $content += "`n## 规则索引`n`n"
    $content += "### 共享层（shared）`n"
    $content += "- 01-git-conventions: Git 提交、分支、版本管理`n"
    $content += "- 02-api-contract: API 契约、OpenAPI、类型同步`n"
    $content += "- 03-error-code-system: 错误码段位、响应格式、traceId`n"
    $content += "- 04-logging-standards: 日志级别、JSON 格式、脱敏`n"
    $content += "- 05-testing-strategy: 测试分层、覆盖率、联调`n"
    $content += "- 06-security-baseline: 输入校验、密钥、XSS/CSRF`n"
    $content += "- 07-dev-workflow: 零干预流程、plan 目录、卡点恢复`n"
    $content += "- 08-cicd-pipeline: CI 触发、构建、部署、回滚`n"

    if ($Layers -contains "python-stack") {
        $content += "`n### Python 技术栈层`n"
        $content += "- 01-coding-standards: Python 命名、格式、注释、类型提示`n"
        $content += "- 02-architecture-patterns: 四层架构、core/、错误处理`n"
        $content += "- 03-code-quality: 审查清单、测试、安全、重构`n"
    }

    if ($Layers -contains "react-stack") {
        $content += "`n### React 技术栈层`n"
        $content += "- 01-coding-standards: TS/React 命名、格式、TSDoc`n"
        $content += "- 02-architecture-patterns: feature-based、目录、数据流`n"
        $content += "- 03-code-quality: 审查清单、测试、性能、重构`n"
        $content += "- 04-a11y-rules: WCAG 2.1 AA、ARIA、键盘导航`n"
        $content += "- 05-performance-budget: Core Web Vitals、bundle 限制`n"
    }

    $content += "`n### 项目定制层`n"
    $content += "- project/00-project-overview.md: 项目概述`n"
    $content += "- project/01-project-specific.md: 项目特定规则`n"

    $targetPath = Join-Path $TargetDir ".trae\AGENTS.md"
    if ($IsDryRun) {
        Write-Log "[generated] AGENTS.md → $targetPath" "DRY"
    } else {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $targetPath) | Out-Null
        $content | Out-File -FilePath $targetPath -Encoding utf8 -Force
        Write-Log "[generated] AGENTS.md → $targetPath" "OK"
    }
}

# --- 主同步逻辑 ---
function Sync-Target {
    param([string]$TargetName, [bool]$IsDryRun)

    $cfg = $configs[$TargetName]
    Write-Log "`n{'='*60}" "INFO"
    Write-Log "开始同步: $TargetName" "INFO"
    Write-Log "模式: $(if ($IsDryRun) {'预览(DryRun)'} else {'实际同步'})" "INFO"

    # 推断目标项目路径
    $projectPath = $ProjectRoot
    if (-not $projectPath) {
        # 尝试常见路径
        $candidates = @(
            "d:\workspances-software\workspace-github\$($cfg.ProjectDir)",
            "..\$($cfg.ProjectDir)",
            "..\..\$($cfg.ProjectDir)"
        )
        foreach ($p in $candidates) {
            $fullPath = if (Test-Path $p) { (Resolve-Path $p).Path } else { $p }
            if (Test-Path $fullPath) {
                $projectPath = $fullPath
                break
            }
        }
    }

    if (-not $projectPath -or -not (Test-Path $projectPath)) {
        Write-Log "目标项目路径不存在: $projectPath" "WARN"
        Write-Log "请使用 -ProjectRoot 参数指定目标项目路径" "WARN"
        Write-Log "示例: .\sync-to-project.ps1 -Target $TargetName -ProjectRoot 'C:\path\to\$($cfg.ProjectDir)'" "INFO"
        return
    }

    Write-Log "目标项目: $projectPath" "INFO"
    $targetTrae = Join-Path $projectPath ".trae"

    # --- 同步共享层 ---
    Write-Log "`n--- 同步共享层 (shared) ---" "INFO"
    Sync-Directory `
        -Source "$base\.trae\rules\shared" `
        -Destination "$targetTrae\rules\shared" `
        -LayerName "shared-rules" `
        -IsDryRun $IsDryRun

    Sync-Directory `
        -Source "$base\.trae\rules\templates" `
        -Destination "$targetTrae\rules\templates" `
        -LayerName "shared-templates" `
        -IsDryRun $IsDryRun

    Sync-Directory `
        -Source "$base\.trae\skills\shared" `
        -Destination "$targetTrae\skills\shared" `
        -LayerName "shared-skills" `
        -IsDryRun $IsDryRun

    # --- 同步技术栈层 ---
    $stackDir = "$base\.rules-skills\$($cfg.StackDir)\.trae"
    Write-Log "`n--- 同步技术栈层 ($($cfg.StackDir)) ---" "INFO"
    Sync-Directory `
        -Source "$stackDir\rules" `
        -Destination "$targetTrae\rules\stack" `
        -LayerName "stack-rules" `
        -IsDryRun $IsDryRun

    Sync-Directory `
        -Source "$stackDir\skills" `
        -Destination "$targetTrae\skills\stack" `
        -LayerName "stack-skills" `
        -IsDryRun $IsDryRun

    # --- 同步项目层（rules 不覆盖，skills 复制新增） ---
    $projectSource = "$base\.rules-skills\$($cfg.ProjectDir)\.trae"
    Write-Log "`n--- 同步项目层 ($($cfg.ProjectDir)) ---" "INFO"

    # Project rules: 仅复制新增文件，不覆盖已有文件
    if (Test-Path "$projectSource\rules\project") {
        $projectRules = Get-ChildItem -Path "$projectSource\rules\project" -Recurse -File
        foreach ($file in $projectRules) {
            $relativePath = $file.FullName.Substring("$projectSource\rules\project".Length).TrimStart('\','/')
            $targetPath = Join-Path "$targetTrae\rules\project" $relativePath

            if (-not (Test-Path $targetPath)) {
                if ($IsDryRun) {
                    Write-Log "[project-rules] 新增: ${relativePath}" "DRY"
                } else {
                    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $targetPath) | Out-Null
                    Copy-Item -Path $file.FullName -Destination $targetPath -Force
                    Write-Log "[project-rules] 新增: ${relativePath}" "OK"
                }
            } else {
                Write-Log "[project-rules] 保留(不覆盖): ${relativePath}" "WARN"
            }
        }
    }

    # Project skills: 复制新增，保留已有
    if (Test-Path "$projectSource\skills") {
        $projectSkills = Get-ChildItem -Path "$projectSource\skills" -Recurse -File
        foreach ($file in $projectSkills) {
            $relativePath = $file.FullName.Substring("$projectSource\skills".Length).TrimStart('\','/')
            $targetPath = Join-Path "$targetTrae\skills\project" $relativePath

            if (-not (Test-Path $targetPath)) {
                if ($IsDryRun) {
                    Write-Log "[project-skills] 新增: ${relativePath}" "DRY"
                } else {
                    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $targetPath) | Out-Null
                    Copy-Item -Path $file.FullName -Destination $targetPath -Force
                    Write-Log "[project-skills] 新增: ${relativePath}" "OK"
                }
            } else {
                Write-Log "[project-skills] 保留(不覆盖): ${relativePath}" "WARN"
            }
        }
    }

    # --- 同步 WORKFLOW.md ---
    $workflowFile = "$projectSource\WORKFLOW.md"
    if (Test-Path $workflowFile) {
        $targetWorkflow = "$targetTrae\WORKFLOW.md"
        if ($IsDryRun) {
            Write-Log "[workflow] WORKFLOW.md" "DRY"
        } else {
            Copy-Item -Path $workflowFile -Destination $targetWorkflow -Force
            Write-Log "[workflow] WORKFLOW.md" "OK"
        }
    }

    # --- 生成 AGENTS.md ---
    Write-Log "`n--- 生成 AGENTS.md ---" "INFO"
    Generate-AgentsMd -TargetDir $projectPath -Layers $cfg.Layers -IsDryRun $IsDryRun

    # --- 生成 SKILL_REGISTRY.md ---
    Write-Log "`n--- 生成 SKILL_REGISTRY.md ---" "INFO"
    $registrySource = "$base\.trae\skills\SKILL_REGISTRY.md"
    $registryTarget = "$targetTrae\SKILL_REGISTRY.md"
    if ($IsDryRun) {
        Write-Log "[registry] SKILL_REGISTRY.md" "DRY"
    } else {
        Copy-Item -Path $registrySource -Destination $registryTarget -Force
        Write-Log "[registry] SKILL_REGISTRY.md" "OK"
    }

    Write-Log "`n同步完成: $TargetName" "OK"
}

# --- 执行 ---
if ($Target -eq "all") {
    Sync-Target -TargetName "server" -IsDryRun $DryRun
    Sync-Target -TargetName "web" -IsDryRun $DryRun
} else {
    Sync-Target -TargetName $Target -IsDryRun $DryRun
}

Write-Log "`n{'='*60}" "INFO"
Write-Log "全部同步操作完成" "OK"
