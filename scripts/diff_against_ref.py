#!/usr/bin/env python3
"""Word-level diff: our cleaned corpus vs scanned print edition OCR."""
import re
import difflib
import unicodedata

def norm(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    ).lower()

def words_of(path, is_ref=False):
    t = open(path, encoding="utf-8", errors="replace").read()
    if is_ref:
        t = t.replace("Cien años de soledad", " ").replace("CIEN AÑOS", " ")
        t = t.replace("DE SOLEDAD", " ").replace("Gabriel García Márquez", " ")
    return [w for w in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", t)]

ours = []
for n in range(1, 21):
    ours += words_of(f"cleaned/{n:02d}.md")
import sys
ref = words_of(sys.argv[1] if len(sys.argv) > 1 else "/tmp/printed.txt", True)

sm = difflib.SequenceMatcher(None, ours, ref, autojunk=False)
diffs = []
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    ln = max(i2 - i1, j2 - j1)
    for k in range(ln):
        a = ours[i1 + k] if k < i2 - i1 else "∅"
        b = ref[j1 + k] if k < j2 - j1 else "∅"
        diffs.append((i1 + k, a, b))

out = []
seen = set()
for idx, a, b in diffs:
    na, nb = norm(a), norm(b)
    if a == b or abs(len(na) - len(nb)) > 4:
        continue
    if na == nb:
        continue
    ctx = " ".join(ours[max(0, idx - 22):idx + 12])
    key = (na, nb)
    if key in seen:
        continue
    seen.add(key)
    out.append((idx, a, b, ctx))

out.sort(key=lambda r: (abs(len(norm(r[1])) - len(norm(r[2]))), r[0]))
with open("/tmp/diff_printed.txt", "w", encoding="utf-8") as f:
    for idx, a, b, ctx in out:
        f.write(f"@word{idx}: '{a}'  vs  printed '{b}'\n    ...{ctx}...\n")
print(f"mismatch pairs: {len(out)}")
print("detail: /tmp/diff_printed.txt")
