#!/usr/bin/env python3
"""Stage 2d: triage flagged words (optimized: batched aspell, one-pass ctx)."""
import re
import unicodedata
import subprocess
from collections import defaultdict

def norm(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    ).lower()

def lev(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
        prev = cur
    return prev[-1]

flagged = {}
with open("/tmp/spell_report.txt", encoding="utf-8") as f:
    for line in f:
        m = re.match(r"== (\S+)  \[(\w+)\]", line)
        if m:
            flagged[m.group(1)] = m.group(2)

# One-pass case-insensitive context extraction
ctxs = defaultdict(list)
words_by_len = sorted(flagged, key=len, reverse=True)
alt = re.compile(
    r"(?<![a-záéíóúüñ])(" + "|".join(re.escape(w) for w in words_by_len) + r")(?![a-záéíóúüñ])"
)
for n in range(1, 21):
    chap = f"{n:02d}"
    with open(f"cleaned/{chap}.md", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            low = line.lower()
            for m in alt.finditer(low):
                w = m.group(1)
                if len(ctxs[w]) >= 2:
                    continue
                s = max(0, m.start() - 30)
                ctxs[w].append(f"ch.{chap} L{lineno}: ...{line[s:m.end() + 30].strip()}...")

def aspell_suggestions(words):
    proc = subprocess.run(
        ["aspell", "-l", "es", "-a"],
        input="\n".join(words) + "\n", capture_output=True, text=True,
    )
    out = {}
    i = 0
    for line in proc.stdout.splitlines():
        if not line or line.startswith("@"):
            continue
        w = words[i] if i < len(words) else None
        i += 1
        if w is None:
            continue
        sugs = []
        if line.startswith("&"):
            body = line.split(":", 1)[1] if ":" in line else ""
            for t in body.split(","):
                t = t.strip()
                if re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", t):
                    sugs.append(t)
        elif line.startswith("+"):
            sugs = [t for t in line[1:].split()
                    if re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", t)]
        out[w] = sugs
    return out

need_sug = [w for w, t in flagged.items() if t in ("aspell", "BOTH")]
sug_map = aspell_suggestions(need_sug)

rows = []
for w, tag in flagged.items():
    nw = norm(w)
    cands = []
    for sw in sug_map.get(w, []):
        sn = norm(sw)
        if sn == nw:
            continue
        d = lev(nw, sn)
        if d <= 2 and abs(len(nw) - len(sn)) <= 3:
            cands.append((d, sw))
    if cands:
        rows.append((min(d for d, _ in cands), w,
                     sorted(set(cands))[:5], tag, ctxs[w]))

rows.sort(key=lambda r: (r[0], r[1]))
with open("/tmp/spell_likely.txt", "w", encoding="utf-8") as f:
    for d, w, cands, tag, ctx in rows:
        f.write(f"lev{d}  {w}  ->  {', '.join(c for _, c in cands)}  [{tag}]\n")
        for c in ctx:
            f.write(f"    {c}\n")
print(f"candidates: {len(rows)}")
