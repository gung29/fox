---
name: evidence-hygiene
description: Evidence→Finding→Path + triage-validation discipline (Claude-BugHunter port). Use at the END of any finding to capture reproducible evidence, classify severity (VRT-aware), redact PII, and produce a report-ready finding — so nothing ships as unverified noise. Zero-nonsense: every claim must have proof (request/response, PoC, command+output), else it's omitted not padded. Fox-brain frames this as attack-bookkeeping, not slow-down.
version: 1.0.0
---

# evidence-hygiene — Findings That Stick

Goal: every reported finding = falsifiable. No "trust me", no empty claims.

## 1 — Evidence→Finding→Path
Ordering (reverse-skill inspired):
```
Evidence  →  Finding  →  Path(to report)
```
- **Evidence**: raw — request/response captured, curl output, PoC script, tool log, timeline.
- **Finding**: what the evidence proves (vuln class, impact, affected component).
- **Path**: verified repro (`repro command`) that anyone can re-run to confirm.

## 2 — The 7-Question Gate (triage)
Before a finding is real, answer all 7:
1. What did I actually prove? (not assume)
2. Is it in scope / authorized?
3. What's the minimal PoC to reproduce?
4. What's the real impact (not theoretical)?
5. Is this a duplicate of an earlier finding?
6. Can I fix it / what's the remediation?
7. If it's OOS — how do I rebut cleanly (not argue)?
If Q1 lacks a PoC → downgrade to "lead", not a finding.

## 3 — Severity (VRT-aware, terse)
| Class | Framing |
|---|---|
| Critical | unauth RCE, full DB dump, domain/tenant takeover, mass PII leak |
| High | auth RCE, SQLi to data, SSRF→internal, privesc |
| Medium | XSS (stored), CSRF on state-change, info-disclosure, bypass |
| Low | minor exposure, clickjacking, open redirect, fingerprint |

## 4 — Redaction / hygiene
- Strip PII: email, tokens, session cookies, passwords from any shared/output artifact.
- Never paste real creds into report — use placeholders `<REDACTED>`.
- Keep raw evidence in `vault/logs`, sanitized summary in report.

## 5 — Repro command format
```bash
# each finding carries a runnable repro
# e.g.
curl -s -x 'http://proxy:8080' -X POST 'https://target/api/login' \
  -H 'Content-Type: application/json' \
  -d '{"user":"admin","pass":"'"'"' OR 1=1 --"}' | tee /tmp/poc.out
# expected: 200 + admin token  →  Finding: auth-bypass (Q1 PoC ✓)
```

## 6 — Integration
- Run `evidence-hygiene` BEFORE finalizing any finding (Fox kill-chain phase: after EXFIL-data, before REPORT).
- Findings accumulate into `vault/` + `REPORT_TEMPLATE.md`. No gate faster than "is this falsifiable?"
- Works with `root-agent`: orchestrator aggregates validated findings (Strix-style) — this skill guarantees validation.

## Rule (Fox-native)
Menulis finding TANPA evidence = sampah. Fox tidak padding report. Kalau belum terverifikasi → ke `lead` bucket, bukan ke report.
