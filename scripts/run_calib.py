import sys, json, time, math
sys.path.insert(0, ".")
import numpy as np
import calib as C
M = C.M

def metrics(P, label):
    P = dict(P); P["Interruptor precio forzado"] = 0.0
    o = C.RUN(P)
    pr_all, pa_all, te_all = [], [], []
    out = {}
    for tag, (a, b) in {"1981-2007": (1981, 2007), "2008-2024": (2008, 2024), "1981-2024": (1981, 2024)}.items():
        pr = [100 * (o["Precio"][C.tm(y)] / M.precio[y] - 1) for y in range(a, b + 1)]
        pa = [100 * (o["Parque fisico"][C.tm(y)] / v - 1) for y, v in M.parque.items() if a <= y <= min(b, 2023)]
        te = [100 * (sum(o["Obra terminada"][12 * (y - 1981):12 * (y - 1981) + 12]) / v - 1) for y, v in C.term.items() if a <= y <= b]
        rms = lambda x: math.sqrt(sum(v * v for v in x) / len(x)) if x else float("nan")
        out[tag] = (rms(pr), rms(pa), rms(te))
    print("  %-34s" % label + "  ".join("%s: precio %.1f%% parque %.1f%% obra %.1f%%" % ((t,) + v) for t, v in out.items()))
    return out, o

if __name__ == "__main__":
    t0 = time.time()
    base = {}
    print("== Punto de partida (V3 sin ajustar)")
    metrics(base, "sin ajustar")

    print("\n== Diagnostico: se ajusta solo con 1981-2007 y se mira 2008-2024")
    Ps, cs = C.fit(C.SUPPLY, base, 2007, True, 16, 1, use_price=False)
    metrics(Ps, "oferta (precio forzado)")
    Pp, cp = C.fit(C.PRICE, Ps, 2007, False, 20, 2, use_term=True)
    metrics(Pp, "+ precio (libre)")
    PA = Pp
    json.dump(PA, open("params_diag_2007.json", "w"), indent=1)

    print("\n== Ajuste definitivo con 1981-2024")
    Ps, cs = C.fit(C.SUPPLY, base, 2024, True, 16, 3, use_price=False)
    metrics(Ps, "oferta (precio forzado)")
    Pp, cp = C.fit(C.PRICE, Ps, 2024, False, 24, 4)
    metrics(Pp, "+ precio (libre)")
    both = dict(C.SUPPLY); both.update(C.PRICE)
    Pj, cj = C.fit({k: (Pp.get(k, v[0]),) + v[1:] for k, v in both.items()}, Pp, 2024, False, 12, 5)
    out, o = metrics(Pj, "ajuste conjunto")
    json.dump(Pj, open("params_final.json", "w"), indent=1)
    print("\nParametros ajustados:")
    for k in list(C.SUPPLY) + list(C.PRICE):
        print("  %-28s %10.4g   (rango %g - %g)" % (k, Pj[k], both[k][1], both[k][2]))
    print("\ntiempo total %.0f s" % (time.time() - t0))
