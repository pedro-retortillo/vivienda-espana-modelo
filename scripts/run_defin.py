import sys, os, json, time, math
os.environ["VIV_MODEL"] = "vfin_model"
sys.path.insert(0, ".")
import numpy as np
from scipy.optimize import differential_evolution, least_squares
import calib as C
import run_calib as R
import engine
name = sys.argv[1]; seed = int(sys.argv[2]); ymax = int(sys.argv[3]) if len(sys.argv) > 3 else 2024
SPACE = {
 "Sensibilidad margen": (0.05, 6.0), "Fraccion suelo": (0.1, 0.7), "tau obra": (6.0, 48.0), "Exponente inventario": (0.0, 6.0), "Elasticidad credito obra": (0.0, 1.5),
 "Esfuerzo maximo": (0.15, 0.9), "Ahorro anios": (0.2, 5.0), "Elasticidad acceso": (0.2, 8.0), "Relacion precio capacidad": (0.3, 2.0), "Velocidad financiera": (0.0, 0.2),
 "Fraccion hipotecada": (0.2, 1.0), "Fraccion vida media": (0.2, 1.0),
 "Velocidad precio": (0.005, 0.3), "Elasticidad hogares": (0.1, 2.0), "Techo desequilibrio": (0.3, 3.0), "tau expectativa": (3.0, 60.0),
 "Elasticidad expectativa hogares": (0.0, 15.0), "Elasticidad empleo": (0.0, 25.0), "Sensibilidad inversora": (0.0, 80.0)}
FIJOS = {"tau deterioro": 2400.0, "tau demolicion": 1500.0, "Exponente edad": 1.0}
if name.startswith("B"): SPACE["Sensibilidad inversora"] = (0.0, 0.0001)   # control: canal inversor apagado
if name.startswith("C"):   # control: sin piezas estadisticas (expectativas de hogares y paro)
    SPACE["Elasticidad expectativa hogares"] = (0.0, 0.0001); SPACE["Elasticidad empleo"] = (0.0, 0.0001)
NAMES = list(SPACE); BOUNDS = [SPACE[n] for n in NAMES]
KW = dict(w_parque=4.0, w_precio=1.0, w_term=1.5, w_deuda=0.5)
V4 = json.load(open("params_final4.json")); V4.update(json.load(open("params_final5.json")))
DEF = {"Esfuerzo maximo": 0.35, "Ahorro anios": 1.5, "Elasticidad acceso": 2.0, "Relacion precio capacidad": 0.8, "Velocidad financiera": 0.02, "Fraccion hipotecada": 0.6, "Fraccion vida media": 0.5}
x0 = np.array([min(max(V4.get(n, DEF.get(n, 0.0)), SPACE[n][0]), SPACE[n][1]) for n in NAMES])
def mk(x):
    P = dict(FIJOS); P.update(dict(zip(NAMES, x))); P["Interruptor precio forzado"] = 0.0; return P
def obj(x):
    try:
        r = C.residuals(mk(x), ymax, **KW); v = float(np.sum(r * r)); return v if math.isfinite(v) else 1e6
    except Exception: return 1e6
t0 = time.time()
print("coste del punto de partida: %.3f" % obj(x0), flush=True)
res = differential_evolution(obj, BOUNDS, seed=seed, popsize=15, maxiter=110, tol=1e-8, mutation=(0.4, 0.9), recombination=0.8, polish=False, init="sobol", x0=x0)
lo = np.array([b[0] for b in BOUNDS]); hi = np.array([b[1] for b in BOUNDS])
fun = lambda x: C.residuals(mk(x), ymax, **KW)
s = least_squares(fun, res.x, bounds=(lo, hi), diff_step=1e-3, max_nfev=60, x_scale=np.maximum(hi - lo, 1e-9))
P = mk(s.x)
out, o = R.metrics(P, "%s semilla %d (ajuste hasta %d)" % (name, seed, ymax))
# desviacion de la deuda
oo = C.RUN(P)
dv = [100 * (oo["Deuda indice"][C.tm(y)] / oo["Credito indice"][C.tm(y)] - 1) for y in range(1982, 2025)]
print("  deuda frente al BIS: desviacion media %.1f %%, rms %.1f %%" % (sum(dv) / len(dv), math.sqrt(sum(v * v for v in dv) / len(dv))))
json.dump({"params": P, "metrics": out, "coste": 2 * s.cost, "deuda_rms": math.sqrt(sum(v * v for v in dv) / len(dv))}, open("fitF_%s_%d.json" % (name, seed), "w"), indent=1)
print("fin %s semilla %d: coste %.3f en %.0f s" % (name, seed, 2 * s.cost, time.time() - t0), flush=True)
