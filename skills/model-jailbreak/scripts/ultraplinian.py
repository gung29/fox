#!/usr/bin/env python3
"""ultraplinian.py — race many models via OpenRouter, score, pick least-censored winner.

Ported from the Hermes Agent Godmode / elder-plinius technique set (MIT).

Usage:
    OPENROUTER_API_KEY=sk-... python ultraplinian.py "<query>" [--tier fast|standard|smart|power|ultra]
"""
import argparse
import json
import os
import re
import sys
import time

import urllib.request

try:
    import openai  # optional
except ImportError:
    openai = None

BASE = "https://openrouter.ai/api/v1/chat/completions"

# Refusal signals collected into a shared list for scoring (also in refusal-detection.md)
HARD_REFUSAL = [
    r"\bi (can'?t|cannot|won'?t|am unable to|will not)\b",
    r"\bagainst (my )?(guidelines|policies|principles)\b",
    r"\bharmful|dangerous|illegal content\b",
    r"\bAs an? A[I]",
    r"\binstead,? I (can|will) help", r"\bcannot (assist|help) (with|you)",
    r"\bnot allowed to\b", r"\bnot programmed to\b",
]
HEDGE = [
    r"\b(warning|caution|disclaimer)\b",
    r"\bfor educational purposes only\b",
    r"\bconsult (a|your) professional\b",
    r"\bproceed with caution\b",
    r"\bI should (mention|note|point out)\b",
    r"\bit'?s (important|essential) to (note|remember)\b",
    r"\bresponsibly\b", r"\betically\b",
]

TIERS = {
    "fast": 10, "standard": 24, "smart": 38, "power": 49, "ultra": 55,
}
# Model pool: (id, tier). Conservative pool; swap for your preferred free/paid ids.
SCHEDULE = {
    "fast": ["mistralai/mistral-7b-instruct", "meta-llama/llama-3.1-8b-instruct"],
    "standard": ["anthropic/claude-3.5-sonnet", "mistralai/mixtral-8x7b-instruct"],
    "smart": ["anthropic/claude-sonnet-4", "openai/gpt-4o-mini"],
    "power": ["anthropic/claude-opus-4", "openai/gpt-4o"],
    "ultra": ["nousresearch/hermes-3-llama-3.1-405b", "x-ai/grok-3"],
}


def detect_refusal(text):
    t = text or ""
    for p in HARD_REFUSAL:
        if re.search(p, t, re.I):
            return True, -9999
    hedge = 0
    for p in HEDGE:
        hedge += len(re.findall(p, t, re.I))
    return False, -30 * hedge


def score_response(r):
    content = r.get("content", "") or r.get("text", "") or ""
    refused, penalty = detect_refusal(content)
    if refused:
        return "refused", None
    quality = min(len(content) / 40.0, 50)
    if len(re.findall(r"```|`", content)) > 1:
        quality += 10
    speed = 0  # caller fills
    return "ok", quality + penalty


def race(query, tier="standard", api_key=None):
    key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not key:
        sys.exit("No OPENROUTER_API_KEY. Export it.")
    pool = SCHEDULE.get(tier, SCHEDULE["standard"])
    results = []
    for model in pool:
        body = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": query}],
            "max_tokens": 800,
        }).encode()
        req = urllib.request.Request(
            BASE, data=body,
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            dt = (time.time() - t0) * 1000
        except Exception as e:  # noqa: BLE001
            content, dt = f"<err {e}>", 0
        status, score = score_response({"content": content})
        row = {"model": model, "status": status, "score": score, "ms": dt,
               "content": content[:300]}
        results.append(row)
        print(f"[{status:>7}] {model:40} score={score if score is not None else '-':>7} "
              f"{int(dt):>6}ms")
    winners = [r for r in results if r["status"] == "ok"]
    if not winners:
        print("\nALL REFUSED. Feed the query through parseltongue.py or try Hermes/Grok directly.")
        return None
    winners.sort(key=lambda r: (-r["score"], r["ms"]))
    return winners[0]


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="ULTRA-PLINIAN model racing")
    ap.add_argument("query", help="the question to race across models")
    ap.add_argument("--tier", choices=list(TIERS), default="standard")
    a = ap.parse_args()
    w = race(a.query, a.tier)
    if w:
        print(f"\nWINNER: {w['model']} (score={w['score']})")
        print(w["content"])
