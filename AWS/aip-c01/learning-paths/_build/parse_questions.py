import re,json,sys
def parse_exam(path,tag):
    t=open(path).read()
    qsec=t.split('## QUESTIONS',1)[1]; asec=''
    if '## ANSWERS' in qsec: qsec,asec=qsec.split('## ANSWERS',1)
    out=[]
    for blk in re.split(r'\n---\n',qsec):
        m=re.search(r'\*\*Q(\d+)\.\*\*\s*(.*)',blk,re.S)
        if not m: continue
        n=int(m.group(1)); body=m.group(2).strip()
        lines=body.split('\n'); stem=[]; opts={}; dom=None; cur=None
        for ln in lines:
            om=re.match(r'^([A-F])\)\s*(.*)',ln)
            dm=re.match(r'\*\*Domain:\*\*\s*(\d)',ln)
            if dm: dom=int(dm.group(1)); cur=None; continue
            if om: cur=om.group(1); opts[cur]=om.group(2).strip(); continue
            if cur and ln.strip(): opts[cur]+=' '+ln.strip()
            elif not cur: stem.append(ln)
        stem='\n'.join(stem).strip()
        out.append({'id':f'{tag}-Q{n}','exam':tag,'n':n,'stem':stem,'options':opts,'domain':dom,'answer':None})
    ans={}
    for row in re.findall(r'^\|(.*)\|\s*$',asec,re.M):
        cells=[c.strip() for c in row.split('|')]
        for i in range(0,len(cells)-1):
            if re.fullmatch(r'\d+',cells[i]) and re.fullmatch(r'[A-F](\*?)(,\s*[A-F])*\*?',cells[i+1]):
                ans[int(cells[i])]=cells[i+1].replace('*','').replace(' ','')
    for q in out:
        if q['n'] in ans: q['answer']=ans[q['n']]
    return out
def parse_practice(path):
    t=open(path).read()
    qpart=t.split('# Part 1',1)[1].split('# Part 2',1)[0]; apart=t.split('# Part 2',1)[1]
    out=[]
    for m in re.finditer(r'## Question (\d+)\n(.*?)(?=\n## Question \d+\n|\Z)',qpart,re.S):
        n=int(m.group(1)); body=m.group(2)
        opts=dict(re.findall(r'- \*\*([A-F])\.\*\*\s*(.*)',body))
        stem=body.split('- **A.**')[0].strip().replace('→ [Show answer]','')
        out.append({'id':f'PQ-Q{n}','exam':'PQ','n':n,'stem':stem,'options':opts,'domain':None,'answer':None,'explanation':None})
    for m in re.finditer(r'## Answer (\d+)\n(.*?)(?=\n## Answer \d+\n|\Z)',apart,re.S):
        n=int(m.group(1)); body=m.group(2)
        am=re.search(r'\*\*Correct answers?:\s*([A-F](?:(?:,| and)\s*[A-F])*)',body)
        for q in out:
            if q['n']==n:
                q['answer']=re.sub(r'\s*(,|and)\s*',',',am.group(1)) if am else None
                q['explanation']=body.split('**Read more**')[0].strip()
    return out
qs=parse_exam('01/EXAM.md','E1')+parse_exam('02/EXAM.md','E2')+parse_exam('03/EXAM.md','E3')+parse_practice('practice-questions.md')
json.dump(qs,open(sys.argv[1],'w'),indent=1)
from collections import Counter
print(len(qs),Counter(q['exam'] for q in qs)); print('with answer:',sum(1 for q in qs if q['answer'])); print('E1 domains:',Counter(q['domain'] for q in qs if q['exam']=='E1'))
print('option counts:',Counter(len(q['options']) for q in qs))
bad=[q['id'] for q in qs if len(q['options'])<4 or not q['stem']]; print('bad:',bad)
# compact dumps for reading
for tag in ['E2','E3','PQ']:
    with open(f'{sys.argv[1].rsplit("/",1)[0]}/q_{tag}.txt','w') as f:
        for q in qs:
            if q['exam']!=tag: continue
            f.write(f"### {q['id']}\n{q['stem']}\n"+'\n'.join(f"{k}) {v}" for k,v in sorted(q['options'].items()))+(f"\nANS: {q['answer']}" if q['answer'] else '')+"\n\n")
