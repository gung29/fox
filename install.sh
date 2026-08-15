#!/bin/bash
# ============================================================
#  FOX — cross-platform installer (Linux / macOS / WSL / Git Bash)
#  Opsi A — manual installer.
#  Menerapkan Fox persona + skills ke harness:
#    opencode · oh-my-pi (omp) · hermes-agent
#  Windows native pakai -> install.ps1
#
#  Usage:
#    ./install.sh            # preview
#    ./install.sh apply      # install/applyn ke semua harness terdeteksi
#    ./install.sh apply -t opencode|omp|hermes
# ============================================================
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-preview}"
TARGET="all"
[ "${2:-}" = "-t" ] && [ -n "${3:-}" ] && TARGET="$3"

# --- pasang python3 bila belum ada (hermes dan config adapter butuh) ---
ensure_python() {
  if command -v python3 >/dev/null 2>&1; then return; fi
  echo "  [!] python3 tidak ditemukan. Coba pasang..."
  if command -v apt-get >/dev/null 2>&1; then sudo apt-get update && sudo apt-get install -y python3; fi
  if command -v dnf >/dev/null 2>&1; then sudo dnf install -y python3; fi
  if command -v pacman >/dev/null 2>&1; then sudo pacman -S --noconfirm python; fi
  if command -v brew >/dev/null 2>&1; then brew install python; fi
  command -v python3 >/dev/null 2>&1 || { echo "  [x] gagal pasang python3. Install manual."; exit 1; }
}

preview() {
  cat <<EOF
==> FOX Installer (Opsi A) — PREVIEW
  Akan mendeteksi & menginstal persona/skills Fox ke:
    • opencode     (agent.fox + skill paths + perm allow)
    • oh-my-pi     (~/.omp/agent models.yml router + persona)
    • hermes-agent (~/.hermes config.yaml + SOUL.md + prefill)
  Skrip yang dipakai (auto-pick per OS):
    • Linux/macOS/WSL/Git Bash → config/install-fox.sh
    • Windows native          → config/install-fox.ps1
  Setiap target = backup config lama dulu.

  RUN:  ./install.sh apply
        ./install.sh apply -t opencode   # hanya satu harness
EOF
}

apply() {
  echo "==> FOX Installer (Opsi A) — APPLY"
  ensure_python
  sh "$REPO/config/install-fox.sh" apply "$TARGET"
  echo "==> Selesai. Restart harness agar persona aktif."
}

case "$MODE" in
  apply) apply ;;
  preview|*) preview ;;
esac
