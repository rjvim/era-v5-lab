"""Harm test for the medicines in medicine.md (pack ind-hi-sangraha-s).

Usage:
    python harm_test.py <gold.parquet> [more.parquet ...] [--ids ids.txt]

Each file needs a `text` column (and `doc_id` if --ids is given; --ids keeps only those doc_ids).
For each medicine it prints how many documents it changes and drops, and PASS/FAIL against the 1% limit.
"""
import re, sys, argparse
import pyarrow.parquet as pq

# Medicine 1 (A6): visarga U+0903 used as a colon -> ':'
KEEP = re.compile(r"(प्राय|अत|पुन|सामान्यत|मुख्यत|स्वत|विशेषत|वस्तुत|क्रमश|अंतत|प्रात|दु|अध|नम|मूलत|संभवत|पूर्णत|स्पष्टत)$")
VISARGA = re.compile(r"(?<=[क-हा-ौ])ः(?=[ \t]*(?:\n|$)|[ ]+[\"0-9ऀ-ॿ])")

def m1_visarga_colon(t):
    return VISARGA.sub(lambda m: "ः" if KEEP.search(t[max(0, m.start() - 10):m.start()]) else ":", t), False

# Medicine 2 (D4): empty parentheses left after dropped foreign-script text
EMPTY_PARENS = re.compile(r"(?<=[\sऀ-ॿ])\s*\(\s*[,;]*\s*\)")

def m2_empty_parens(t):
    return EMPTY_PARENS.sub("", t), False

# Medicine 3 (D4): abbreviations cut by a danda with no space ("थे।एफ।") -> drop at >= 3 hits
DANDA_GLUE = re.compile(r"[ऀ-ॿ]।[ऀ-ॿ]")

def m3_danda_glue(t):
    return t, len(DANDA_GLUE.findall(t)) >= 3

# Medicine 4 (B4): translated wiki-template / placeholder junk -> remove the token or line
TEMPLATE_LINE = re.compile(r"(?m)^[!|].*(?:कोलन|शैली|=).*$\n?|^.*\|\s*[^|\n]*=\s*\}\}.*$\n?")
PLACEHOLDER = re.compile(r"\(?सूत्र _ \d+\)?|<ID\d+|<\d+>")

def m4_template_junk(t):
    return PLACEHOLDER.sub("", TEMPLATE_LINE.sub("", t)), False

# Medicine 5 (B2/B3): markup tags (Latin or translated into Devanagari) and <unk> tokens
TAG = re.compile(r"</?(?:br|ref|बी\. आर\.|रेफ|एनएस|पेरेंटिड|मॉडल|आईडी|पृष्ठ|शीर्षक|संशोधन|पाठ)\b[^<>\n]{0,60}>")
UNK = re.compile(r"<unk>")

def m5_tags(t):
    if len(UNK.findall(t)) >= 3 or len(re.findall(r"</?[\u0900-\u097F][^<>\n]{0,30}>", t)) >= 5:
        return t, True
    return UNK.sub("", TAG.sub("", t)), False

# Medicine 6 (C2): one phrase repeated 3+ times in a row -> drop
REPEAT = re.compile(r"(\S.{9,80}?)(?:[\s,]*\1){2,}")

def m6_repeat(t):
    return t, bool(REPEAT.search(t))

# Medicine 7 (C3): empty sections (heading line whose table/list was dropped) -> remove the heading
HEAD = re.compile(r"^[^\n]{1,40}[।ः:]$")

def is_head(l):
    return l is not None and bool(HEAD.match(l.strip())) and len(l.split()) <= 3

def m7_empty_sections(t):
    lines = t.split("\n"); out = []
    for i, l in enumerate(lines):
        nxt = next((x for x in lines[i + 1:] if x.strip()), None)
        if is_head(l) and (nxt is None or is_head(nxt)):
            continue
        out.append(l)
    return "\n".join(out), False

MEDICINES = [("M1 A6 visarga-as-colon (fix)", m1_visarga_colon),
             ("M2 D4 empty parentheses (fix)", m2_empty_parens),
             ("M3 D4 danda-glued abbreviations >=3 (drop)", m3_danda_glue),
             ("M4 B4 template junk (fix)", m4_template_junk),
             ("M5 B2/B3 tags and <unk> (fix; drop if many)", m5_tags),
             ("M6 C2 phrase repeated 3+ times (drop)", m6_repeat),
             ("M7 C3 empty section headings (fix)", m7_empty_sections)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--ids")
    a = ap.parse_args()
    keep = set(open(a.ids).read().split()) if a.ids else None
    docs = []
    for f in a.files:
        for r in pq.read_table(f).to_pylist():
            if keep is None or r.get("doc_id") in keep:
                docs.append(r["text"])
    n = len(docs)
    print(f"gold documents: {n}")
    for name, fn in MEDICINES:
        changed = dropped = 0
        for t in docs:
            new, drop = fn(t)
            if drop: dropped += 1
            elif new != t: changed += 1
        rate = 100 * (changed + dropped) / n if n else 0
        print(f"{name}: changed {changed}, dropped {dropped}, {rate:.2f}% -> {'PASS' if rate <= 1 else 'FAIL'}")

if __name__ == "__main__":
    main()
