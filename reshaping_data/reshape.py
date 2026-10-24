"""
Fix Arabic text extracted from PDFs in visual order (reversed lines +
presentation-form glyphs).

Usage:  python fix_arabic_json.py input.json output.json
"""
import json
import re
import sys
import unicodedata

# Characters that must be mirrored when a line is reversed
MIRROR = str.maketrans("()[]{}<>«»", ")(][}{><»«")
# Digit / Latin runs keep their left-to-right order inside an RTL line
LTR_RUN = re.compile(r"[0-9\u0660-\u0669\u06F0-\u06F9A-Za-z]+(?:[./:,][0-9\u0660-\u0669]+)*")


def fix_line(line: str) -> str:
    if not re.search(r"[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]", line):
        return line                                   # no Arabic -> leave alone
    rev = line[::-1].translate(MIRROR)                # 1) undo visual order
    rev = LTR_RUN.sub(lambda m: m.group()[::-1], rev) # 2) un-reverse numbers/Latin
    rev = unicodedata.normalize("NFKC", rev)          # 3) presentation forms -> real letters
    rev = rev.replace("\u0640", "")                   # 4) drop tatweel (kashida)
    return rev


def fix_text(text: str) -> str:
    return "\n".join(fix_line(l) for l in text.split("\n"))


PRES = re.compile(r"[\uFB50-\uFDFF\uFE70-\uFEFF]")


def fix_record(rec: dict) -> dict:
    text = rec.get("raw_text", "")
    # Only fix the "presentation forms" variant. Plain-letter reversed text
    # has an unfixable lam-alef ambiguity -> flag it for re-extraction instead.
    if text and len(PRES.findall(text)) < 0.2 * max(1, len(text) / 10):
        rec["needs_reextract"] = True
        print(f"  skipped law {rec.get('law_number')}/{rec.get('year')}: different encoding variant, re-extract or OCR")
        return rec
    if text:
        rec["raw_text"] = fix_text(rec["raw_text"])
    for art in rec.get("articles", []):
        if art.get("content"):
            art["content"] = fix_text(art["content"])
    return rec


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    data = [fix_record(r) for r in data]
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Fixed {len(data)} records -> {dst}")

