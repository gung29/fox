---
name: fox-dashboard
description: Jack-Dashboard / C2-lite — live HTML panel over the Fox operations directory. Use when you want to visualize active targets (TARGET.md + recon/vulns/creds/payloads/loot/exploits counts) in a browser, or run a watch hook that fires when a target changes. Zero-dependency (stdlib http.server). Usage: python skills/fox-dashboard.py --ops <ops> [--port 8080] [--notify hook.sh].
version: 1.0.0
---

# fox-dashboard — Jack-Dashboard / C2-lite

## Start
```bash
python skills/fox-dashboard.py --ops $FOX_HOME/operations --port 8080
# browse http://localhost:8080
```

## Notify hook (target change → script)
```bash
python skills/fox-dashboard.py --ops $FOX_HOME/operations --notify /path/hook.sh
```
hook.sh gets called `<hook "target" changed>` on any change to a target dir mtime.

## One-shot scan (no server)
```bash
python skills/fox-dashboard.py --ops $FOX_HOME/operations --interactive-only
```

## Integration
- Complements `fox.sh status` (terminal) with a web view.
- Useful for a small monitoring pane / "war room" while an engagement runs.
- Pair with `harness-evasion` to shut the panel after op if you don't want it exposed.
