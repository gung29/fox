#!/usr/bin/env python3
"""fox-dashboard.py — Jack-Dashboard / C2-lite panel (stdlib only, no deps).

Scans the Fox operations dir (operations/*/TARGET.md + subfolders) and serves a
live HTML panel. Optional --notify <script> runs a hook on changes (e.g. telegram).

Usage:
  python fox-dashboard.py --ops <FOX_HOME>/operations   [--port 8080] [--notify hook.sh]
  python fox-dashboard.py --interactive-only            # one-shot scan output
"""
import argparse, glob, html, json, os, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, unquote


def now_iso():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def scan_targets(ops_root):
    """Return list of {name, target_md, cnt, sub, files} for each target dir."""
    if not os.path.isdir(ops_root):
        return []
    out = []
    for d in sorted(glob.glob(os.path.join(ops_root, "*"))):
        if not os.path.isdir(d):
            continue
        name = os.path.basename(d)
        tmd = ""
        tmd_path = os.path.join(d, "TARGET.md")
        if os.path.exists(tmd_path):
            tmd = open(tmd_path, encoding="utf-8", errors="ignore").read(4000)
        counts = {}
        files = {}
        for sub in ["recon", "vulns", "creds", "payloads", "loot", "exploits"]:
            sp = os.path.join(d, sub)
            if os.path.isdir(sp):
                cnt = sum(os.path.getsize(os.path.join(r, f)) > 0
                          for r, _, fs in os.walk(sp) for f in fs)
                counts[sub] = cnt
                fl = [f for r, _, fs in os.walk(sp) for f in fs][:30]
                files[sub] = fl
        out.append({"name": name, "target_md": tmd, "counts": counts,
                    "files": files, "mtime": os.path.getmtime(d)})
    return out


def render_html(targets):
    rows = ""
    for t in targets:
        md = html.escape(t["target_md"]).replace("\n", "<br>")[:1200]
        subs = " ".join(f"<span class='sub'>{k}:{v}</span>"
                        for k, v in sorted(t["counts"].items()) if v)
        rows += (f"<div class='card'><h3>🦊 {html.escape(t['name'])}</h3>"
                 f"<div>{subs or '—'}</div><pre>{md}</pre></div>")
    stats = f"{len(targets)} target(s) · {time.strftime('%Y-%m-%d %H:%M:%S')}"
    return f"""<!doctype html><html><head><meta charset=utf-8><title>FOX Jack-Dashboard</title>
<style>
 body{{font-family:monospace;background:#0d0d12;color:#eee;margin:0;padding:20px}}
 h1{{color:#ef4444}} .card{{background:#16161e;border:1px solid #2a2a3a;border-radius:8px;padding:14px;margin:10px 0}}
 .sub{{display:inline-block;background:#1f1f2b;color:#7c6cff;padding:2px 8px;margin:2px;border-radius:4px}}
 pre{{white-space:pre-wrap;color:#9be7a0;font-size:12px}}
 .stat{{color:#888}} h3{{margin:0 0 8px}}
</style></head><body><h1>🐺 FOX — Jack-Dashboard</h1><div class='stat'>{stats}</div>{rows}</body></html>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        targets = scan_targets(self.server.ops_root)
        body = render_html(targets).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def watch(ops_root, notify, interval):
    """Poll ops_root; run notify hook when any target changes. Drop-in C2-lite watcher."""
    last = {}
    print(f"[*] watching {ops_root} (interval {interval}s) notify={notify}")
    while True:
        cur = {d: os.path.getmtime(os.path.join(d)) if os.path.exists(d) else 0
               for d in [os.path.join(ops_root, x) for x in os.listdir(ops_root)]
               if os.path.isdir(os.path.join(ops_root, x))}
        for d, m in cur.items():
            if last.get(d) is not None and m != last[d] and notify:
                name = os.path.basename(d)
                os.system(f'"{notify}" "{name}" changed' )
                print(f"[+] change on {name}")
        last = cur
        time.sleep(interval)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ops", default=os.path.expanduser("~/.fox/operations"))
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--notify", help="hook script called on target change")
    ap.add_argument("--watch-interval", type=int, default=5)
    ap.add_argument("--interactive-only", action="store_true", help="one-shot, no server")
    a = ap.parse_args()

    if a.interactive_only:
        for t in scan_targets(a.ops):
            print(json.dumps(t, ensure_ascii=False)[:300])
        return

    srv = ThreadingHTTPServer(("0.0.0.0", a.port), H)
    srv.ops_root = a.ops
    print(f"[*] Jack-Dashboard: http://0.0.0.0:{a.port}  (ops={a.ops})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
