"""Compara duas versões da mesma sequência (saídas do dump_prproj.py).
  python3 comparar_prproj.py claude.tsv final.tsv [--desloca 1]
--desloca N: o final tem N faixas novas logo acima da V1 (ex.: camada de cor do Juliano).
Alinha os tempos pela V1 (in da fonte) e lista REMOVIDO / NOVO / MUDOU por clipe."""
import sys
def load(f):
    R=[]
    for l in open(f,encoding='utf-8'):
        p=l.rstrip('\n').split('\t'); R.append((p[0],float(p[1]),float(p[2]),float(p[3]),p[4],p[5]))
    return R
A=load(sys.argv[1]); D=load(sys.argv[2])
SH=int(sys.argv[sys.argv.index('--desloca')+1]) if '--desloca' in sys.argv else 0
va=[r for r in A if r[0]=='V1']; vd=[r for r in D if r[0]=='V1']
def mp(t):
    for a,d in zip(va,vd):
        if a[1]-0.01<=t<a[2]+0.01:
            src=a[3]+(t-a[1]); return round(d[1]+(src-d[3]),2)
    return t
def fmt(t): return f"{int(t//60)}:{t%60:05.2f}"
tracks=sorted({r[0] for r in A if r[0][0]=='V' and r[0]!='V1'},key=lambda x:int(x[1:]))
used=set()
out=[]
for ta in tracks:
    td='V'+str(int(ta[1:])+SH)
    da=[r for r in D if r[0]==td]
    for r in [r for r in A if r[0]==ta]:
        s,e=mp(r[1]),mp(r[2])
        best=None
        for i,d in enumerate(da):
            if (td,i) in used or d[4]!=r[4]: continue
            dd=abs(d[1]-s)+abs(d[2]-e)
            if dd<3 and (best is None or dd<best[0]): best=(dd,i,d)
        if best is None:
            # procurar em qualquer faixa
            alt=[d for d in D if d[4]==r[4] and abs(d[1]-s)<1.5]
            out.append((s,f"REMOVIDO  {ta}->{td} {fmt(s)}-{fmt(e)} {r[4]} [{r[5]}]"+(f"  (há em {alt[0][0]} {fmt(alt[0][1])}-{fmt(alt[0][2])})" if alt else "")))
        else:
            used.add((td,best[1])); d=best[2]
            ch=[]
            if abs(d[1]-s)>0.15 or abs(d[2]-e)>0.15: ch.append(f"tempo {fmt(s)}-{fmt(e)} -> {fmt(d[1])}-{fmt(d[2])}")
            if abs(d[3]-r[3])>0.15 and r[3]<3000: ch.append(f"in {r[3]:.2f}->{d[3]:.2f}")
            if d[5]!=r[5]: ch.append(f"efeitos [{r[5]}] -> [{d[5]}]")
            if ch: out.append((s,f"MUDOU     {td} {r[4]}: "+'; '.join(ch)))
for td in sorted({r[0] for r in D if r[0][0]=='V' and int(r[0][1:])>1+SH},key=lambda x:int(x[1:])):
    for i,d in enumerate([r for r in D if r[0]==td]):
        if (td,i) not in used: out.append((d[1],f"NOVO      {td} {fmt(d[1])}-{fmt(d[2])} {d[4]} [{d[5]}]"))
for s,l in sorted(out): print(l)
