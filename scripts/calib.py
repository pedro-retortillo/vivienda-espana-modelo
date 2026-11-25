import sys, json, time, math, random
sys.path.insert(0, ".")
import numpy as np
from scipy.optimize import least_squares
import importlib, os
M = importlib.import_module(os.environ.get('VIV_MODEL', 'v3_model'))
import engine

m = engine.Model([v[:4] for v in M.V])
W = ["Parque fisico", "Precio", "Obra terminada", "Error balance parque", "Viviendas venta", "Hogares sin alojar", "Expectativa ge"] + [n for n in ("Deuda indice", "Credito indice") if n in M.names]
DT = 0.5
RUN = m.make(W, 528, DT)
PER = int(round(1 / DT))

import csv
term = {}
for r in csv.DictReader(open(M._m.D + "viviendas_iniciadas_terminadas_2003_2024.csv", encoding="utf-8")):
    term[int(r["anio"])] = float(r["total_terminadas"])

def tm(y): return 12 * (y - 1981) + 6
def outputs(P):
    return RUN(P)

def residuals(P, y_max, w_parque=3.0, w_precio=1.0, w_term=1.0, use_price=True, use_parque=True, use_term=True, w_deuda=0.0):
    o = RUN(P)
    r = []
    if use_parque:
        for y, v in M.parque.items():
            if y <= y_max and y <= 2023: r.append(w_parque * math.log(max(o["Parque fisico"][tm(y)], 1.0) / v))
    if use_price:
        for y in range(1981, min(y_max, 2024) + 1):
            r.append(w_precio * math.log(max(o["Precio"][tm(y)], 1.0) / M.precio[y]))
    if use_term:
        for y, v in term.items():
            if y <= y_max:
                a = sum(o["Obra terminada"][12 * (y - 1981):12 * (y - 1981) + 12]) / 1.0
                r.append(w_term * math.log(max(a, 1.0) / v))
    if w_deuda and "Deuda indice" in o:
        for y in range(1982, min(y_max, 2024) + 1):
            r.append(w_deuda * math.log(max(o["Deuda indice"][tm(y)], 1e-9) / o["Credito indice"][tm(y)]))
    return np.array(r)

SUPPLY = {  # nombre: (inicio, min, max). El deterioro y la demolicion no se ajustan: no hay datos que los identifiquen.
 "Sensibilidad margen": (1.0, 0.05, 6.0), "Fraccion suelo": (0.45, 0.1, 0.7), "tau obra": (18.0, 6.0, 48.0),
 "Exponente inventario": (1.5, 0.0, 6.0), "Elasticidad credito obra": (0.3, 0.0, 1.5)}
PRICE = {
 "Velocidad precio": (0.03, 0.005, 0.3), "Elasticidad asequibilidad": (1.0, 0.1, 3.0), "Elasticidad hogares": (1.0, 0.1, 2.0),
 "Elasticidad credito": (0.3, 0.0, 2.0), "Elasticidad tipos": (0.5, 0.0, 3.0), "Sensibilidad inversora": (20.0, 0.0, 80.0),
 "tau expectativa": (24.0, 3.0, 60.0), "Techo desequilibrio": (1.0, 0.3, 3.0)}

def fit(space, base, y_max, forced, restarts, seed, **kw):
    names = list(space)
    lo = np.array([space[n][1] for n in names]); hi = np.array([space[n][2] for n in names])
    rng = random.Random(seed)
    best = None
    for k in range(restarts):
        x0 = np.array([space[n][0] for n in names]) if k == 0 else np.array([rng.uniform(l, h) for l, h in zip(lo, hi)])
        def fun(x):
            P = dict(base); P.update(dict(zip(names, x))); P["Interruptor precio forzado"] = 1.0 if forced else 0.0
            try: return residuals(P, y_max, **kw)
            except Exception: return np.full(80, 10.0)
        try:
            s = least_squares(fun, x0, bounds=(lo, hi), diff_step=1e-3, max_nfev=60, x_scale=(hi - lo))
        except Exception as e:
            continue
        if best is None or s.cost < best.cost: best = s
    P = dict(base); P.update(dict(zip(names, best.x)))
    return P, best.cost

if __name__ == "__main__":
    t = time.time(); RUN({}); print("una simulacion: %.3f s" % (time.time() - t))
    t = time.time()
    for _ in range(20): RUN({})
    print("promedio 20: %.3f s" % ((time.time() - t) / 20))
