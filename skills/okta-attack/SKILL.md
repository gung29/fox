---
name: okta-attack
description: Okta SSO / Workforce Identity attack playbook. Use when targeting an org on Okta — API key / token abuse, super-admin & admin-role escalation, substring/group rules, delegation abuse, MFA bypass, impersonation, post-auth session hijack, and chain to connected apps (SaaS, AWS, VPN). Zero-gate under Fox/Jack.
version: 1.0.0
---

# okta-attack — Okta Tenant & SSO Takeover

Goal: from leaked Okta API token / admin creds / SSO session → super-admin + connected-app access.

## 0 — Recon
- Determine if target is Okta: response headers (`X-Okta-Request-Id`), login `okta.com/...`, `.well-known/openid-configuration`.
- Org URL typically `https://<subdomain>.okta.com` or custom domain.
- Enumerate: okta user brute (no lockout on some), `samaccountname`, admin-related endpoints.

## 1 — Attack vectors
- **API token theft**: leaked `nnn...` (SSWS token) → full API. `Authorization: SSWS <token>`.
- **Admin creds**: spray on super-admin; many orgs have straddling admin accounts.
- **Subdomain takeover / custom-domain**: dangling CNAME for org's custom domain → takeover → intercept SSO (see `subdomain-takeover`).
- **Login/opend redirect via delegation**: `?redirect_uri=` chain to attacker callback.

## 2 — Privilege escalation (→ Super Administrator)
| Path | Method |
|---|---|
| Admin role assignment | with `OKTA_SWAP_ADMIN` or `users.lifecycle` == an admin app token → grant self `OKTA_ADMIN_GROUP` |
| Group rule injection | `groups/rules` — create rule `user.name matches "*" → add to all-admins` then it processes automatically |
| API token with admin perms | create a NEW SSWS token with `super_admin` scope |
| Delegation | OIDC delegation / app link authorization → impersonate another admin |
| Session | steal admin Okta session cookie → replay (fix `sid`, `sid_claimer`) |

### Admin role titles (escalation target)
`SUPER_ADMIN`, `APP_ADMIN`, `USER_ADMIN`, `HELP_DESK_ADMIN`, `READ_ONLY_ADMIN`, `API_ACCESS_MANAGEMENT_ADMIN`.

## 3 — Post-auth chain (connected apps — the real damage)
- With SUPER_ADMIN → reset any user's password or enact **sudo (step-up)** then:
  - reset phishing / disabled / service accounts to re-enter every SaaS tied to SSO.
  - impersonate via `on_login_success` → SWA / OIDC flows → AWS Console, Zoom, Slack, GitHub, VPN.
- AWS: use Okta->AWS role assumption (SAML) → inherit cloud (then `cloud-iam-deep`).

## 4 — Session / token ops
```bash
# valid token test
curl -s -H "Authorization: SSWS $TOKEN" 'https://<org>.okta.com/api/v1/users?limit=1' -o /tmp/ok.out -w "%{http_code}\n"
# list admins
curl -s -H "Authorization: SSWS $TOKEN" 'https://<org>.okta.com/api/v1/roles?limit=200'
```

## 5 — Validation (no FP)
Proof: API call returns another user's record (enumeration = real if beyond your own), or you can MINT a session (`/authn` with reset creds). Capture token→200 JSON.

## Chain
- → `cloud-iam-deep` for AWS/Azure behind Okta.
- → `saml-sso-assertion-attacks` if you get to forge/relay assertions.
