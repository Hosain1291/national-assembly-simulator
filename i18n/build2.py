import json,re,sys,subprocess
L=sys.argv[1]  # en | ja
SRC='../korea-assembly.html'
subprocess.run(['node','extract.mjs'],check=True,capture_output=True)
src=open(SRC,encoding='utf-8').read()
i0=src.index('<script>')+8; i1=src.rindex('</script>')
js=src[i0:i1]
lits=json.load(open('lits.json'))
D=json.load(open('names_%s.json'%L,encoding='utf-8'))
D.update(json.load(open('dict_%s.json'%L,encoding='utf-8')))
for k,v in list(D.items()):
    if k.endswith(' ') and v and not v.endswith(' '): v=v+' '
    if k.startswith(' ') and v and not v.startswith(' '): v=' '+v
    D[k]=v
g0=js.index('const GOVM='); g1=js.index('\n',g0)
def q(s,quote):
    if quote=="'": return "'"+s.replace('\\','\\\\').replace("'","\\'").replace('\n','\\n')+"'"
    return json.dumps(s,ensure_ascii=False)
out=[]; pos=0; miss={}
for o in sorted(lits,key=lambda o:o['s']):
    s,e,v=o['s'],o['e'],o['v']; raw=js[s:e]
    if g0<=s<g1 and o['kind']=='lit':
        out.append(js[pos:s]); out.append(q('|'.join(D.get(x,x) for x in v.split(' ')),raw[0])); pos=e; continue
    if v not in D: miss[v]=miss.get(v,0)+1; continue
    t=D[v]; out.append(js[pos:s])
    out.append(t.replace('\\','\\\\').replace('`','\\`').replace('${','\\${') if o['kind']=='tpl' else q(t,raw[0]))
    pos=e
out.append(js[pos:]); js2=''.join(out)
P=json.load(open('patch_%s.json'%L,encoding='utf-8'))
for a,b in P['replace']:
    if a not in js2: print('PATCH MISS',a[:70])
    js2=js2.replace(a,b)
for a,b in P.get('regex',[]):
    js2,n=re.subn(a,b,js2)
    if not n: print('REGEX MISS',a)
js2=P['prelude']+js2.rstrip()
# append overrides before IIFE end
k=js2.rstrip().rfind('})();')
js2=js2[:k]+P['overrides']+'\n'+js2[k:]
head=src[:i0]; tail=src[i1:]
def trhtml(h):
    def f(m):
        t=m.group(1); st=t.strip()
        return '>'+t.replace(st,D[st])+'<' if st in D else m.group(0)
    h=re.sub(r'>([^<>]*[가-힣][^<>]*)<',f,h)
    h=re.sub(r'((?:aria-label|title|placeholder|alt|content)=")([^"]*[가-힣][^"]*)"',lambda m:m.group(1)+D.get(m.group(2),m.group(2))+'"',h)
    return h
res=trhtml(head)+js2+trhtml(tail)
for a,b in P.get('html',[]):
    if a not in res: print('HTML MISS',a[:60])
    res=res.replace(a,b)
import base64 as _b64, os as _os
_ef=[x for x in P.get('embedfonts',[]) if _os.path.exists(x[2])]
if _ef:
    _ff='\n'.join("@font-face{font-family:'%s';src:url(data:font/woff2;base64,%s) format('woff2');font-weight:%d;font-display:swap}"%(f,_b64.b64encode(open(p,'rb').read()).decode(),w) for f,w,p in _ef)
    _k=res.index("@font-face{font-family:'HadaBatang'"); _e=res.index('\n',_k); res=res[:_e+1]+_ff+'\n'+res[_e+1:]
for fam in P.get('dropfonts',[]):
    res='\n'.join(l for l in res.split('\n') if not l.startswith("@font-face{font-family:'%s'"%fam))
open('../korea-assembly-%s.html'%L,'w',encoding='utf-8').write(res)
noc=re.sub(r'/\*.*?\*/','',re.sub(r'data:[a-z/+\-]+;base64,[A-Za-z0-9+/=]+','',res),flags=re.S)
noc=re.sub(r'//[^\n]*','',noc)
print('missing unique',len(miss),'hangul left (no comments)',len(re.findall(r'[가-힣]',noc)))
json.dump(sorted(miss,key=lambda x:-miss[x]),open('missing_%s.json'%L,'w'),ensure_ascii=False,indent=0)
