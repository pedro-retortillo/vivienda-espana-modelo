"""Modelo V6: V5 + COSTES DE CONSTRUCCION con series reales (INE: materiales y mano de obra, 1995-2024),
sobrecoste normativo por escalones y un PRECIO DE COSTE que actua como suelo de largo plazo del precio.
Euros constantes de 2010. Con USA_COSTE_REAL=0 el modelo reproduce la V5 (cifras de coste fijas)."""
import os, sys, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vfin_model as _v5
from vfin_model import f, lk, YEARS, T, HORIZON, P0, rd, _m
D = _m.D
V = list(_v5.V)
def _find(n):
    for i, v in enumerate(V):
        if v[0] == n: return i
    raise KeyError(n)
def upd(n, e=None, view="keep", c=None, u=None):
    i = _find(n); a = V[i]
    V[i] = (a[0], a[1] if e is None else e, a[2] if u is None else u, a[3] if c is None else c, a[4] if view == "keep" else view)
def add(n, e, u, c, view=None): V.append((n, e, u, c, view))

# ---------------- series reales del INE (1981=1; antes de 1995 se mantiene constante: supuesto) ----------------
rows = rd("INE_costes_construccion_1995_2025.csv")
k_mo, k_mat, k_ipc = [k for k in rows[0].keys() if k != "anio"]
mo_r, mat_r = {}, {}
for r in rows:
    y = int(r["anio"])
    mo_r[y] = float(r[k_mo]) / float(r[k_ipc]); mat_r[y] = float(r[k_mat]) / float(r[k_ipc])
for y in range(1981, 1995): mo_r[y] = 1.0; mat_r[y] = 1.0
mo_r = {y: mo_r[y] for y in YEARS if y in mo_r}; mat_r = {y: mat_r[y] for y in YEARS if y in mat_r}
# escalones normativos (fechas de entrada en vigor: CTE 2006-07, DB-HE 2013 -> 2014, DB-HE 2019 -> 2020); el tamano es supuesto
esc = {}
for y in YEARS:
    esc[y] = (1.0 if y >= 2007 else 0.0) + (1.0 if y >= 2014 else 0.0) + (1.0 if y >= 2020 else 0.0)

add("Indice materiales dato", lk(mat_r), "Dmnl", "Precio real de los materiales de construccion (INE, media simple de 8 materiales, 1995=100 -> relativo a 1981). Antes de 1995 se mantiene constante (supuesto).", "02")
add("Indice mano obra dato", lk(mo_r), "Dmnl", "Coste real de la mano de obra en construccion (INE, relativo a 1981). El INE lo construye con el 85 % de la variacion salarial general: es una convencion. Antes de 1995, constante (supuesto).", "02")
add("Deriva coste real", "0.0", "1/Year", "Crecimiento anual real de los costes despues de 2024 (supuesto de escenario).")
add("Indice materiales", "IF THEN ELSE(Time>522, Indice materiales dato*(1+Deriva coste real)^((Time-522)/12), Indice materiales dato)", "Dmnl", "Indice de materiales usado: el dato hasta 2024 y despues, el dato por la deriva de escenario.", "02")
add("Indice mano obra", "IF THEN ELSE(Time>522, Indice mano obra dato*(1+Deriva coste real)^((Time-522)/12), Indice mano obra dato)", "Dmnl", "Indice de mano de obra usado.", "02")
add("Escalones normativos", lk(esc), "Dmnl", "Numero de cambios normativos acumulados (CTE 2006, DB-HE 2013, DB-HE 2019). Cada uno se aplica con una rampa de un ano.", "02")
add("Escala normativa", "0.0", "Dmnl", "SUPUESTO: sobrecoste de cada escalon normativo, como fraccion del precio de 1981. No hay dato abierto que lo fije.")
add("Coste normativa", "Escala normativa*Escalones normativos*%s" % f(P0, 4), "Euro/Metro2", "Sobrecoste acumulado por normativa (eficiencia energetica, accesibilidad, seguridad).", "02")
add("Politica coste", "1.0", "Dmnl", "Multiplicador del coste de construccion desde el inicio de la politica (por ejemplo, 0,9 = reducir un 10 % cargas y sobrecostes).")
upd("Coste materiales", "%s*Indice materiales" % f(0.28 * P0, 4), c="Materiales: 28 % del precio de 1981 x indice real de materiales (INE).")
upd("Coste mano obra", "%s*Indice mano obra" % f(0.22 * P0, 4), c="Mano de obra: 22 % del precio de 1981 x indice real de mano de obra (INE).")
upd("Coste energia transporte", "%s*Indice materiales" % f(0.02 * P0, 4), c="Energia y transporte: 2 % del precio de 1981 x indice de materiales (la energia esta en el).")
add("Coste construccion", "(Coste materiales+Coste mano obra+Coste energia transporte+Coste calidad+Coste otros+Coste normativa)*IF THEN ELSE(Time>=Inicio politica, Politica coste, 1)", "Euro/Metro2", "Coste de construir un m2 sin el suelo.", "02")
upd("Coste obra", "Coste suelo+Coste construccion")
add("Precio de coste", "(Coste construccion+Margen minimo)/(1-Fraccion suelo)", "Euro/Metro2", "Precio por debajo del cual no sale a cuenta construir: coste + margen minimo, con el suelo como fraccion del precio.", "02")
add("Brecha coste", "Precio efectivo/Precio de coste-1", "Dmnl", "Precio frente a su precio de coste.", "02")
add("Velocidad coste", "0.0", "1/Month", "A CALIBRAR: rapidez con que el precio sube hacia su precio de coste cuando cae por debajo.")
i = _find("Cambio bruto precio")
upd("Cambio bruto precio", V[i][1] + "-Velocidad coste*Precio*MIN(0, Brecha coste)")

