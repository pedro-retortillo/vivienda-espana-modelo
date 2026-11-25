"""Modelo de vivienda V3: V2 + obra frenada por inventario y credito + proyeccion 2025-2050 con palancas de politica."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2_model as _m
from v2_model import f, P0, H0, Vs0, C0, HORIZON as _H2, T, YEARS, parque, precio, epa, TARGET_PARQUE, TARGET_PRECIO, lk, gdp, cred, tipo_real, growth

HORIZON = 840            # enero de 1981 a diciembre de 2050
V = list(_m.V)

def _find(n):
    for i, v in enumerate(V):
        if v[0] == n: return i
    raise KeyError(n)
def upd(n, e=None, u=None, c=None, view="keep"):
    i = _find(n); a = V[i]
    V[i] = (a[0], a[1] if e is None else e, a[2] if u is None else u, a[3] if c is None else c, a[4] if view == "keep" else view)
def add(n, e, u, c, view=None):
    V.append((n, e, u, c, view))
def rename(old, new):
    i = _find(old); a = V[i]; V[i] = (new,) + a[1:]

# ---------- obra: inventario y credito ----------
upd("Inicio obra", "Inicio base*Politica obra efectiva*MAX(0, 1+Sensibilidad margen*Margen obra/Margen ref)*Factor inventario*Credito indice^Elasticidad credito obra",
    c="I_nuevo: margen x inventario x credito x politica.")
add("Factor inventario", "MIN(Tope factor inventario, (Disponibles ref/(Disponibles por mil hogares+0.001))^Exponente inventario)", "Dmnl",
    "La obra se frena si hay mas vivienda sin vender por hogar que en 1981.", "01")
add("Exponente inventario", "0.0", "Dmnl", "A CALIBRAR (0 = sin efecto).")
add("Tope factor inventario", "2.0", "Dmnl", "")
add("Disponibles ref", f(1000 * Vs0 / H0, 6), "Vivienda/Hogar", "Vacias en venta por mil hogares en 1981.")
add("Elasticidad credito obra", "0.0", "Dmnl", "A CALIBRAR (0 = sin efecto).")

# ---------- entradas externas y proyeccion ----------
rename("Hogares dato", "Hogares dato")
upd("Hogares objetivo", "Hogares dato*(1+Crecimiento hogares futuro)^(MAX(0,Time-522)/12)", c="H* = EPA hasta 2024; despues crece al ritmo de la proyeccion.", view="03")
rename("Ingreso indice", "Ingreso indice dato")
add("Ingreso indice", "Ingreso indice dato*(1+Crecimiento ingreso futuro)^(MAX(0,Time-522)/12)", "Dmnl", "Renta real relativa a 1981; despues crece al ritmo de la proyeccion.", "05")
rename("Tipo capital", "Tipo capital dato")
add("Tipo capital", "Tipo capital dato+IF THEN ELSE(Time>=Inicio politica, Politica tipos, 0)", "1/Year", "Tipo real; la politica puede sumarle puntos.", "05")
rename("Credito indice", "Credito indice dato")
add("Credito indice", "Credito indice dato*IF THEN ELSE(Time>=Inicio politica, Politica credito, 1)", "Dmnl", "Credito a hogares relativo a 1981 x politica.", "05")
add("Multiplicador inversor efectivo", "Multiplicador inversor*IF THEN ELSE(Time>=Inicio politica, Politica inversion, 1)", "Dmnl", "m_inv x politica.", "02")
add("Riesgo regulacion efectivo", "Riesgo regulacion+IF THEN ELSE(Time>=Inicio politica, Politica riesgo, 0)", "1/Year", "rho_pol + politica.", "02")
add("Politica obra efectiva", "IF THEN ELSE(Time>=Inicio politica, Politica obra, 1)", "Dmnl", "", "01")
add("Capacidad rehabilitacion efectiva", "Capacidad rehabilitacion*IF THEN ELSE(Time>=Inicio politica, Politica rehabilitacion, 1)", "Vivienda/Month", "", "01")
upd("Rehabilitacion", "MIN(Deterioradas/tau rehabilitacion, Capacidad rehabilitacion efectiva)")
upd("Demanda inversora", "Multiplicador inversor efectivo*Demanda base inversora*MAX(0, 1+Sensibilidad inversora*(Rentabilidad inversora-Rentabilidad ref))")
upd("Rentabilidad inversora", "12*Renta neta/Precio efectivo+Expectativa usada-Tipo capital-Coste mantenimiento-Riesgo regulacion efectivo")
for n, v, u, c in [
    ("Inicio politica", 528, "Month", "Mes (desde enero de 1981) en que empiezan las politicas: 528 = enero de 2025, justo despues del ultimo dato."),
    ("Politica inversion", 1.0, "Dmnl", "Multiplicador de la demanda inversora desde el inicio de la politica (1 = sin politica; 0,5 = recorte a la mitad)."),
    ("Politica riesgo", 0.0, "1/Year", "Puntos de riesgo regulatorio que se suman a la rentabilidad exigida."),
    ("Politica obra", 1.0, "Dmnl", "Multiplicador de los inicios de obra (impulso de la oferta)."),
    ("Politica rehabilitacion", 1.0, "Dmnl", "Multiplicador de la capacidad de rehabilitar."),
    ("Politica tipos", 0.0, "1/Year", "Puntos que se suman al tipo de interes real."),
    ("Politica credito", 1.0, "Dmnl", "Multiplicador del credito a hogares."),
    ("Crecimiento ingreso futuro", 0.01, "1/Year", "Crecimiento real anual de la renta tras 2024. SUPUESTO."),
    ("Crecimiento hogares futuro", 0.007, "1/Year", "Crecimiento anual de los hogares tras 2024 (INE: +11,1 % en 15 anos, escenario central)."),
]:
    add(n, f(v, 8), u, c, None)

# ---------- cuota hipotecaria: el tipo nominal abarata o encarece comprar ----------
_tipo_nom = {y: (_m.policy[y] + _m.SPREAD) / 100.0 for y in YEARS}
add("Tipo nominal dato", lk(_tipo_nom), "1/Year", "Tipo oficial + 1,5 puntos (nominal).", "05")
add("Tipo nominal", "Tipo nominal dato+IF THEN ELSE(Time>=Inicio politica, Politica tipos, 0)", "1/Year", "Tipo hipotecario nominal; la politica puede sumarle puntos.", "05")
add("Carga hipotecaria indice", "(Tipo nominal+Amortizacion anual)/Carga ref", "Dmnl", "Cuota anual por euro prestado (intereses + amortizacion), relativa a 1981.", "02")
add("Factor tipos", "Carga hipotecaria indice^(-Elasticidad tipos)", "Dmnl", "Una cuota mas baja aumenta la demanda de los hogares.", "02")
add("Elasticidad tipos", "0.0", "Dmnl", "A CALIBRAR (0 = sin efecto).")
add("Amortizacion anual", "0.04", "1/Year", "Amortizacion de una hipoteca a 25 anos.")
add("Carga ref", f(_tipo_nom[1981] + 0.04, 8), "1/Year", "Cuota anual por euro prestado en 1981.")
upd("Demanda hogares", "Demanda base hogares*(Hogares/Hogares ref)^Elasticidad hogares*((Ingreso/Precio efectivo)/(Ingreso ref/Precio ref))^Elasticidad asequibilidad*Factor credito*Factor tipos")

# ---------- utilidades para el dibujo y el motor ----------
import re as _re
names = [v[0] for v in V]
eq = {v[0]: v[1] for v in V}
WORDS = sorted(names, key=len, reverse=True)
def refs(expr):
    found, s = [], expr
    for w in WORDS:
        if w in s:
            found.append(w); s = s.replace(w, " ")
    return found

if __name__ == "__main__":
    import engine
    W = ["Parque fisico", "Precio", "Obra terminada", "Error balance parque"]
    m3 = engine.Model([v[:4] for v in V]); m2 = engine.Model([v[:4] for v in _m.V])
    a = m3.make(W, 528, 0.25)(); b = m2.make(W, 528, 0.25)()
    print("V3 vs V2 con palancas neutras: dif max parque %.3g, precio %.3g, obra %.3g" % tuple(max(abs(x - y) for x, y in zip(a[k], b[k])) for k in ("Parque fisico", "Precio", "Obra terminada")))
    c = m3.make(W, 840, 0.25)(); print("proyeccion a 2050: parque %.0f, precio %.0f, maxerr %.1e" % (c["Parque fisico"][-1], c["Precio"][-1], max(abs(x) for x in c["Error balance parque"])))
