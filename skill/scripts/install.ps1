# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
# Licensed under the MIT License. See the LICENSE file for details.
#
# gongwen-optimizer skill 安装器（Windows / PowerShell）
# 将 skill/ 源目录复制到各 Agent 平台的技能目录（复制而非符号链接，避免权限问题）。
#
# 用法:
#   powershell -ExecutionPolicy Bypass -File skill/scripts/install.ps1 -All
#   powershell -ExecutionPolicy Bypass -File skill/scripts/install.ps1 -List
#   $env:SKILL_DIRS="C:\a;C:\b"; powershell -ExecutionPolicy Bypass -File skill/scripts/install.ps1

param(
  [switch]$All,
  [switch]$List
)

$ErrorActionPreference = "Stop"
$SkillSource = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$TargetName = "gongwen-optimizer"

$DefaultTargets = @(
  "$env:USERPROFILE\.claude\skills",          # Claude Code
  "$env:USERPROFILE\.codex\skills",           # Codex
  "$env:USERPROFILE\.config\opencode\skill",  # OpenCode
  "$env:USERPROFILE\.trae\skills",            # Trae Code
  "$env:USERPROFILE\.kimi\skills",            # Kimi Code
  "$env:USERPROFILE\.zcode\skills",           # ZCode
  "$env:USERPROFILE\.traework\skills",        # TraeWork
  "$env:USERPROFILE\.workbuddy\skills",       # WorkBuddy
  "$env:USERPROFILE\.cursor\skills"           # Cursor
)

function Get-Targets {
  if ($env:SKILL_DIRS) {
    return $env:SKILL_DIRS -split ";"
  }
  return $DefaultTargets
}

function Install-One {
  param([string]$Target)
  if (-not $Target) { return }
  $Dest = Join-Path $Target $TargetName
  New-Item -ItemType Directory -Force -Path $Target | Out-Null
  if (Test-Path $Dest) {
    Remove-Item -Recurse -Force $Dest
  }
  Copy-Item -Recurse -Force $SkillSource $Dest
  Write-Host "[install] copied: $Dest <- $SkillSource"
}

if ($List) {
  Write-Host "source: $SkillSource"
  Write-Host "targets:"
  foreach ($t in (Get-Targets)) { Write-Host "  $(Join-Path $t $TargetName)" }
  exit 0
}

if ($All -or -not $PSBoundParameters.Count) {
  foreach ($t in (Get-Targets)) { Install-One $t }
  Write-Host "[install] done."
} else {
  Write-Host "usage: install.ps1 [-All|-List]" -ForegroundColor Yellow
  exit 1
}
