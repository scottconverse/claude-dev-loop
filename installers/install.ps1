<#
.SYNOPSIS
    Install the claude-dev-loop skill into the user's Claude Code skills directory.

.DESCRIPTION
    Copies skill/CLAUDE.md, scripts/, and vault-templates/ into
    $HOME\.claude\skills\claude-dev-loop so the skill loads in the Cowork Desktop app
    (Code tab) and the helper scripts (which copy the templates into each project vault)
    work from the installed location.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File installers\install.ps1
#>

[CmdletBinding()]
param(
    [string]$Destination = (Join-Path $HOME ".claude\skills\claude-dev-loop")
)

$ErrorActionPreference = "Stop"

# Repo root = parent of this installers/ directory.
$RepoRoot = Split-Path -Parent $PSScriptRoot

$skillSrc     = Join-Path $RepoRoot "skill"
$scriptsSrc   = Join-Path $RepoRoot "scripts"
$templatesSrc = Join-Path $RepoRoot "vault-templates"

foreach ($p in @($skillSrc, $scriptsSrc, $templatesSrc)) {
    if (-not (Test-Path $p)) {
        throw "Missing source folder: $p  (run this from inside the claude-dev-loop repo)"
    }
}

Write-Host "Installing claude-dev-loop ->" $Destination -ForegroundColor Cyan

# Fresh skill payload (skill/CLAUDE.md and anything else under skill/)
$scriptsDst   = Join-Path $Destination "scripts"
$templatesDst = Join-Path $Destination "vault-templates"

New-Item -ItemType Directory -Force -Path $Destination   | Out-Null
New-Item -ItemType Directory -Force -Path $scriptsDst     | Out-Null
New-Item -ItemType Directory -Force -Path $templatesDst   | Out-Null

# 1. Skill file(s)
Copy-Item -Path (Join-Path $skillSrc "*") -Destination $Destination -Recurse -Force

# 2. Scripts
Copy-Item -Path (Join-Path $scriptsSrc "*.py") -Destination $scriptsDst -Force

# 3. Vault templates (bootstrap_vault.py copies these into each project)
Copy-Item -Path (Join-Path $templatesSrc "*.md") -Destination $templatesDst -Force

$copiedScripts   = (Get-ChildItem $scriptsDst -Filter *.py | Measure-Object).Count
$copiedTemplates = (Get-ChildItem $templatesDst -Filter *.md | Measure-Object).Count

Write-Host ""
Write-Host "Installed:" -ForegroundColor Green
Write-Host "  CLAUDE.md      -> $Destination\CLAUDE.md"
Write-Host "  scripts        -> $scriptsDst ($copiedScripts files)"
Write-Host "  vault-templates-> $templatesDst ($copiedTemplates files)"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. In any project:  python `"$scriptsDst\bootstrap_vault.py`" --target ."
Write-Host "  2. Restart Claude Code (Cowork Desktop) so it picks up the new skill."
