# FOX VAULT — Master Index

## Structure
```
vault/
├── targets/          # Per-target credential inventory
├── combos/           # email:password dumps
├── hashes/           # Hash dumps (NTLM, SHA, bcrypt, etc.)
├── intel/            # CVE/exploit intel cache (cve-intel-weaponizer)
├── keys/             # SSH keys, SSL certs, PGP keys
├── sessions/         # Active session cookies
├── cracking/         # hashcat rules, cracked hashes
└── logs/             # Audit trail of extraction events
```

## Target File Format (`targets/[target-name].md`)
```markdown
# Target: [Name]
# Domain: [domain]
# Owned: [date]
# Access: [level]

#### Credentials Found
| Type | Username/Email | Password/Hash | Source | Service |
```

## Rules
- Every cred goes straight to vault
- Dedup on arrival
- Tag by source
- Categorize by type
- Hash → crack → store plaintext in combos/
