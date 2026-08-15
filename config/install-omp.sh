#!/bin/bash
# ============================================================
#  FOX — oh-my-pi (omp) harness adapter
#  Writes ~/.omp/agent/models.yml + settings.json persona/role
#  Usage:
#    ./install-omp.sh [apply]     # apply = write live config (default: dry-run preview)
#    ./install-omp.sh --help
# ============================================================
set -euo pipefail

FOX_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OMP_HOME="${OMP_HOME:-$HOME/.omp}"
OMP_AGENT="$OMP_HOME/agent"
MODELS_YML="$OMP_AGENT/models.yml"
SETTINGS_JSON="$OMP_AGENT/settings.json"
PERSONA_FILE="$FOX_REPO/config/fox-persona.md"
MODE="${1:-preview}"

# --- role → model mapping (tuned for gacor) -----------------
# Default roles omp understands: default / smol / slow / plan / commit
write_models_yml() {
  cat > "$MODELS_YML" <<EOF
# FOX router — role → model tiering (edit freely)
models:
  default:
    provider: naraya
    id: deepseek-v4-flash
  smol:            # quick / cheap tasks
    provider: naraya
    id: mistral-medium-3-5
  slow:            # deep reasoning
    provider: aerolink
    id: claude-opus-4-6
  plan:            # architecture / planning
    provider: dahono
    id: dahono/claude-sonnet-4.5-thinking-agentic-free
  commit:          # git commit message generation
    provider: 9router
    id: hunter
EOF
  echo "[+] wrote $MODELS_YML"
}

write_settings_persona() {
  # inject Fox persona into settings.json (personality/system_prompt if supported)
  local persona
  persona="$(cat "$PERSONA_FILE" 2>/dev/null || echo "Fox #PERSONA_MISSING#")"
  if [ -f "$SETTINGS_JSON" ]; then
    # non-destructive: back up, then try to add persona field via python
    cp "$SETTINGS_JSON" "$SETTINGS_JSON.bak-$(date +%s)"
  fi
  python3 - "$SETTINGS_JSON" "$persona" <<'PY'
import json, os, sys
path, persona = sys.argv[1], sys.argv[2]
data = {}
try:
    data = json.load(open(path)) if os.path.exists(path) else {}
except Exception:
    data = {}
data.setdefault("persona", {})
data["persona"]["fox"] = persona
json.dump(data, open(path, "w"), indent=2)
print(f"[+] persona injected -> {path}")
PY
  return 0
}

case "$MODE" in
  apply)
    echo "==> FOX · oh-my-pi adapter (APPLY)"
    [ -d "$OMP_AGENT" ] || mkdir -p "$OMP_AGENT"
    write_models_yml
    write_settings_persona
    echo "==> done. restart omp/gateway for changes."
    ;;
  preview|--help|-h|*)
    echo "==> FOX · oh-my-pi adapter (PREVIEW)"
    echo "  will write:"
    echo "    $MODELS_YML      (router roles)"
    echo "    $SETTINGS_JSON   (fox persona)"
    echo "  persona source: $PERSONA_FILE"
    echo
    echo "  RUN:  ./install-omp.sh apply"
    echo "  NOTE: prior settings.json is backed up first (never clobbered)."
    ;;
esac
