"""Modelo V5: V4 sin el ancla estadistica + subsistema de FINANCIACION (capacidad de compra hipotecaria,
deuda hipotecaria) + rentabilidad real del alquiler. Euros constantes de 2010."""
import os, sys, csv, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v4_model as _v4
from v4_model import f, lk, YEARS, T, HORIZON, parque, precio, epa, gdp, TARGET_PARQUE, TARGET_PRECIO, P0, H0, Vs0, C0
_m = _v4._m
D = _m.D
V = list(_v4.V)

REMOVE = {"Factor credito", "Elasticidad credito", "Factor tipos", "Carga hipotecaria indice", "Elasticidad tipos", "Carga ref", "Amortizacion anual",
          "Factor tipo real", "Elasticidad tipo real", "Tipo capital ref", "Velocidad ancla", "Exponente ancla", "Brecha fundamental", "Elasticidad asequibilidad",
          "Ingreso indice consumo", "Ingreso indice RNB", "Selector ingreso", "Ingreso indice PIB", "Renta neta", "Elasticidad empleo_"}
V = [v for v in V if v[0] not in REMOVE]
def _find(n):
    for i, v in enumerate(V):
        if v[0] == n: return i
    raise KeyError(n)
def upd(n, e=None, view="keep", c=None, u=None):
    i = _find(n); a = V[i]
    V[i] = (a[0], a[1] if e is None else e, a[2] if u is None else u, a[3] if c is None else c, a[4] if view == "keep" else view)
def add(n, e, u, c, view=None): V.append((n, e, u, c, view))
def rd(fn): return list(csv.DictReader(open(D + fn, encoding="utf-8")))

# ---------------- datos de financiacion y rentabilidad ----------------
fin = {int(r["anio"]): r for r in rd("financiacion_hipotecas_2003_2024.csv")}
rent = {int(r["anio"]): r for r in rd("rentabilidad_vivienda_alternativas_1996_2024.csv")}
tipo_hip = {y: (_m.policy[y] + _m.SPREAD) / 100.0 for y in YEARS}                 # antes de 2004: tipo oficial + 1,5 puntos
for y in range(2004, 2025): tipo_hip[y] = float(fin[y]["tipo_nuevas_hipotecas_pct"]) / 100.0
plazo = {y: float(fin[y]["plazo_meses"]) for y in range(2004, 2025)}
ltv = {y: float(fin[y]["prestamo_valor_pct"]) / 100.0 for y in range(2004, 2025)}
yield_alq = {y: float(rent[y]["rentabilidad_bruta_alquiler_pct"]) / 100.0 for y in range(1996, 2025)}
for y in range(1981, 1996): yield_alq[y] = yield_alq[1996]                       # antes de 1996: se mantiene el valor de 1996 (supuesto)
renta_alq = {y: yield_alq[y] * precio[y] / 12.0 for y in YEARS}                    # euros de 2010 por m2 y mes

gdpi = {y: gdp[y] / gdp[1981] for y in YEARS}
SUP = 80.0
# Ingreso de referencia: el que hace que el precio sobre renta de 2004 sea el observado (7,67 anos)
Y0 = precio[2004] * SUP / (12.0 * float(fin[2004]["precio_sobre_renta_bruta_hogar_anios"]) * gdpi[2004])
PYI0 = P0 * SUP / (12.0 * Y0)
tipo0, plazo0, ltv0 = tipo_hip[1981], plazo[2004], ltv[2004]
cuota0 = max(tipo0, 0.005) / (1 - (1 + max(tipo0, 0.005)) ** (-plazo0 / 12.0))