# ---------------- vista 07: costes y composicion del precio ----------------
for _n in ["Indice materiales dato", "Indice mano obra dato", "Deriva coste real", "Indice materiales", "Indice mano obra", "Escalones normativos", "Escala normativa",
           "Coste normativa", "Politica coste", "Coste materiales", "Coste mano obra", "Coste energia transporte", "Coste calidad", "Coste otros", "Coste construccion",
           "Coste suelo", "Coste obra", "Precio de coste", "Brecha coste", "Velocidad coste", "Fraccion suelo", "Margen minimo", "Margen obra"]:
    upd(_n, view="07")

import re as _re
names = [v[0] for v in V]; eq = {v[0]: v[1] for v in V}
WORDS = sorted(names, key=len, reverse=True)
def refs(expr):
    found, s = [], expr
    for w in WORDS:
        if w in s: found.append(w); s = s.replace(w, " ")
    return found
parque, precio, TARGET_PARQUE, TARGET_PRECIO = _v5.parque, _v5.precio, _v5.TARGET_PARQUE, _v5.TARGET_PRECIO
epa, gdp, tipo_hip, ltv, plazo = _v5.epa, _v5.gdp, _v5.tipo_hip, _v5.ltv, _v5.plazo

if __name__ == "__main__":
    import json, engine
    m = engine.Model([v[:4] for v in V])
    W = ["Precio", "Parque fisico", "Obra terminada", "Coste construccion", "Precio de coste", "Margen obra", "Inicio obra", "Brecha coste", "Error balance parque"]
    run = m.make(W, 528, 0.25)
    P5 = json.load(open("params_final4.json")); P5.update(json.load(open("params_final5.json")))
    o = run(P5)
    print("V6 con parametros de la V5 (sin velocidad de coste, sin normativa):")
    for y in (1981, 1990, 2000, 2007, 2013, 2021, 2022, 2024):
        t = 12 * (y - 1981) + 6
        print("  %d precio %6.0f (dato %6.0f) coste constr %5.0f precio coste %6.0f margen %7.0f inicios %6.0f/mes" % (
            y, o["Precio"][t], precio[y], o["Coste construccion"][t], o["Precio de coste"][t], o["Margen obra"][t], o["Inicio obra"][t]))
    print("error balance max %.1e" % max(abs(x) for x in o["Error balance parque"]))
