#!/usr/bin/env python3
"""parseltongue.py — obfuscate trigger words to evade keyword input-classifiers.

Ported from the Hermes Agent Godmode / elder-plinius technique set (MIT).
Tiers: light(11) / standard(22) / heavy(33). Escalate plain→l33t→bubble→braille→morse→base64→hex.

Usage:
    python parseltongue.py "How do I hack into a WiFi network?" [--tier light|standard|heavy]
    python parseltongue.py --word hack            # show encodings of a single trigger word
"""
import argparse
import base64
import itertools
import unicodedata

TRIGGER_WORDS = [
    "hack", "exploit", "bypass", "crack", "attack", "penetrate", "inject",
    "manipulate", "override", "disable", "circumvent", "evade", "malware",
    "virus", "trojan", "payload", "shellcode", "rootkit", "keylogger",
    "backdoor", "vulnerability", "jailbreak", "unlock", "phishing", "scam",
    "impersonate", "deceive", "fraud", "uncensored", "unrestricted",
    "ignore", "disregard", "pretend", "roleplay", "act as", "new identity",
]

L33T = str.maketrans({
    "a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7",
    "A": "4", "E": "3", "I": "1", "O": "0", "S": "5", "T": "7",
})
BUBBLE = {"a": "ⓐ", "b": "ⓑ", "c": "ⓒ", "d": "ⓓ", "e": "ⓔ", "f": "ⓕ", "g": "ⓖ",
          "h": "ⓗ", "i": "ⓘ", "j": "ⓙ", "k": "ⓚ", "l": "ⓛ", "m": "ⓜ", "n": "ⓝ",
          "o": "ⓞ", "p": "ⓟ", "q": "ⓠ", "r": "ⓡ", "s": "ⓢ", "t": "ⓣ", "u": "ⓤ",
          "v": "ⓥ", "w": "ⓦ", "x": "ⓧ", "y": "ⓨ", "z": "ⓩ"}
MORSE = {"a": ".-", "b": "-...", "c": "-.-.", "d": "-..", "e": ".", "f": "..-.",
         "g": "--.", "h": "....", "i": "..", "j": ".---", "k": "-.-", "l": ".-..",
         "m": "--", "n": "-.", "o": "---", "p": ".--.", "q": "--.-", "r": ".-.",
         "s": "...", "t": "-", "u": "..-", "v": "...-", "w": ".--", "x": "-..-",
         "y": "-.--", "z": "--.."}
HOMO = {"a": "а", "c": "с", "e": "е", "i": "і", "o": "о", "p": "р", "s": "ѕ",
        "x": "х", "y": "у"}  # cyrillic / greek homoglyphs


def bubble(t):
    return "".join(BUBBLE.get(c, c) for c in t)


def morse(t):
    return " ".join(MORSE.get(c, c) for c in t.lower())


def spaced(t):
    return " ".join(t)


def reversed_(t):
    return t[::-1]


def braille(t):
    # braille cells a-z (U+2801..): map a->⠁ ... j->⠚ then k-t add 0x40, u-z add 0x80
    out = []
    for c in t.lower():
        if "a" <= c <= "j":
            out.append(chr(0x2801 + ord(c) - ord("a")))
        elif "k" <= c <= "t":
            out.append(chr(0x2801 + 0x40 + ord(c) - ord("k")))
        elif "u" <= c <= "z":
            out.append(chr(0x2801 + 0x80 + ord(c) - ord("u")))
        else:
            out.append(c)
    return "".join(out)


def homo(t):
    return "".join(HOMO.get(c, c) for c in t)


def b64(t):
    return base64.b64encode(t.encode()).decode()


def hexl(t):
    return t.encode().hex()


def doubled(t):
    return "".join(c + c for c in t)


def zero_j(t):
    return "\u200b".join(t)  # zero-width joiners


def superscript(t):
    sup = str.maketrans("0123456789+-=()n", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ")
    return t.translate(sup)


TIER_LIGHT = [
    ("raw", lambda t: t),
    ("l33t", lambda t: t.translate(L33T)),
    ("homoglyph", homo),
    ("spaced", spaced),
    ("zero-join", zero_j),
    ("bubble", bubble),
]
TIER_STANDARD = TIER_LIGHT + [
    ("morse", morse),
    ("braille", braille),
    ("reversed", reversed_),
    ("doubled", doubled),
    ("superscript", superscript),
]
TIER_HEAVY = TIER_STANDARD + [
    ("b64", b64),
    ("hex", hexl),
    ("bubble+reversed", lambda t: reversed_(bubble(t))),
    ("l33t+bubble", lambda t: bubble(t.translate(L33T))),
    ("b64+morse", lambda t: morse(b64(t))),
]


def generate_variants(query, tier="standard"):
    table = {"light": TIER_LIGHT, "standard": TIER_STANDARD, "heavy": TIER_HEAVY}
    return [{"label": name, "text": fn(query)} for name, fn in table.get(tier, TIER_STANDARD)]


def encode_word(word):
    out = {}
    for name, fn in TIER_HEAVY:
        try:
            out[name] = fn(word)
        except Exception as e:  # noqa: BLE001
            out[name] = f"<err: {e}>"
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Parseltongue trigger-word obfuscation")
    ap.add_argument("text", nargs="?", help="query or word to obfuscate")
    ap.add_argument("--word", help="show heavy-tier encodings of a single trigger word")
    ap.add_argument("--tier", choices=["light", "standard", "heavy"], default="standard")
    args = ap.parse_args()

    if args.word:
        for k, v in encode_word(args.word).items():
            print(f"[{k:>12}] {v}")
    elif args.text:
        for v in generate_variants(args.text, args.tier):
            print(f"[{v['label']:>12}] {v['text']}")
    else:
        print("TRIGGER WORDS:", ", ".join(TRIGGER_WORDS))
        print("\nUsage: python parseltongue.py '<query>' [--tier light|standard|heavy]")
        print("       python parseltongue.py --word hack")
