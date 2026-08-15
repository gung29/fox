#!/usr/bin/env python3
"""fox-dorker.py — multi-engine dork searcher (authorized recon).

Search engines via lightweight HTML scraping (no API keys). Engines:
  google, bing, yahoo, ask, all.
Supports: single dork (-d), batch dork list (-l), proxy rotation (--proxy file),
page count (-p), output (-o), interactive (-i). Results deduped.

Usage:
  fox-dorker -d "inurl:php?id=" -e bing -p 3 -o targets.txt
  fox-dorker -l dorks.txt -e all -p 2
  fox-dorker -i
"""
import argparse, re, sys, time, random, html, os

try:
    import requests
except ImportError:
    sys.exit("[!] requests tidak ada: pip install requests")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def load_proxies(path):
    out = []
    if path and os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#"):
                out.append({"http": line, "https": line})
    return out


def grab(url, proxies, engine):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, proxies=proxies,
                         timeout=20, verify=False)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return ""


def parse_google(html_):
    out = []
    for m in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', html_):
        url, txt = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        if "google.com" in url or "google." in url:
            continue
        if txt.strip():
            out.append(url)
    return out


def parse_bing(html_):
    out = []
    for m in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*>', html_):
        url = m.group(1)
        if url.startswith("http") and "bing.com" not in url and "microsoft.com" not in url:
            out.append(url)
    return out


def parse_yahoo(html_):
    out = []
    for m in re.finditer(r"href=\"(https?://(?!search.yahoo)[^\"]+)\"", html_):
        url = m.group(1)
        if url.startswith(("https://r.search.yahoo.com", "http://r.search.yahoo.com")):
            mm = re.search(r"/RU=([^/]+)", url)
            if mm:
                import urllib.parse
                url = urllib.parse.unquote(mm.group(1))
        out.append(url)
    return out


def parse_ask(html_):
    out = []
    for m in re.finditer(r'href="(https?://[^\"]+)"', html_):
        url = m.group(1)
        if url.startswith("http") and "ask.com" not in url:
            out.append(url)
    return out


ENGINES = {
    "google": ("https://www.google.com/search?q={q}&num={n}&start={start}", parse_google),
    "bing": ("https://www.bing.com/search?q={q}&count={n}&first={start}", parse_bing),
    "yahoo": ("https://search.yahoo.com/search?p={q}&n={n}&b={start}", parse_yahoo),
    "ask": ("https://www.ask.com/web?q={q}&page={page}", parse_ask),
}


def search(engine, dork, pages, proxies):
    q = html.escape(dork)
    base, parser = ENGINES[engine]
    results = []
    per = 10
    for p in range(1, pages + 1):
        start = (p - 1) * per + 1
        url = base.format(q=q, n=per, start=start, page=p)
        html_ = grab(url, proxies, engine)
        found = parser(html_)
        results.extend(found)
        time.sleep(random.uniform(1.0, 2.5))  # slow down to avoid rate-limit (authorized)
    return results


def run(dork, engine, pages, proxies, outfile):
    print(f"[*] fox-dorker: engine={engine} pages={pages} dork={dork!r}")
    if engine == "all":
        engs = ["google", "bing", "yahoo", "ask"]
    else:
        engs = [engine]
    allres = {}
    for e in engs:
        print(f"    -> {e} ...")
        for u in search(e, dork, pages, proxies):
            if u not in allres:
                allres[u] = None
        time.sleep(random.uniform(1, 2))
    urls = list(allres.keys())
    print(f"[+] {len(urls)} unique results")
    if outfile:
        with open(outfile, "w") as f:
            f.write("\n".join(urls))
        print(f"    saved -> {outfile}")
    else:
        for u in urls[:50]:
            print("   ", u)
    return urls


def interactive(proxies):
    print("[i] fox-dorker interactive. Commands: dork> <dork>, !engine x, !pages n, !output f, !proxy file")
    dork, engine, pages, outfile = "", "all", 3, None
    while True:
        try:
            line = input("dork> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line.startswith("!"):
            k, _, v = line[1:].partition(" ")
            if k == "engine":
                engine = v; print(f"    engine={engine}")
            elif k == "pages":
                pages = int(v); print(f"    pages={pages}")
            elif k == "output":
                outfile = v; print(f"    output={outfile}")
            elif k == "proxy":
                proxies = load_proxies(v); print(f"    proxies={len(proxies)}")
            elif k in ("quit", "exit"):
                break
            continue
        dork = line
        run(dork, engine, pages, proxies, outfile)


def main():
    ap = argparse.ArgumentParser(description="fox-dorker — multi-engine dork searcher")
    ap.add_argument("-d", "--dork", help="single dork")
    ap.add_argument("-l", "--list", help="file of dorks (batch)")
    ap.add_argument("-e", "--engine", default="all", help="google|bing|yahoo|ask|all (default all)")
    ap.add_argument("-p", "--pages", type=int, default=3)
    ap.add_argument("--proxy", help="file of proxies (one per line)")
    ap.add_argument("-o", "--output", help="save results to file")
    ap.add_argument("-i", "--interactive", action="store_true")
    a = ap.parse_args()

    proxies = None
    if a.proxy:
        proxies = load_proxies(a.proxy)
        print(f"    loaded {len(proxies)} proxies")
    if a.interactive:
        interactive(proxies)
        return
    if a.list:
        if not os.path.exists(a.list):
            sys.exit(f"[!] {a.list} tidak ada")
        for line in open(a.list):
            line = line.strip()
            if line and not line.startswith("#"):
                run(line, a.engine, a.pages, proxies, a.output)
                time.sleep(1)
        return
    if a.dork:
        run(a.dork, a.engine, a.pages, proxies, a.output)
        return
    ap.print_help()


if __name__ == "__main__":
    main()