# ---------------- entradas ----------------
upd("Tipo nominal dato", lk(tipo_hip), c="Tipo hipotecario: oficial + 1,5 pts hasta 2003; observado en las hipotecas nuevas desde 2004 (Banco de España).")
upd("Ingreso indice dato", lk({y: gdpi[y] for y in YEARS}), c="PIB per capita real / 1981 (proxy de la renta).")
add("Plazo hipoteca dato", lk(plazo), "Month", "Plazo medio de las hipotecas nuevas (2004-2024). Antes de 2004 se mantiene el de 2004 (supuesto).", "05")
add("Plazo hipoteca", "Plazo hipoteca dato+IF THEN ELSE(Time>=Inicio politica, Politica plazo, 0)", "Month", "Plazo; la politica puede alargarlo.", "05")
add("Politica plazo", "0.0", "Month", "Meses que se suman al plazo de las hipotecas desde el inicio de la politica.")
add("Prestamo valor dato", lk(ltv), "Dmnl", "Prestamo sobre valor de las hipotecas nuevas (2004-2024). Antes se mantiene el de 2004 (supuesto).", "05")
add("Prestamo valor", "MIN(0.95, Prestamo valor dato+IF THEN ELSE(Time>=Inicio politica, Politica prestamo valor, 0))", "Dmnl", "Prestamo sobre valor; la politica (por ejemplo un aval publico) puede subirlo.", "05")
add("Politica prestamo valor", "0.0", "Dmnl", "Puntos (en tanto por uno) que se suman al prestamo/valor desde el inicio de la politica.")
add("Renta alquiler dato", lk(renta_alq), "Euro/Metro2/Month", "Alquiler bruto = rentabilidad por alquiler observada (Banco de España, desde 1996) x precio real. Antes de 1996, la de 1996 (supuesto).", "05")
upd("Ingreso ref", f(Y0, 6), c="Ingreso por hogar de 1981 que da el precio/renta de 2004 observado (7,67 anos).")
# ---------------- capacidad de compra hipotecaria ----------------
add("Cuota anual por euro", "MAX(0.005, Tipo nominal)/(1-(1+MAX(0.005, Tipo nominal))^(-Plazo hipoteca/12))", "1/Year", "Cuota anual por euro prestado (intereses + amortizacion).", "06")
add("Capacidad por pago", "Esfuerzo maximo/(Cuota anual por euro*Prestamo valor)", "Year", "Anos de renta que un hogar puede pagar si dedica a la cuota su esfuerzo maximo.", "06")
add("Capacidad por ahorro", "Ahorro anios/(1-Prestamo valor)", "Year", "Anos de renta que puede pagar con su entrada (ahorro en anos de renta / parte no financiada).", "06")
add("Capacidad hipotecaria", "MIN(Capacidad por pago, Capacidad por ahorro)", "Year", "Anos de renta que puede pagar un hogar: manda la restriccion mas estricta.", "06")
add("Acceso", "Capacidad hipotecaria/Precio sobre ingreso", "Dmnl", "Capacidad de compra / precio, ambos en anos de renta. 1 = el precio justo cabe.", "06")
add("Acceso ref", "MIN(Esfuerzo maximo/(Cuota ref*Prestamo valor ref), Ahorro anios/(1-Prestamo valor ref))/Precio sobre ingreso ref", "Dmnl", "Acceso de 1981.", "06")
add("Factor acceso", "(Acceso/Acceso ref)^Elasticidad acceso", "Dmnl", "La demanda de los hogares sube o baja con el acceso, relativo a 1981.", "06")
add("Precio fundamental", "Capacidad hipotecaria*12*Ingreso/Superficie tipo", "Euro/Metro2", "Precio que cabe en la capacidad de compra de un hogar medio.", "06")
add("Brecha financiera", "Precio efectivo/(Relacion precio capacidad*Precio fundamental)-1", "Dmnl", "Precio frente a lo que financia el sistema.", "06")
add("Esfuerzo maximo", "0.35", "Dmnl", "A CALIBRAR: parte de la renta que un hogar dedica como maximo a la cuota.")
add("Ahorro anios", "1.5", "Year", "A CALIBRAR: ahorro disponible para la entrada, en anos de renta.")
add("Elasticidad acceso", "2.0", "Dmnl", "A CALIBRAR.")
add("Relacion precio capacidad", "0.8", "Dmnl", "A CALIBRAR: a que fraccion de la capacidad tiende el precio.")
add("Velocidad financiera", "0.02", "1/Month", "A CALIBRAR: rapidez con que el precio se acerca a lo que financia el sistema.")
add("Cuota ref", f(cuota0, 8), "1/Year", "Cuota por euro de 1981.")
add("Prestamo valor ref", f(ltv0, 8), "Dmnl", "Prestamo sobre valor de referencia (2004).")
add("Precio sobre ingreso ref", f(PYI0, 8), "Year", "Precio sobre renta de 1981 en el modelo.")
upd("Cambio bruto precio", "Velocidad precio*Precio*MIN(Presion-1, Techo desequilibrio)-Velocidad financiera*Precio*Brecha financiera")
upd("Demanda hogares", "Demanda base hogares*(Hogares/Hogares ref)^Elasticidad hogares*Factor acceso*Factor empleo*Factor expectativa hogares")
# ---------------- deuda hipotecaria (stock y flujos) ----------------
DEUDA0 = 0.30 * Y0 * 12.0 * H0
add("Deuda hipotecaria", f"INTEG(Nuevos prestamos-Amortizacion, {f(DEUDA0, 1)})", "Euro", "Deuda hipotecaria de los hogares (euros de 2010). Inicio: 30 % de la renta anual total (supuesto, solo importa la forma).", "06")
add("Nuevos prestamos", "Fraccion hipotecada*(Compra hogares+Compra inversora)*Precio efectivo*Superficie tipo*Prestamo valor", "Euro/Month", "Compras financiadas x precio x superficie x prestamo/valor.", "06")
add("Fraccion hipotecada", "0.6", "Dmnl", "A CALIBRAR: parte de las compras que se financian con hipoteca.")
add("Amortizacion", "Deuda hipotecaria/(Plazo hipoteca*Fraccion vida media)", "Euro/Month", "Devolucion: el stock entre la vida media restante de los prestamos.", "06")
add("Fraccion vida media", "0.5", "Dmnl", "A CALIBRAR: vida media restante de los prestamos como fraccion del plazo.")
add("Deuda sobre renta", "Deuda hipotecaria/(Ingreso*Hogares*12)", "Dmnl", "Deuda / renta anual total de los hogares.", "04")
add("Deuda indice", f"Deuda sobre renta/{f(0.30, 6)}", "Dmnl", "Relativa al inicio. Se compara con el credito a hogares/PIB del BIS.", "04")
add("Desviacion deuda", "Deuda indice/Credito indice-1", "Dmnl", "Frente al credito a hogares sobre PIB (BIS) relativo a 1981.", "04")
# ---------------- rentabilidad del alquiler observada ----------------
add("Ingreso indice 2024", f(gdpi[2024], 8), "Dmnl", "Indice de renta de 2024.")
add("Renta alquiler efectiva", "Renta alquiler dato*IF THEN ELSE(Time>522, Ingreso indice/Ingreso indice 2024, 1)", "Euro/Metro2/Month", "Alquiler observado hasta 2024; despues crece con la renta.", "02")
upd("Rentabilidad inversora", "12*Renta alquiler efectiva/Precio efectivo+Expectativa usada-Tipo capital-Coste mantenimiento-Riesgo regulacion efectivo")
i0 = _m.tipo_real[1981]
upd("Rentabilidad ref", f(yield_alq[1981] - i0 - 0.01, 8), c="Rentabilidad de 1981 (base de la demanda inversora).")
upd("Alquiler sobre ingreso", "Renta alquiler efectiva*Superficie tipo/Ingreso")

