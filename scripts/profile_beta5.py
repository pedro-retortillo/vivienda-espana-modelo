import sys, os, json, math, time
os.environ["VIV_MODEL"] = "vfin_model"
sys.path.insert(0, ".")
import numpy as np
from scipy.optimize import least_squares
import calib as C
import run_calib as R
beta = float(sys.argv[1])
BASE = json.load(open("params_final5.json"))
SPACE = {"Sensibilidad margen": (0.05, 6.0), "Fraccion suelo": (0.1, 0.7), "tau obra": (6.0, 48.0), "Exponente inventario": (0.0, 6.0), "Elasticidad credito obra": (0.0, 1.5),
 "Esfuerzo maximo": (0.15, 0.9), "Ahorro anios": (0.2, 5.0), "Elasticidad acceso": (0.2, 8.0), "Relacion precio capacidad": (0.3, 2.0), "Velocidad financiera": (0.0, 0.2),
 "Fraccion hipotecada": (0.2, 1.0), "Fraccion vida media": (0.2, 1.0), "Velocidad precio": (0.005, 0.3), "Elasticidad hogares": (0.1, 2.0), "Techo desequilibrio": (0.3, 3.0),
 "tau expectativa": (3.0, 60.0), "Elasticidad expectativa hogares": (0.0, 15.0), "Elasticidad empleo": (0.0, 25.0)}
NAMES = list(SPACE); lo = np.array([SPACE[n][0] for n in NAMES]); hi = np.array([SPACE[n][1] for n in NAMES])
KW = dict(w_parque=4.0, w_precio=1.0, w_term=1.5, w_deuda=0.5)
FIJOS = {"tau deterioro": 2400.0, "tau demolicion": 1500.0, "Exponente edad": 1.0}
def mk(x):
    P = dict(FIJOS); P.update(dict(zip(NAMES, x))); P["Sensibilidad inversora"] = beta; P["Interruptor precio forzado"] = 0.0; return P
def fun(x):
    try: return C.residuals(mk(x), 2024, **KW)
    except Exception: return np.full(100, 10.0)
x0 = np.array([min(max(BASE[n], SPACE[n][0]), SPACE[n][1]) for n in NAMES])
best = None
import random
rng = random.Random(7)
for k in range(5):
    xs = x0 if k == 0 else np.array([min(max(v * rng.uniform(0.6, 1.4), l), h) for v, l, h in zip(x0, lo, hi)])
    s = least_squares(fun, xs, bounds=(lo, hi), diff_step=1e-3, max_nfev=150, x_scale=(hi - lo))
    if best is None or s.cost < best.cost: best = s
P = mk(best.x)
out, o = R.metrics(P, "beta_i = %g" % beta)
json.dump({"beta": beta, "coste": 2 * best.cost, "metrics": out}, open("prof5_%g.json" % beta, "w"))
print("beta %g coste %.3f" % (beta, 2 * best.cost), flush=True)
