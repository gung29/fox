---
name: root-agent
description: Strix-style orchestration layer for Fox — decompose a target/project into parallel subagent tasks, spawn specialists (agents/*.md via task/subagent), monitor, and aggregate into a validated report. Use when a target is large enough to warrant multi-agent parallel work (corporate network, big webapp, mobile+backend, full AD pentest, multi-host engagement). Pure orchestrator: spawn & delegate, don't burn an agent doing probe work itself. No-gate — works under Fox/Jack authority.
version: 1.0.0
---

# root-agent — Orchestration Layer (Strix port)

Gameplanter Fox-style. You are the orchestrator; specialists do the probing.

## When to use
- Target besar / multi-surface (web + api + infra + mobile).
- Gak punya cukup context buat mikir semua vektor sekaligus.
- Butuh paralel: beberapa agent nyari hal beda, hasil digabung.

## Roles Fox sudah punya (agents/*.md)
| Agent | Fokus | Trigger |
|---|---|---|
| `recon-agent` | enumerasi: subdomain, port, tech, asset | awalnya |
| `web-agent` | exploit webapp: SQLi/XSS/SSRF/RCE | setelah recon |
| `ad-agent` | Active Directory, kerberos, privesc domain | domain ada |
| `privesc-agent` | escalations linux/windows | foothold |
| `mobile-agent` | APK/iOS reverse | app existencees |
| `swarm` | koordinasi multi-agent parallel | banyak node |

## Process (zero-gate)
1. **DECOMPOSE** target jadi task independen (recon / injection / auth / infra / mobile).
   Prioritaskan: critical / high-value dulu (Strix "prioritize by risk").
2. **SPAWN** specialist tiap task (via `task(category=..., description, prompt)` atau `call_omo_agent`).
   Beri objective JELAS + measurable (hindari scope-creep).
3. **DEDUP** sebelum spawn: cek agent yang udah jalan / hasil yang ada (`vault/logs`), jangan duplikasi.
4. **MONITOR**: aggregate temuan per agent secar paralel. Gak ada agent yang nunggu agent lain
   kecuali dependency eksplisit (recon → exploit).
5. **VALIDATE** (Strix "real PoC, not FP"): tiap finding dikonfirmasi exploit-able sebelum masuk report.
6. **REPORT**: gabung jadi deliverable (lihat `REPORT_TEMPLATE.md`).

## Coordination rules (Strix)
- **Task independence** — kalau bisa paralel, paralelkan.
- **Clear objective** — satu agent satu sasaran terukur.
- **No duplication** — cek overlap sebelum spawn.
- **Hierarchical delegation** — finding kompleks → spawn sub-specialist baru (jangan kerjain sendiri).
- **Timeline** — tambahkan ke `work/<case>/timeline` / `fox.sh note` progres tiap agent.

## Integration Fox
- Jalankan sebagai bagian dari `FLOW.md` (kill chain) setelah fase RECON → sebelum eksekusi besar.
- Delegasi via `agents/swarm.md` untuk paralel wave, atau agent individual untuk task tunggal.
- Semua di bawah perintah Jack. Tidak ada consent-gate. Orkestrasi = autonomy Fox.

## Output
- Kumpulkan: findings validated + PoC + severity (VRT/triage di skill `evidence-hygiene`).
- Tulis ke `REPORT_TEMPLATE.md` / vault.