import re as _re
names = [v[0] for v in V]; eq = {v[0]: v[1] for v in V}
WORDS = sorted(names, key=len, reverse=True)
def refs(expr):
    found, s = [], expr
    for w in WORDS:
        if w in s: found.append(w); s = s.replace(w, " ")
    return found

if __name__ == "__main__":
    import engine
    m = engine.Model([v[:4] for v in V])
    W = ["Precio", "Parque fisico", "Obra terminada", "Deuda indice", "Credito indice", "Acceso", "Capacidad hipotecaria", "Precio fundamental", "Factor acceso", "Hogares sin alojar", "Precio sobre ingreso", "Error balance parque", "Cuota anual por euro", "Demanda hogares", "Demanda inversora", "Compra hogares"]
    f_ = m.make(W, 528, 0.25)
    o = f_()
    print("Y0=%.1f €/mes  PYI0=%.2f  cuota0=%.3f  Racc0: K0=%.2f" % (Y0, PYI0, cuota0, min(0.35 / (cuota0 * ltv0), 1.5 / (1 - ltv0))))
    print("Con los valores iniciales (sin ajustar):")
    for y in (1981, 1985, 1990, 1995, 2000, 2004, 2007, 2010, 2013, 2020, 2024):
        t = 12 * (y - 1981) + 6
        print("  %d precio %6.0f (dato %6.0f) | capacidad %5.2f anos | PYI %5.2f | acceso %5.2f | deuda idx %5.2f (BIS %5.2f) | obra %7.0f/ano" % (
            y, o["Precio"][t], precio[y], o["Capacidad hipotecaria"][t], o["Precio sobre ingreso"][t], o["Acceso"][t], o["Deuda indice"][t], o["Credito indice"][t], 12 * o["Obra terminada"][t]))
    print("error balance max %.1e" % max(abs(x) for x in o["Error balance parque"]))
