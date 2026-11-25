"""Banco de pruebas: V3 + mecanismos candidatos que explican el precio. Todos apagados por defecto (parametro = 0)."""
import os, sys, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v3_model as _v3
import v2_model as _m
from v3_model import V as _V3, f, lk, YEARS, T, HORIZON, parque, precio, epa, gdp, TARGET_PARQUE, TARGET_PRECIO, P0, H0, Vs0, C0
V = list(_V3)
def _find(n):
    for i, v in enumerate(V):
        if v[0] == n: return i
    raise KeyError(n)
def upd(n, e=None, view="keep", c=None):
    i = _find(n); a = V[i]; V[i] = (a[0], a[1] if e is None else e, a[2], a[3] if c is None else c, a[4] if view == "keep" else view)
def add(n, e, u, c, view=None): V.append((n, e, u, c, view))
D = _m.D
def rd(fn): return list(csv.DictReader(open(D + fn, encoding="utf-8")))
paro = {int(r["anio"]): float(r["paro_pct"]) / 100.0 for r in rd("WB_Espana_paro_pct_1975_2025.csv")}
pop = {int(r["anio"]): float(r["poblacion"]) for r in rd("WB_Espana_poblacion_1975_2025.csv")}
cons = {int(r["anio"]): float(r["consumo_privado_real_usd2015"]) / pop[int(r["anio"])] for r in rd("WB_Espana_consumo_privado_real_1975_2025.csv")}
rnb = {int(r["anio"]): float(r["rnb_per_capita_usd_const_2015"]) for r in rd("WB_Espana_RNB_per_capita_USD2015_1975_2024.csv")}
rnb[2025] = rnb[2024]
# --- selector de la medida de renta ---
upd("Ingreso indice dato", "IF THEN ELSE(Selector ingreso=1, Ingreso indice consumo, IF THEN ELSE(Selector ingreso=2, Ingreso indice RNB, Ingreso indice PIB))")
add("Ingreso indice PIB", lk({y: gdp[y] / gdp[1981] for y in YEARS}), "Dmnl", "PIB per capita real / 1981.", "05")
add("Ingreso indice consumo", lk({y: cons[y] / cons[1981] for y in YEARS}), "Dmnl", "Consumo privado real per capita / 1981.", "05")
add("Ingreso indice RNB", lk({y: rnb[y] / rnb[1981] for y in YEARS}), "Dmnl", "Renta nacional bruta per capita real / 1981.", "05")
add("Selector ingreso", "0", "Dmnl", "0 = PIB, 1 = consumo privado, 2 = renta nacional bruta.")
# --- candidato 1: paro ---
add("Paro dato", lk(paro), "Dmnl", "Tasa de paro (INE/Banco Mundial).", "05")
add("Paro ref", f(paro[1981], 8), "Dmnl", "Paro de 1981.")
add("Elasticidad empleo", "0.0", "Dmnl", "A PROBAR: la demanda cae con el paro.")
add("Factor empleo", "2.718281828^(-Elasticidad empleo*(Paro dato-Paro ref))", "Dmnl", "Efecto del paro sobre la demanda de los hogares.", "02")
# --- candidato 2: ancla precio/ingreso ---
add("Brecha fundamental", "Precio efectivo/(Precio ref*Ingreso indice^Exponente ancla)-1", "Dmnl", "Precio frente a lo que justificaria la renta.", "02")
add("Velocidad ancla", "0.0", "1/Month", "A PROBAR: el precio vuelve hacia la relacion precio/renta.")
add("Exponente ancla", "1.0", "Dmnl", "")
upd("Cambio bruto precio", "Velocidad precio*Precio*MIN(Presion-1, Techo desequilibrio)-Velocidad ancla*Precio*Brecha fundamental")
# --- candidato 3: tipo real ---
add("Tipo capital ref", f(_m.tipo_real[1981], 8), "1/Year", "Tipo real de 1981.")
add("Elasticidad tipo real", "0.0", "Dmnl", "A PROBAR: la demanda cae cuando sube el tipo real.")
add("Factor tipo real", "2.718281828^(-Elasticidad tipo real*(Tipo capital-Tipo capital ref))", "Dmnl", "Efecto del tipo real sobre la demanda de los hogares.", "02")
# --- candidato 4: los hogares tambien compran por expectativas ---
add("Elasticidad expectativa hogares", "0.0", "Dmnl", "A PROBAR: los hogares compran mas si esperan que el precio suba.")
add("Factor expectativa hogares", "2.718281828^(Elasticidad expectativa hogares*Expectativa usada)", "Dmnl", "Efecto de la expectativa sobre la demanda de los hogares.", "02")
upd("Demanda hogares", "Demanda base hogares*(Hogares/Hogares ref)^Elasticidad hogares*((Ingreso/Precio efectivo)/(Ingreso ref/Precio ref))^Elasticidad asequibilidad*Factor credito*Factor tipos*Factor empleo*Factor tipo real*Factor expectativa hogares")
import re as _re
names = [v[0] for v in V]; eq = {v[0]: v[1] for v in V}
WORDS = sorted(names, key=len, reverse=True)
def refs(expr):
    found, s = [], expr
    for w in WORDS:
        if w in s: found.append(w); s = s.replace(w, " ")
    return found
