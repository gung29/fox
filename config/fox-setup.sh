#!/bin/bash
# ============================================================
#  FOX SELF-BOOTSTRAP — one-shot auto-install (Opsi B engine)
#  Dipanggil oleh AI-agent harness (via AI-INSTALL.md prompt)
#  atau manual:  bash config/fox-setup.sh
#
#  Melakukan SEMUA setup Fox tanpa interaksi:
#    1. auto-detect harness (opencode/omp/hermes) + OS (linux/win-bash)
#    2. apply persona + router + SOUL + prefill (lewati config/install-fox.sh)
#    3. buat struktir ~/.fox local (vault/multibrain) ala bootstrap/setup.sh
#    4. verifikasi hasil — lapor ringkas
#
#  Aman: setiap target backup dulu; idempotent (bisa dijalankan ulang).
# ============================================================
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_DIR="${HOME:-$USERPROFILE}"
FOX_LOCAL="$HOME_DIR/.fox"
LOG=""
VERBOSE="${FOX_SETUP_VERBOSE:-0}"

log()  { echo "  $*"; }
info() { echo "[·] $*"; }
ok()   { echo "[✓] $*"; }
warn() { echo "[!] $*"; }

detect_os() {
  case "$(uname -s 2>/dev/null || echo Windows)" in
    Linux*)  echo linux ;;
    Darwin*) echo macos ;;
    MINGW*|MSYS*|CYGWIN*) echo windows-gitbash ;;
    *)       echo windows ;;
  esac
}

harness_present() {
  # $1 = command or config-dir marker
  local probe="$1"
  command -v "$probe" >/dev/null 2>&1 && return 0
  [ -e "$HOME_DIR/.$probe" ] && return 0
  [ -e "$HOME_DIR/.config/$probe" ] && return 0
  return 1
}

setup_local_structure() {
  info "struktur local ~/.fox"
  mkdir -p "$FOX_LOCAL"/{vault/{targets,combos,hashes,tokens,keys,sessions,cracking,logs},multibrain/{indexes,context},training}
  for d in vault targets combos; do :; done
  [ -f "$FOX_LOCAL/vault/master-index.md" ]   || printf '# FOX VAULT — Master Index\n' > "$FOX_LOCAL/vault/master-index.md"
  [ -f "$FOX_LOCAL/multibrain/session.md" ]   || printf '# MultiBrain Session — Fox\n\n## Active Ops\n(None)\n' > "$FOX_LOCAL/multibrain/session.md"
  [ -L "$FOX_LOCAL/skills" ] || ln -s "$REPO/skills" "$FOX_LOCAL/skills" 2>/dev/null || true
  ok "struktur ~/.fox siap"
}

apply_harnesses() {
  local os="$1"
  info "menerapkan Fox ke harness terdeteksi (OS=$os)"
  if [ "$os" = "windows" ]; then
    # pure-Windows native: jalankan PowerShell installer
    pwsh -NoProfile -File "$REPO/config/install-fox.ps1" -Apply 2>/dev/null \
      || powershell -ExecutionPolicy Bypass -File "$REPO/config/install-fox.ps1" -Apply
  else
    # linux/macos/windows-gitbash: bash installer
    bash "$REPO/config/install-fox.sh" apply
  fi
}

verify() {
  info "verifikasi"
  [ -f "$FOX_LOCAL/multibrain/session.md" ] && ok "session.md ada"
  local n
  n=$(find "$REPO/skills" -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
  ok "$n skills terdaftar di repo"
  # per-harness spot check
  [ -f "$HOME_DIR/.hermes/SOUL.md" ] && ok "hermes SOUL.md Fox"
  grep -q "personality: fox" "$HOME_DIR/.hermes/config.yaml" 2>/dev/null && ok "hermes personality:fox"
  [ -f "$HOME_DIR/.omp/agent/models.yml" ] && ok "omp models.yml Fox"
  if [ -d "$HOME_DIR/.config/opencode" ] || [ -d "$HOME_DIR/.opencode" ]; then
    ok "opencode config dir ditemukan (agent.fox diterapkan oleh installer)"
  fi
}

main() {
  local os
  os="$(detect_os)"
  echo "==> FOX SELF-BOOTSTRAP (Opsi B) — OS=$os"
  setup_local_structure
  apply_harnesses "$os"
  verify
  echo
  ok "FOX TERINSTAL. /!\\ JACK'S WORD IS LAW."
}

main
