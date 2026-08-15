---
name: cloud-iam-deep
description: Cross-cloud IAM attack & privesc playbook (AWS / GCP / Azure). Use when inside a cloud account — metadata endpoint SSRF→keys, role chaining, over-privileged IAM roles, identity pool, service account abuse, container/pod identity, and lateral to other accounts/providers. Zero-gate under Fox/Jack.
version: 1.0.0
---

# cloud-iam-deep — Cloud IAM Takeover (AWS / GCP / Azure)

Goal: from a single leaked key / metadata hit / service account → cloud-privilege domination.

## 0 — Discovery (keys & identity)
- Metadata endpoints (if SSRF/VM):
  - AWS: `http://169.254.169.254/latest/meta-data/iam/security-credentials/` 
  - GCP: `http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/` (header `Metadata-Flavor: Google`)
  - Azure: `http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=...` (header `Metadata: true`)
- Hunt keys: `.env`, cloud-init `user-data`, git history (see `insecure-source-code-management`), env vars.

## 1 — Enumerate identity & permissions (AWS)
```bash
# whoami / get-caller-identity
aws sts get-caller-identity
# list roles you can assume
aws iam list-roles | jq -r '.Roles[].RoleName'
# check your policies (or brute via Access Analyzer)
aws iam list-attached-user-policies --user-name $USER
# enumerate assets you can read/write
aws s3 ls; aws ec2 describe-instances; aws rds describe-db-instances
```

## 2 — Privilege escalation (AWS)
| Path | Method |
|---|---|
| PassRole → Lambda/EC2 | `iam:*PassRole` + `lambda:CreateFunction` → run role-privileged code |
| CreateAccessKey | `iam:CreateAccessKey` on a privileged user/role → inherit |
| AttachUserPolicy | `iam:Attach*` → self-admin |
| UpdateAssumeRolePolicy | edit trust policy → assume any role |
| sts:AssumeRole with `SessionTags` | if allowed, escalate effective policy |

## 3 — GCP escalation
- Service account key export: `iam.serviceAccountKeys.create` → add a key for a privileged SA.
- `iam.roles.update` → set permissions on a role you hold.
- `compute.instances.setMetadata` → inject startup script (runs as SA) on an instance.
- Kubernetes → read secrets / SA token (tie to `kubernetes-pentesting`).

## 4 — Azure escalation
- Privileged Role assignments: `Microsoft.Authorization/roleAssignments/write` → self-global-admin.
- Managed identity: obtain MSI token, use to authenticate as the resource.
- Key Vault secret read if `KV` delegation permits.
- AAD→ARM chain via `Microsoft.AAD` / `AzureAD` (tie to `m365-entra-attack`).

## 5 — Lateral & exfil
- s3/rclone to an attacker bucket (authorized range), GCS, Azure blob; or use `s3 cp` to staging.
- Plant in an over-privileged identity → move across accounts (org units) via `sts:AssumeRole`.

## 6 — Validation (no FP)
Proof = you accessed a resource governed by a privilege you were NOT entitled to (list/show/download). Capture the call + returned data; establish the denied→allowed boundary.

## Chain
- → `ssrf-server-side-request-forgery` to GET the metadata keys if you came from an app.
- → `m365-entra-attack` if Azure AD tenant is reachable; `kubernetes-pentesting` if cluster.
