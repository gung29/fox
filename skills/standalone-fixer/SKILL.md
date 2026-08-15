---
name: standalone-fixer
description: Auto-fix / remediation generator — from a validated vulnerability finding produce a concrete patch or hardening recommendation (patch diff, config fix, dependency bump, WAF rule). Strix 'Auto-fix & reporting' pattern. Use when a program/owner wants remediation alongside the PoC, or when you want to demonstrate impact-to-fix. Zero-gate: output is actionable, not opinion.
version: 1.0.0
---

# standalone-fixer — From Finding to Patch

Goal: evidence → concrete fix a team can apply.

## 1 — Input
A validated finding (from `evidence-hygiene`) with the vulnerable code/config/endpoint.

## 2 — Fix templates by class
| Vuln | Canonical fix |
|---|---|
| SQLi | parameterized queries / prepared statements; input validation; least-privilege DB role |
| XSS | context-aware output encoding; CSP; sanitizer; no `innerHTML` with user data |
| SSRF | block private IP ranges; allowlist hosts; no raw URL from user; SSRF guard (e.g. SSRFMap) |
| IDOR | object-level auth check; server-side ownership; UUIDs not sequential guessable |
| Auth bypass | server-side session/role check; MFA everywhere; never trust client |
| Upload | allowlist extensions + MIME; server-side magic-byte check; store outside webroot; random filename |
| Deserialization | safe deserializers; allowlist classes; no pickle/unserialize of untrusted |
| CORS | no `Access-Control-Allow-Origin: *` with creds; reflect only trusted origins |
| JWT | validate `alg` header + key; short expiry; no `none`; proper secret |
| Command inj | no shell with unsanitized input; use exec-array; allowlist; sandbox |

## 3 — Output formats
- **Patch diff**: minimal `git diff` style — show BEFORE/AFTER lines.
- **Config fix**: exact line changes (nginx/apache/app config).
- **Dependency bump**: package.json / requirements.txt / pom version.
- **WAF/guard rule**: a rule that blocks the payload class (e.g. regex/ModSecurity/Cloudflare rule).

## 4 — Verify the fix (no FP on both sides)
- Suggest the fix only when you can REASON it closes the vector (address root cause, not symptom).
- Where possible, note the regression test that would catch a re-introduction.
- Don't propose fixes for things you didn't actually exploit (guesswork = noise).

## 5 — Deliverable
Wrap into `REPORT_TEMPLATE.md` "Fix" section + a `fixes/<finding-id>.patch`/`.conf` file for handoff.
Pair with `bug-bounty-workflow` for the full submit package.

## Integration
- Runs after `evidence-hygiene` when owner/program wants remediation.
- Part of Fox kill-chain finalize (REPORT).
