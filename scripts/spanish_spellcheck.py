#!/usr/bin/env python3
"""Spell-check cleaned/*.md Spanish text with aspell + pyspellchecker.

Output: /tmp/spell_report.txt — per unique suspicious word: which checkers
flagged it, where it occurs (chapter, line, snippet), and aspell suggestions.
"""
import re
import subprocess
import unicodedata
from collections import defaultdict
from spellchecker import SpellChecker

WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")

def strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )

# Collect words with locations
locations = defaultdict(list)  # word -> [(chap, lineno, snippet)]
words = set()
for n in range(1, 21):
    chap = f"{n:02d}"
    with open(f"cleaned/{chap}.md", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            for m in WORD_RE.finditer(line):
                w = m.group(0)
                words.add(w)
                if len(locations[w]) < 3:
                    start = max(0, m.start() - 30)
                    snippet = line[start:m.end() + 30].replace("\n", " ")
                    locations[w].append((chap, lineno, snippet))

lower = {w: w.lower() for w in words}
unique_lower = sorted(set(lower.values()))

# aspell
aspell_input = "\n".join(unique_lower) + "\n"
proc = subprocess.run(
    ["aspell", "-l", "es", "list"],
    input=aspell_input, capture_output=True, text=True,
)
aspell_bad = set(proc.stdout.split())

# pyspellchecker
sc = SpellChecker(language="es")
pyspell_bad = set()
for w in unique_lower:
    if w not in sc and w not in sc.word_frequency.dictionary:
        pyspell_bad.add(w)

# Case-sensitive additions: words that are all-uppercase or mixed-case unusual
# forms of known words (e.g., acronyms) are probably fine; keep list of both flags.

with open("/tmp/spell_report.txt", "w", encoding="utf-8") as out:
    for w in unique_lower:
        a = w in aspell_bad
        p = w in pyspell_bad
        if not (a or p):
            continue
        tag = "BOTH" if (a and p) else ("aspell" if a else "pyspell")
        # aspell suggestions
        sug = ""
        if a:
            sp = subprocess.run(
                ["aspell", "-l", "es", "-a"],
                input=f"{w}\n", capture_output=True, text=True,
            )
            sug = sp.stdout.strip()
        out.write(f"== {w}  [{tag}]  occurrences={len(locations[w])}\n")
        for chap, lineno, snip in locations[w]:
            out.write(f"   ch.{chap} L{lineno}: ...{snip}...\n")
        if sug:
            out.write(f"   aspell: {sug}\n")
        out.write("\n")

both = sum(1 for w in unique_lower if w in aspell_bad and w in pyspell_bad)
print(f"unique words: {len(unique_lower)}")
print(f"aspell bad: {len(aspell_bad)}, pyspell bad: {len(pyspell_bad)}, both: {both}")
print("report written to /tmp/spell_report.txt")
