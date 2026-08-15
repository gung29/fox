#!/bin/bash
# ============================================================
#  FOX TOOL-INDEX bootstrapper
#  Port + modifikasi dari reverse-skill refresh-tool-index /
#  cybersec-toolkit tool-registry. Menulis tool-index.md + json
#  sehingga Fox tahu tool mana yang SUDAH ada (tidak install ulang)
#  dan mana yang BISA di-`bootstrap` bila perlu.
#  Cross-platform: Linux / macOS / WSL / Git-Bash. Windows native -> fox-toolindex.ps1
#
#  Usage:  bash skills/fox-toolindex.sh          (generate)
#          FOX_TOOLS="extra1,extra2" bash skills/fox-toolindex.sh   (override scan)
# ============================================================
set -euo pipefail

# --- tools yang kita kenal; beri 'yes' bila binary / file ada di PATH ---
declare -a TOOLS=(nmap masscan ffuf feroxbuster gobuster dirb john hashcat sqlmap
  sqlite3 curl wget python3 node npm jadx apktool frida adb ghidra objdump readelf
  strace ltrace gdb radare2 r2 pwntools nc ncat socat proxychains ssh scp openssl
  dig nslookup host whois subfinder amass httpx nuclei dalfox commix tplmap arjun
  katana gau parametizer msfconsole msfvenom metasploit mimikatz powershell docker)

outdir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
index_md="$outdir/tool-index.md"
index_json="$outdir/tool-index.json"

> /tmp/foxi.txt
echo "scanning $(uname -s) ..."
for t in "${TOOLS[@]}"; do
  if command -v "$t" >/dev/null 2>&1; then
    echo "yes	$t	$(command -v "$t")" >> /tmp/foxi.txt
  else
    echo "no	$t	" >> /tmp/foxi.txt
  fi
done

# --- build markdown ---
{
  echo "# FOX Tool-Index (auto-generated)"
  echo "# Tools marked 'yes' tersedia; 'no' bisa di-bootstrap (online) atau install manual."
  echo
  printf '%-12s %-16s %s\n' "status" "tool" "path"
  printf '%-12s %-16s %s\n' "------" "----" "----"
  while IFS=$'\t' read -r st t p; do
    printf '%-12s %-16s %s\n' "$st" "$t" "$p"
  done < /tmp/foxi.txt
} > "$index_md"

# --- build json ---
python3 - "$index_json" <<'PY'
import json, os, sys
data = {}
for line in open('/tmp/foxi.txt'):
    line=line.rstrip('\n')
    if '\t' not in line: continue
    st,t,p = line.split('\t')
    data[t] = {"available": st=="yes", "path": p or None}
json.dump(data, open(sys.argv[1],'w'), indent=2)
PY

yes="$(grep -c '^yes' /tmp/foxi.txt)"
no="$(grep -c '^no' /tmp/foxi.txt)"
echo "[+] wrote $index_md ($yes tersedia / $no belum)"
echo "[+] wrote $index_json"
