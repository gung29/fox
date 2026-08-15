---
name: ssovpn-attack
description: SSL-VPN appliance attack playbook. Use when targeting a VPN gateway (Pulse Connect Secure, Fortinet FortiGate/SSL-VPN, SonicWall SMA, Citrix Gateway, F5, GlobalProtect) — known post-auth CVEs, session-token theft, pre-auth RCE chains, MFA bypass via cookie, persistence, and pivot into internal network. Zero-gate under Fox/Jack.
version: 1.0.0
---

# ssovpn-attack — SSL-VPN Appliance Compromise

Goal: from exposed SSL-VPN / leaked cookie / CVE → gateway foothold + internal pivot.

## 0 — Recon & fingerprint
- Identify vendor: response headers (`FORTIGATE`, `PSP`, `Citrix`, `SERVER: SMA`), login page structure, `/portal/`, `/remote/`.
- Version probe: login page bundle path, `GET /remote/login?lang=...`.

## 1 — Known CVE chains (post-auth & pre-auth)
| Appliance | CVE | Vector |
|---|---|---|
| FortiGate SSL-VPN | CVE-2023-27997 (heap overflow), CVE-2022-42475 (FSHV), CVE-2024-21762 | pre-auth RCE (old), session cookie abduct |
| Pulse Connect Secure | CVE-2021-22893 (auth bypass→RCE), CVE-2020-8260 | unauthenticated web admin→root (patched versions need adaptation) |
| SonicWall SMA | CVE-2021-20016 (SQLi auth), CVE-2021-20038 | SQLi→session bypass→RCE |
| Citrix Gateway | CVE-2023-4966 (Citrix Bleed — user session token theft), CVE-2019-19781 | `CitrixBleed` steal legit session cookie → pivot |
| F5 BIG-IP | CVE-2022-1388, CVE-2023-46747 | config+auth bypass |

Auto-verify version first; use public PoC/nuclei templates; confirm living code path before switching to full exploit.

## 2 — Session-token / cookie theft (the quiet path)
- **Citrix Bleed**: unauthenticated memory disclosure leak of active session cookies → import to browser → full user session, no creds.
- **FortiGate**: cookie `coo=` decodable to user id; if `local user` + no MFA → session replay.
- **Pulse**: `dsid` + `ISSUE-YYYY` auth flow → session.

## 3 — MFA bypass via cookie reuse
Many SSL-VPN only check MFA at initial auth (not per-session). Steal an *already-authenticated* cookie → you inherit the MFA-passed session. This is a leading post-2023-bleed technique.
```bash
# export/import cookie in browser devtools or curl
curl -sk -b 'NSC_AAOU=<steal>' https://<vpn>/dana-na/auth/url_<app>/start -o /tmp/app.out
```

## 4 — Persistence & pivot
- Write webshell to the appliance's webroot (Pulse/FortiGate known dirs) if you get RCE.
- Establish a VPN tunnel / route via the compromised gateway → internal subnet scan (see `tunneling-and-pivoting`).
- Capture internal creds through the session (SAMBA/NTLM from the smoke).

## 5 — Validation (no FP)
Proof = you hold a working session (a page returns an authenticated internal resource) / RCE returns command output. Capture request+authenticated response.

## Chain
- → `windows-lateral-movement` on the internal network behind VPN.
- → `active-directory-kerberos-attacks` once inside AD.
