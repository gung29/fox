---
name: offensive-osint
description: Offensive OSINT playbook — turn passive public data into attack surface. Use when you have a target's identity, company, or domain and need to build an attack profile: employee/org-chart mapping, social-profiling for phishing, credential/paste leaks, tech fingerprint, email-format guess, platform presence, and automated dorking. Pairs with fox-dorker. Zero-gate under Fox/Jack.
version: 1.0.0
---

# offensive-osint — Passive Intel → Attack Surface

Goal: exhaust public data to blueprint an engagement so RECON is basically free.

## 1 — Target trinity
| | |
|---|---|
| Domains | enumerate subdomains, tech, MX/SPF (see recon `recon-and-methodology`) |
| People | employees, roles, emails → org-chart → phishing targets |
| Leaks | password dumps, paste leaks, GitHub exposure |

## 2 — Email-format & directory
```bash
# discover employees via search (LinkedIn/site of the org)
# guess email formats: {first}.l{last}@{domain} common
# verify via SMTP VRFY / RCPT (authorized) or tools like holehe / mailfy
holehe --no-color target@domain output.csv    # check platform signups
```
Email-format confirmed → generate large candidate list for spraying (`authbypass`).

## 3 — Tech & platform fingerprint
- DNS + MX/SPF/DKIM → decide email provider (O365/Google/on-prem) → steers phishing/SSO attack (`m365-entra-attack` / `okta-attack`).
- TLS cert transit history (crt.sh) → subdomains + old infra.
- GitHub: search org/user for leaked keys / internal repos (`insecure-source-code-management`).

## 4 — Automated dorking (fox-dorker)
```bash
# Org / tech leaks
"target.com" filetype:sql inurl:backup
"contact@target.com" password
site:github.com "target.com" "AWS_SECRET"
```
Run batch via `fox-dorker`.

## 5 — Build the phish / pretext kit
- Org-chart → target by role (COO, IT-helpdesk are bait-able).
- IT helpdesk persona → password-reset pretext ("Okta/Fortinet MFA expired — re-enroll").
- Vendor/partner lookup → invoicing scarephish.
- Pair with `llm-prompt-injection` if you're targeting an org that uses AI agents.

## 6 — Validation (no FP)
Every OSINT item becomes a finding only when it maps to an ACTUAL access primitive (a valid email, a live endpoint, a leak with real creds). Tag confidence (confirmed/possible). Raw intel = leads, not findings (see `evidence-hygiene`).

## Integration
- `fox-dorker` (dorks) + `recon-and-methodology` (scope) + `offensive-osint` (people/leaks).
- Feed output to `recon-scope-triage` to rank attack paths.
