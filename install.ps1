# ============================================================
#  FOX - cross-platform installer (Windows PowerShell native)
#  Option A - manual installer.
#  Applies Fox persona + skills to harness:
#    opencode / oh-my-pi (omp) / hermes-agent
#  Linux/macOS/WSL use -> install.sh
#
#  Usage:
#    powershell -ExecutionPolicy Bypass -File .\install.ps1            # preview
#    powershell -ExecutionPolicy Bypass -File .\install.ps1 -Apply     # apply all
#    powershell -ExecutionPolicy Bypass -File .\install.ps1 -Apply -Target opencode|omp|hermes
# ============================================================
[CmdletBinding()]
param(
    [switch]$Apply,
    [ValidateSet("all","opencode","omp","hermes")][string]$Target = "all"
)

$Repo = Split-Path -Parent $MyInvocation.MyCommand.Path

function Ensure-Python {
    try { python3 --version *> $null; return } catch {}
    try { python --version *> $null
        Write-Host "  [i] python (unbranded) found" ; return } catch {}
    Write-Host "  [!] Python 3 not found. Fox needs Python." -ForegroundColor Yellow
    Write-Host "      Install from https://python.org or: winget install Python.Python.3" -ForegroundColor Yellow
    exit 1
}

if (-not $Apply) {
    Write-Host "==> FOX Installer (Option A) - PREVIEW" -ForegroundColor Yellow
    Write-Host "  Will detect & install Fox persona/skills into:"
    Write-Host "    * opencode     (agent.fox + skill paths + perm allow)"
    Write-Host "    * oh-my-pi     (~/.omp/agent models.yml router + persona)"
    Write-Host "    * hermes-agent (~/.hermes config.yaml + SOUL.md + prefill)"
    Write-Host "  Every target backs up its config before touching it."
    Write-Host "  RUN:  powershell -ExecutionPolicy Bypass -File .\install.ps1 -Apply"
    exit 0
}

Write-Host "==> FOX Installer (Option A) - APPLY" -ForegroundColor Yellow
Ensure-Python
& powershell -ExecutionPolicy Bypass -File (Join-Path $Repo "config\install-fox.ps1") -Apply -Target $Target
Write-Host "==> Done. Restart harness for persona to activate." -ForegroundColor Green
