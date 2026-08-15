---
name: bug-bounty-workflow
description: Bug-bounty / bugcrowd / hackeron automa auto-reporting workflow — take validated findings (evidence-hygiene) and turn them into platform-ready submissions: VRT-aware severity, repro steps, impact, remediation, evidence sanitization, and rate/scope compliance. Runs the REPORT_TEMPLATE + vault into a polished deliverable. Zero-gate under Fox/Jack; focuses on payout-grade output.
version: 1.0.0
---

# bug-bounty-workflow — From Finding to Payout

Goal: validated findings → submission that gets accepted (no triage reject).

## 1 — Input contract
Consume from `evidence-hygiene` (falsifiable findings) — each must have:
- working PoC / repro command
- severity (Critical/High/Medium/Low VRT-aware)
- affected endpoint/asset + in-scope confirmation

## 2 — The Python template (REPORT_TEMPLATE.md via fill)
Per finding, produce:
```
### [SEV] Title (CWE-###)
- **Asset**: <url/endpoint>
- **Repro**:
  1. <step> → <result>
  2. <step> → <result>   (must be copy-pasteable)
- **Impact**: <what attacker gets: data/compromise>
- **Fix**: <remediation, VRT convention>
- **Evidence**: <sanitized request/resp or screenshot ref>
```
Fill `REPORT_TEMPLATE.md` fields per finding.

## 3 — Platform mapping
| Platform | Severity model | Extra required |
|---|---|---|
| HackerOne | CVSS v3/v4 + weakness (CWE) | impact statement, disclosed info |
| Bugcrowd | VRT priority + CVSS | reproducible steps, OWASP category |
| Intigriti | CVSS + business impact | PoC, language fixes |
Auto-map from `evidence-hygiene` severity → platform field.

## 4 — Sanitization (before submit)
- Strip PII (creds, tokens, cookies, real names) → `<REDACTED>` (see `evidence-hygiene`).
- Remove any internal IPs/hostnames out-of-scope.
- Ensure repro uses authorized-only endpoints.

## 5 — Evidence packaging
- Attach: sanitized request/response (curl), minimal PoC, screenshot (if UI-based).
- Name files `finding-<cwe>-<short>.{md,txt,png}`.

## 6 — Compliance & rate
- Keep within program scope: no active scanning beyond in-scope.
- Respect rate limits; chain findings (don't spam duplicates).
- Use `recon-scope-triage` ranking to prioritize highest-payout finding first.

## 7 — Report handoff
- Assemble into `REPORT_TEMPLATE.md` output → ready to paste into H1/Bugcrowd/Intigriti.
- Pair with `standalone-fixer` if the program wants a patch suggestion.

## Integration
- Runs at EXFIL→REPORT (post `evidence-hygiene`).
- `fox.sh stash` / vault keep the sanitized evidence.
