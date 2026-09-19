#!/usr/bin/env python3
"""Mechanical guard for the readability rewrite.

Compares the committed version of a unit with the rewritten working copy and
fails if anything that carries information changed: headings, the generated
Knowledge check block, the multiset of numbers, the multiset of code spans, the
link targets, or the word count beyond a tolerance band. Also fails on em dash.

Usage:
    readability_check.py OLD NEW
    readability_check.py --git PATH [PATH ...]   # OLD is `git show HEAD:PATH`
"""

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

WORDS_MIN = 0.97   # a rewrite may not shrink the text by more than 3 percent
WORDS_MAX = 1.35   # lists and connective tissue may grow it up to 35 percent

KC_START = "## Knowledge check"
KC_END = "## Summary"


def kc_block(text):
    """Return the generated Knowledge check block, or '' if the file has none."""
    lines = text.split("\n")
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == KC_START)
    except StopIteration:
        # Domain reviews call this section "Mixed quiz". The generator's
        # markers remain the authoritative boundary for those blocks.
        match = re.search(r"<!-- KC:.*?<!-- KC-END -->", text, re.S)
        return match.group(0) if match else ""
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].strip() == KC_END:
            end = i
            break
    return "\n".join(lines[start:end])


def without_kc(text):
    block = kc_block(text)
    return text.replace(block, "", 1) if block else text


def headings(text):
    return [l.rstrip() for l in text.split("\n") if l.startswith("#")]


def strip_markup(text):
    text = re.sub(r"```.*?```", lambda m: m.group(0), text, flags=re.S)
    text = text.replace("**", "").replace("__", "")
    text = re.sub(r"^\s{0,3}(?:[-*+]|\d+\.)\s+", "", text, flags=re.M)   # list markers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.M)                    # heading marks
    text = re.sub(r"^\s*>\s?", "", text, flags=re.M)                      # blockquotes
    text = text.replace("|", " ")
    return text


def numbers(text):
    text = strip_markup(text)
    # 15, 15.5, 1,000, 10x, 29-second, 5xx, 99.9%, 24h, 6 MB stay as one token each
    # A comma after a number is punctuation, not part of its value. Digits
    # embedded in identifiers (S3, A2A, ml.g5) are not quantitative facts;
    # explaining a product in a second sentence may repeat its name.
    return Counter(re.findall(
        r"(?<![\w])\d+(?:,\d{3})*(?:\.\d+)?(?:[a-zA-Z%]{1,3})?", text
    ))


def code_spans(text):
    return Counter(re.findall(r"`[^`\n]+`", text))


def link_targets(text):
    return Counter(re.findall(r"\]\(([^)\s]+)\)", text))


def links(text):
    return Counter(re.findall(r"!?\[[^\]\n]*\]\([^\n]*?\)", text))


def code_blocks(text):
    return re.findall(r"(?ms)^```[^\n]*\n.*?^```[^\n]*$", text)


def table_rows(text):
    return [line.replace("**", "") for line in text.splitlines()
            if line.startswith("|")]


def word_count(text):
    return len(strip_markup(text).split())


def bold_count(text):
    return len(re.findall(r"\*\*[^*\n]+\*\*", text))


def diff_counter(old, new, label, out):
    missing = old - new
    added = new - old
    ok = True
    if missing:
        ok = False
        items = ", ".join(f"{k}x{v}" if v > 1 else k for k, v in sorted(missing.items()))
        out.append(f"  ERROR   {label} missing from new: {items}")
    if added:
        ok = False
        items = ", ".join(f"{k}x{v}" if v > 1 else k for k, v in sorted(added.items()))
        out.append(f"  ERROR   {label} added in new: {items}")
    return ok


def check(old, new, name):
    out = [f"== {name}"]
    errors = 0

    # Generated exam text must remain byte-identical, including punctuation.
    prose = "\n".join(line for line in without_kc(new).splitlines()
                      if not line.startswith(("|", "#")))
    if "—" in prose:
        n = prose.count("—")
        out.append(f"  ERROR   {n} em dash(es), U+2014")
        errors += 1
    else:
        out.append("  ok      no em dash")

    if headings(old) != headings(new):
        out.append("  ERROR   headings changed (text, order or count)")
        ho, hn = headings(old), headings(new)
        for a, b in zip(ho, hn):
            if a != b:
                out.append(f"          old: {a}")
                out.append(f"          new: {b}")
                break
        if len(ho) != len(hn):
            out.append(f"          old has {len(ho)} headings, new has {len(hn)}")
        errors += 1
    else:
        out.append(f"  ok      {len(headings(new))} heading(s) unchanged")

    ko, kn = kc_block(old), kc_block(new)
    if ko or kn:
        if ko != kn:
            out.append("  ERROR   Knowledge check block changed; it is generated and off limits")
            errors += 1
        else:
            out.append("  ok      Knowledge check block byte-identical")
    else:
        out.append("  info    no Knowledge check block in this file")

    bo, bn = without_kc(old), without_kc(new)

    if not diff_counter(numbers(bo), numbers(bn), "number(s)", out):
        errors += 1
    else:
        out.append(f"  ok      {sum(numbers(bn).values())} number token(s) preserved")

    if not diff_counter(code_spans(bo), code_spans(bn), "code span(s)", out):
        errors += 1
    else:
        out.append(f"  ok      {sum(code_spans(bn).values())} code span(s) preserved")

    if not diff_counter(link_targets(bo), link_targets(bn), "link target(s)", out):
        errors += 1
    else:
        out.append(f"  ok      {sum(link_targets(bn).values())} link target(s) preserved")

    if not diff_counter(links(bo), links(bn), "complete link(s)", out):
        errors += 1
    if code_blocks(bo) != code_blocks(bn):
        out.append("  ERROR   fenced code blocks changed")
        errors += 1
    if table_rows(bo) != table_rows(bn):
        out.append("  ERROR   table content changed beyond bold formatting")
        errors += 1

    wo, wn = word_count(bo), word_count(bn)
    ratio = wn / wo if wo else 1.0
    if ratio < WORDS_MIN:
        out.append(f"  ERROR   word count fell {wo} -> {wn} ({ratio:.2f}x); content was dropped")
        errors += 1
    elif ratio > WORDS_MAX:
        out.append(f"  ERROR   word count grew {wo} -> {wn} ({ratio:.2f}x); content was added")
        errors += 1
    else:
        out.append(f"  ok      word count {wo} -> {wn} ({ratio:.2f}x)")

    bbo, bbn = bold_count(bo), bold_count(bn)
    if bbn <= bbo:
        out.append(f"  warn    bold count did not increase ({bbo} -> {bbn}); was Rule 1 applied?")
    else:
        out.append(f"  info    bold count {bbo} -> {bbn}")

    out.append(f"-- {errors} error(s)")
    print("\n".join(out))
    return errors


def git_show(path):
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True, check=True).stdout.strip()
    rel = str(Path(path).resolve().relative_to(root))
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"cannot read HEAD:{rel}: {r.stderr.strip()}")
    return r.stdout


def main(argv):
    if len(argv) >= 3 and argv[1] == "--git":
        total = 0
        for p in argv[2:]:
            total += check(git_show(p), Path(p).read_text(encoding="utf-8"), p)
        sys.exit(1 if total else 0)
    if len(argv) == 3:
        old = Path(argv[1]).read_text(encoding="utf-8")
        new = Path(argv[2]).read_text(encoding="utf-8")
        sys.exit(1 if check(old, new, argv[2]) else 0)
    sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
