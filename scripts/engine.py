"""Motor generico: lee ecuaciones en sintaxis Vensim (lista V) y simula por Euler con codigo generado.
Soporta INTEG, IF THEN ELSE, MIN, MAX, ^, Time y WITH LOOKUP(Time, ([..],(x,y),...))."""
import re

class Model:
    def __init__(self, V):
        self.V = V
        self.names = [v[0] for v in V]
        self.eq = {v[0]: v[1] for v in V}
        self.idx = {n: i for i, n in enumerate(self.names)}
        self.WORDS = sorted(self.names, key=len, reverse=True)
        self.lookups = {}          # nombre -> (xs, ys)
        self.stocks = {}
        self.aux = []
        self._compile()

    def refs(self, expr):
        found, s = [], expr
        for w in self.WORDS:
            if w in s:
                found.append(w); s = s.replace(w, " ")
        return found

    def _lookup(self, n, e):
        m = re.match(r"^WITH LOOKUP\(Time,\s*\(\[.*?\],(.*)\)\)$", e.strip())
        if not m: return False
        pts = re.findall(r"\(\s*([-\d.eE+]+)\s*,\s*([-\d.eE+]+)\s*\)", m.group(1))
        self.lookups[n] = ([float(a) for a, b in pts], [float(b) for a, b in pts])
        return True

    def _py(self, expr):
        s = expr
        for w in self.WORDS:
            s = s.replace(w, f"@{self.idx[w]}@")
        s = s.replace("IF THEN ELSE", "ITE").replace("^", "**").replace("Time", "T")
        s = re.sub(r"(?<![<>=!])=(?!=)", "==", s)
        return re.sub(r"@(\d+)@", lambda m: f"v{m.group(1)}", s)

    def _compile(self):
        deps = {}
        for n in self.names:
            e = self.eq[n]
            if self._lookup(n, e):
                deps[n] = []; continue
            m = re.match(r"INTEG\((.*),\s*([^,]*)\)$", e)
            if m:
                self.stocks[n] = (m.group(1), m.group(2)); continue
            deps[n] = self.refs(e)
        order, seen = [], set()
        def visit(n, stack=()):
            if n in seen or n in self.stocks: return
            if n in stack: raise RuntimeError("bucle algebraico: " + " -> ".join(stack + (n,)))
            for d in deps[n]: visit(d, stack + (n,))
            seen.add(n); order.append(n)
        for n in deps: visit(n)
        self.order = order

    def source(self, want):
        """Codigo Python de la funcion de simulacion."""
        L = ["def sim(P, nsteps, dt, LK):", "    ITE=lambda c,a,b: a if c else b", "    MIN=min; MAX=max"]
        L.append("    " + "; ".join(f"v{i}=0.0" for i in range(len(self.names))))
        # parametros (ecuacion numerica) desde P si existen
        for n in self.order:
            i = self.idx[n]; e = self.eq[n]
            if re.fullmatch(r"-?[0-9.]+(?:e-?\d+)?", e.strip()):
                L.append(f"    v{i} = P.get({n!r}, {e.strip()})")
        for n, (rate, init) in self.stocks.items():
            L.append(f"    # init {n}")
        L.append("    T = 0.0")
        # inicial: evaluar auxiliares sin dependencia de stocks no es necesario: stocks se inician con su valor
        # primero poner todo a 0 y evaluar parametros derivados que alimentan a las iniciales
        for n in self.order:
            i = self.idx[n]; e = self.eq[n]
            if re.fullmatch(r"-?[0-9.]+(?:e-?\d+)?", e.strip()): continue
            if n in self.lookups: L.append(f"    v{i} = LK[{n!r}][0]")
            else: L.append(f"    try:\n        v{i} = {self._py(e)}\n    except ZeroDivisionError:\n        v{i} = 0.0")
        for n, (rate, init) in self.stocks.items():
            L.append(f"    v{self.idx[n]} = {self._py(init)}")
        rec = {w: self.idx[w] for w in want}
        L.append("    out = {" + ", ".join(f"{w!r}: [0.0]*({'nsteps'}//int(round(1/dt))+1)" for w in want) + "}")
        L.append("    per = int(round(1/dt))")
        L.append("    for k in range(nsteps+1):")
        L.append("        T = k*dt")
        for n in self.order:
            i = self.idx[n]; e = self.eq[n]
            if re.fullmatch(r"-?[0-9.]+(?:e-?\d+)?", e.strip()): continue
            if n in self.lookups: L.append(f"        v{i} = LK[{n!r}][k]")
            else: L.append(f"        v{i} = {self._py(e)}")
        L.append("        if k % per == 0:")
        L.append("            m = k // per")
        for w, i in rec.items():
            L.append(f"            out[{w!r}][m] = v{i}")
        L.append("        if k == nsteps: break")
        sts = list(self.stocks)
        for j, n in enumerate(sts):
            L.append(f"        d{j} = {self._py(self.stocks[n][0])}")
        for j, n in enumerate(sts):
            L.append(f"        v{self.idx[n]} += d{j}*dt")
        L.append("    return out")
        return "\n".join(L)

    def make(self, want, months, dt):
        nsteps = int(round(months / dt))
        LK = {}
        for n, (xs, ys) in self.lookups.items():
            arr = []
            j = 0
            for k in range(nsteps + 1):
                t = k * dt
                if t <= xs[0]: arr.append(ys[0])
                elif t >= xs[-1]: arr.append(ys[-1])
                else:
                    while xs[j + 1] < t: j += 1
                    f = (t - xs[j]) / (xs[j + 1] - xs[j]); arr.append(ys[j] + f * (ys[j + 1] - ys[j]))
            LK[n] = arr
        ns = {}
        exec(self.source(want), ns)
        sim = ns["sim"]
        return lambda P=None: sim(P or {}, nsteps, dt, LK)
