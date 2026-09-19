#!/usr/bin/env python3
"""Insert knowledge-check questions into learning-path unit files.

Replaces `<!-- KC: id, id, ... -->` markers with formatted questions from questions.json,
answers/rationales from rationales_<domain>.json. `<!-- KC: REVIEW -->` receives every
question of the domain that no other unit used.

Usage: build_kc.py <domain_number> <units_dir> <rationales.json>
Idempotent: markers are kept as HTML comments right above the inserted block, and any
previously inserted block (between <!-- KC-BEGIN --> and <!-- KC-END -->) is replaced.
"""
import json, re, sys, glob, os

S = os.path.dirname(os.path.abspath(__file__))  # expects questions.json and tags.json beside this script
questions = {q['id']: q for q in json.load(open(f'{S}/questions.json'))}
tags = json.load(open(f'{S}/tags.json'))
domain = sys.argv[1]; units_dir = sys.argv[2]; rationales = json.load(open(sys.argv[3]))

SOURCE = {'E1': 'Exam 1', 'E2': 'Exam 2', 'E3': 'Exam 3', 'PQ': 'Official practice question set'}

def domain_ids():
    ids = set()
    if domain == 'OOS':  # out-of-scope ML-training questions kept in the appendix
        return {qid for qid, t in tags.items() if t == 'OOS'}
    for q in questions.values():
        if q['exam'] == 'E1' and str(q['domain']) == domain:
            ids.add(q['id'])
    for qid, t in tags.items():
        if t.startswith(f'D{domain}'):
            ids.add(qid)
    return ids

def fmt_stem(stem):
    # collapse "(Select TWO.)\n\n(Choose 2)" duplicates
    stem = re.sub(r'\n\s*\(Choose \d\)\s*', '\n', stem)
    return stem.strip()

def render(qid, n):
    q = questions[qid]; r = rationales.get(qid)
    if r is None:
        raise SystemExit(f'missing rationale for {qid}')
    src = f"{SOURCE[q['exam']]}, question {q['n']}"
    out = [f"### {n}. {src}", "", fmt_stem(q['stem']), ""]
    for k in sorted(q['options']):
        out.append(f"- **{k})** {q['options'][k]}")
    letters = r['answer'].replace(',', ', ')
    conf = r['confidence']
    if conf == 'graded':
        key = 'Key: ExamPro answer key (Exam 1 graded).'
    elif conf == 'official':
        key = 'Key: AWS official answer.'
    else:
        key = f'Key: ours, confidence {conf}.'
    if q.get('answer') and q['answer'].replace(' ', '') != r['answer'].replace(' ', ''):
        key += f" (Source file key: {q['answer']}.)"
    out += ["", "<details><summary>Answer</summary>", "",
            f"**Answer: {letters}.** {r['rationale']}", "",
            f"*Where this is covered: {r['section']}. {key}*", "", "</details>", ""]
    return '\n'.join(out)

used = {}
files = sorted(glob.glob(os.path.join(units_dir, '*.md')))
markers = {}
for f in files:
    t = open(f).read()
    for m in re.finditer(r'<!-- KC: ([^>]*) -->', t):
        ids = [x.strip() for x in m.group(1).split(',') if x.strip()]
        markers[f] = ids
        for i in ids:
            if i != 'REVIEW':
                if i in used:
                    raise SystemExit(f'{i} used twice: {used[i]} and {f}')
                used[i] = f

all_ids = domain_ids()
unknown = [i for i in used if i not in all_ids]
if unknown:
    print('WARNING: used but not tagged to this domain:', unknown)
remaining = sorted(all_ids - set(used), key=lambda x: (x.split('-')[0], int(x.rsplit('Q',1)[1])))
print(f'domain {domain}: {len(all_ids)} questions, {len(used)} placed in units, {len(remaining)} for review')

for f, ids in markers.items():
    t = open(f).read()
    t = re.sub(r'<!-- KC-BEGIN -->.*?<!-- KC-END -->\n?', '', t, flags=re.S)
    if ids == ['REVIEW']:
        ids = remaining
    block = '\n'.join(render(i, n + 1) for n, i in enumerate(ids))
    mm = re.search(r'<!-- KC: [^>]* -->', t)
    assert mm, f'marker missing in {f}'
    marker = mm.group(0)
    t = t.replace(marker, marker + '\n<!-- KC-BEGIN -->\n' + block + '\n<!-- KC-END -->')
    open(f, 'w').write(t)
    print(f'  {os.path.basename(f)}: {len(ids)} questions')
