"""Genera model3.js (modelo V3 en JavaScript) con tablas de datos. Uso: gen_js2.py salida.js [params.json]"""
import re, json, sys
sys.path.insert(0, ".")
import importlib, os
M = importlib.import_module(os.environ.get('VIV_MODEL', 'v3_model'))
import engine

P = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
V = list(M.V)
NUM = re.compile(r"^-?[0-9.]+(?:e-?\d+)?$")
# aplicar parametros ajustados a las ecuaciones numericas
V2 = []
for n, e, u, c, v in V:
    if n in P and NUM.match(e.strip()):
        e = repr(round(float(P[n]), 8))
    V2.append((n, e, u, c, v))
M.V[:] = V2
m = engine.Model([v[:4] for v in V2])
names = [v[0] for v in V2]; eq = {v[0]: v[1] for v in V2}
idx = {n: i for i, n in enumerate(names)}

def js(expr):
    s = expr
    for w in m.WORDS: s = s.replace(w, f"@{idx[w]}@")
    s = s.replace("IF THEN ELSE", "ITE").replace("^", "**").replace("Time", "T")
    s = re.sub(r"(?<![<>=!])=(?!=)", "==", s)
    return re.sub(r"@(\d+)@", lambda mm: f"X[{mm.group(1)}]", s)

params = [n for n in names if NUM.match(eq[n].strip())]
aux = [n for n in m.order if n not in params and n not in m.lookups]
out = []
out.append("const NAMES=" + json.dumps(names, ensure_ascii=False) + ";")
out.append("const UNITS=" + json.dumps([v[2] for v in V2], ensure_ascii=False) + ";")
out.append("const NOTES=" + json.dumps([v[3] for v in V2], ensure_ascii=False) + ";")
out.append("const IDX={};NAMES.forEach((n,i)=>{IDX[n]=i});")
out.append("const ITE=(c,a,b)=>c?a:b, MIN=Math.min, MAX=Math.max;")
out.append("const PARAMS=[" + ",".join("{i:%d,v:%s}" % (idx[n], eq[n].strip()) for n in params) + "];")
out.append("const LOOK={" + ",".join("%d:{x:%s,y:%s}" % (idx[n], json.dumps(m.lookups[n][0]), json.dumps(m.lookups[n][1])) for n in m.lookups) + "};")
items = []
for n in m.order:
    if n in params: continue
    if n in m.lookups: items.append("{i:%d,l:1}" % idx[n])
    else: items.append("{i:%d,f:(X,T)=>%s}" % (idx[n], js(eq[n])))
out.append("const AUX=[" + ",".join(items) + "];")
st = []
for n, (rate, init) in m.stocks.items():
    st.append("{i:%d,rate:(X,T)=>%s,init:(X,T)=>%s}" % (idx[n], js(rate), js(init)))
out.append("const STK=[" + ",".join(st) + "];")
out.append("""const NSTEP=3360, DT=0.25;
const LKARR={};
(function(){for(const k in LOOK){const xs=LOOK[k].x,ys=LOOK[k].y,a=new Float64Array(NSTEP+1);let j=0;
  for(let s=0;s<=NSTEP;s++){const t=s*DT;if(t<=xs[0])a[s]=ys[0];else if(t>=xs[xs.length-1])a[s]=ys[ys.length-1];
   else{while(xs[j+1]<t)j++;const f=(t-xs[j])/(xs[j+1]-xs[j]);a[s]=ys[j]+f*(ys[j+1]-ys[j]);}}
  LKARR[k]=a;}})();
function simulate(ov,want){
  const X=new Float64Array(NAMES.length);
  for(const p of PARAMS){const n=NAMES[p.i];X[p.i]=(ov&&ov[n]!==undefined)?ov[n]:p.v;}
  for(const a of AUX){if(a.l)X[a.i]=LKARR[a.i][0];else{const r=a.f(X,0);X[a.i]=Number.isFinite(r)?r:0;}}
  for(const s of STK){X[s.i]=s.init(X,0);}
  const res={};for(const w of want)res[w]=new Float64Array(841);
  const d=new Float64Array(STK.length);
  for(let k=0;k<=NSTEP;k++){
    const T=k*DT;
    for(const a of AUX){if(a.l)X[a.i]=LKARR[a.i][k];else X[a.i]=a.f(X,T);}
    if(k%4===0){const m=k/4;for(const w of want)res[w][m]=X[IDX[w]];}
    if(k===NSTEP)break;
    for(let j=0;j<STK.length;j++)d[j]=STK[j].rate(X,T);
    for(let j=0;j<STK.length;j++)X[STK[j].i]+=d[j]*DT;
  }
  return res;
}""")
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out) + "\n")
print("params", len(params), "aux", len(aux), "stocks", len(m.stocks), "lookups", len(m.lookups), "bytes", sum(len(x) for x in out))
