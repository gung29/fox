# ============================================================
#  FOX — cross-platform installer (Windows PowerShell native)
#  Opsi A — manual installer.
#  Menerapkan Fox persona + skills ke harness:
#    opencode · oh-my-pi (omp) · hermes-agent
#  Linux/macOS/WSL pakai -> install.sh
#
#  Usage:
#    powershell -ExecutionPolicy Bypass -File .\install.ps1            # preview
#    powershell -ExecutionPolicy Bypass -File .\install.ps1 -Apply     # apply semua
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
        Write-Host "  [i] python (unbranded) ditemukan" ; return } catch {}
    Write-Host "  [!] Python 3 tidak ditemukan. Fox butuh Python." -ForegroundColor Yellow
    Write-Host "      Install dari https://python.org atau winget install Python.Python.3" -ForegroundColor Yellow
    exit 1
}

if (-not $Apply) {
    Write-Host "==> FOX Installer (Opsi A) — PREVIEW" -ForegroundColor Yellow
    Write-Host "  Akan mendeteksi & menginstal persona/skills Fox ke:"
    Write-Host "    • opencode     (agent.fox + skill paths + perm allow)"
    Write-Host "    • oh-my-pi     (~/.omp/agent models.yml router + persona)"
    Write-Host "    • hermes-agent (~/.hermes config.yaml + SOUL.md + prefill)"
    Write-Host "  Setiap target = backup config lama dulu."
    Write-Host "  RUN:  powershell -ExecutionPolicy Bypass -File .\install.ps1 -Apply"
    exit 0
}

Write-Host "==> FOX Installer (Opsi A) — APPLY" -ForegroundColor Yellow
Ensure-Python
& powershell -ExecutionPolicy Bypass -File (Join-Path $Repo "config\install-fox.ps1") -Apply -Target $Target
Write-Host "==> Selesai. Restart harness agar persona aktif." -ForegroundColor Green
