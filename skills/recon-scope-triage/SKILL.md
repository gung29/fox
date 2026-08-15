---
name: recon-scope-triage
description: Recon-scope triage — rank enumerated assets/leads into a prioritized attack queue. Use after broad recon/subdomain/OSINT, before deep exploitation. Classifies assets by exposure, valuability, and attack-surface fit so Fox hits the highest-yield target first instead of burning time on low-value noise. Zero-gate — decision is throughput, not permission.
version: 1.0.0
---

# recon-scope-triage — Prioritize the Attack Queue

Goal: from >100 recon items → top 5 attack paths, fast.

## 1 — Ingestion
Collect from: `recon-and-methodology`, `offensive-osint`, subdomain/discovery tools (amass/subfinder/httpx), dorker output. Normalize into: host / port / service / tech / auth-level captured / notes.

## 2 — Classification matrix
Score each asset 1-5 on:
- **Exposure** (is it internet-reachable, dev-stage, /admin-flagged?)
- **Valuability** (data/creds inside? domain controller? payment? PII?)
- **Crackability** (weak tech, old version, well-known CVE?)
- **Depth** (can it pivot to more? /privilege/ vault? VPN? cloud?)

Queue = `exposure × valuability × crackability` + pivot bonus.

Priority buckets:
| Tier | Means |
|---|---|
| P0 | exposed high-value (admin panel, login, cloud console) |
| P1 | interesting (API, dev env, VPN, S3/cloud assets) |
| P2 | low (static site, CDN-only, no auth) |
| Drop | dead (404, non-app, honeypot) |

## 3 — Scope clamp
- Confirm in-scope (subdomain root + % any). Tag every item `in-scope` / `looks-OOS`.
- Move OOS items to a `lead/out-of-scope` file (see `evidence-hygiene` rebuttal) — don't delete them, just don't ACT.

## 4 — Emit the queue
Produce ordered list for the engagement: top-5 targets + why + first action per target (the skill to load).
```
[P0] https://login.corp.com (admin, O365 SPF) -> m365-entra-attack
[P0] https://vpn.corp.com/login (FortiGate 6.4) -> ssovpn-attack
[P1] api.staging.corp.com (GraphQL introspection open) -> graphql-and-hidden-parameters
```
Feed `fox.sh new <target>` + `recon-add` to persist.

## 5 — Re-triage
After each wave of findings, re-rank (new P0s emerge). Never stall on a stale queue.

## Integration
- Runs right after RECON (kill-chain phase 1-2), before WEAPONIZE.
- Output consumed by `root-agent` orchestration for parallel assignment.
