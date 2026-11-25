"""Modelo de vivienda V2: Espana 1981-2024, en euros constantes de 2010. t = meses desde enero de 1981."""
import csv, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
D = os.environ.get("VIV_DATOS", "../archivos/datos/")
def rd(f): return list(csv.DictReader(open(D + f, encoding="utf-8")))
T = lambda y: 12 * (y - 1981) + 6          # mediados de cada ano
YEARS = list(range(1981, 2025))
HORIZON = 528

# ---------------- datos ----------------
ph = {int(r["anio"]): r for r in rd("parque_hogares_1981_2024.csv")}
epa = {y: float(r["hogares_epa"]) for y, r in ph.items() if r["hogares_epa"]}
parque = {}
for y, r in ph.items():
    if y <= 2000 and r["total_bde"]: parque[y] = float(r["total_bde"])
    elif y >= 2001 and r["total_mivau"]: parque[y] = float(r["total_mivau"])
gdp = {int(r["anio"]): float(r["pib_per_capita_usd_const_2015"]) for r in rd("WB_Espana_PIB_per_capita_USD2015_1975_2025.csv")}
infl = {int(r["anio"]): float(r["inflacion_ipc_pct"]) for r in rd("WB_Espana_inflacion_IPC_pct_1975_2025.csv")}
def monthly_mean(fname_list):
    acc = {}
    for fn in fname_list:
        for r in rd(fn):
            y = int(r["periodo"][:4]); acc.setdefault(y, []).append(float(r["valor"]))
    return {y: sum(v) / len(v) for y, v in acc.items()}
policy = monthly_mean(["BIS_tipo_oficial_Espana_1945_1998.csv", "BIS_tipo_oficial_zona_euro_1999_.csv"])
cred = {int(r["periodo"][:4]): float(r["valor"]) for r in rd("BIS_credito_hogares_pct_PIB_Espana_1980_.csv") if r["periodo"].endswith("Q4")}
real_q = rd("BIS_precio_vivienda_Espana_real_1971_.csv")
price_y = {}
for r in real_q:
    price_y.setdefault(int(r["trimestre"][:4]), []).append(float(r["indice"]))
ANCLA = 19.31       # euros de 2010 por m2 por punto del indice (ver FUENTES.md)
precio = {y: ANCLA * sum(v) / len(v) for y, v in price_y.items()}
SPREAD = 1.5        # diferencial hipotecario sobre el tipo oficial (puntos), supuesto
tipo_real = {y: (policy[y] + SPREAD - infl[y]) / 100.0 for y in YEARS}
def lk(d, ys=YEARS):
    pts = ",".join(f"({T(y)},{round(d[y], 6)!r})" for y in ys if y in d)
    lo, hi = min(d[y] for y in ys if y in d), max(d[y] for y in ys if y in d)
    return f"WITH LOOKUP(Time, ([(0,{math.floor(min(0,lo)*1.5)})-({HORIZON},{math.ceil(hi*1.5+1)})],{pts}))"
growth = {y: math.log(precio[min(y + 1, 2024)] / precio[max(y - 1, 1981)]) / (min(y + 1, 2024) - max(y - 1, 1981)) for y in YEARS}

# ---------------- estado inicial (1981) en cuasi-equilibrio ----------------
Ntot = parque[1981]                  # 14.860.272 (BdE)
H0 = epa[1981]                       # 10.153.000
P0 = precio[1981]
prop = 0.731 + 0.061                 # propiedad + cesion y otros (censo 1981)
O0, R0 = prop * H0, (1 - prop) * H0
S0 = 1898602.0                       # secundarias del censo 1981
C0 = (parque[1985] - parque[1981]) / 48.0     # aumento mensual 1981-85
Qs0, tau_s, tau_O, tau_C, tau_H, tau_D, tau_det, tau_R, falq, tau_sec = 45000.0, 6.0, 600.0, 24.0, 24.0, 600.0, 1200.0, 48.0, 0.8, 480.0
d0 = 1.0 / tau_det; a_ = 1.0 / tau_H + 1.0 / tau_D
Det0 = d0 * Ntot / (a_ + d0)
Vs0 = Qs0 * tau_s
Vi0 = Ntot - (O0 + R0 + S0 + Vs0 + Det0)
Dem0 = Det0 / tau_D; Rehab0 = Det0 / tau_H
Eh0 = O0 / tau_O
Ei0 = Qs0 - d0 * (O0 + R0 + Vi0) - C0 + Dem0 - Eh0
assert Ei0 > 0 and Vi0 > 0, (Ei0, Vi0)
tau_Ei = Vi0 / Ei0
Li0 = R0 / tau_R + d0 * R0
tau_L = falq * Vi0 / Li0
Ai0 = d0 * R0 + Ei0 + d0 * Vi0
Bh0 = Qs0 - Ai0
f_sec = (d0 + 1.0 / tau_sec) * S0 / C0
U0 = C0 * tau_C
def f(x, n=6): return repr(round(float(x), n))

V = []
def add(n, e, u, c, view=None): V.append((n, e, u, c, view))

# ---------- 01 Parque ----------
add("Viviendas venta", f"INTEG(Obra a venta+Reventa propietarios+Venta inversor+Rehabilitacion+Secundarias a venta-Compra hogares-Compra inversora-Deterioro venta, {f(Vs0,1)})", "Vivienda", "Vs: vacias en venta.", "01")
add("Uso propio", f"INTEG(Compra hogares-Reventa propietarios-Deterioro uso propio, {f(O0,1)})", "Vivienda", "O: principales en propiedad o cedidas (73,1 % + 6,1 % del censo de 1981).", "01")
add("Vacias inversor", f"INTEG(Compra inversora+Fin de contrato-Puesta en alquiler-Venta inversor-Deterioro vacias inversor, {f(Vi0,1)})", "Vivienda", "Vi: vacias retenidas fuera del mercado (desocupadas del censo).", "01")
add("Alquiladas", f"INTEG(Puesta en alquiler-Fin de contrato-Deterioro alquiladas, {f(R0,1)})", "Vivienda", "R: principales en alquiler (20,8 % del censo de 1981).", "01")
add("Secundarias", f"INTEG(Obra a secundarias-Secundarias a venta-Deterioro secundarias, {f(S0,1)})", "Vivienda", "Segundas residencias (censo 1981: 1.898.602).", "01")
add("Deterioradas", f"INTEG(Deterioro venta+Deterioro uso propio+Deterioro vacias inversor+Deterioro alquiladas+Deterioro secundarias-Rehabilitacion-Demolicion, {f(Det0,1)})", "Vivienda", "No habitables o pendientes de recuperar.", "01")
add("Parque retirado", "INTEG(Demolicion, 0)", "Vivienda", "Demolidas (acumulado).", "01")
add("En construccion", f"INTEG(Inicio obra-Obra a venta-Obra a secundarias, {f(U0,1)})", "Vivienda", "U: en obra.", "01")
add("Edad media", "INTEG(Envejecimiento-Rejuvenecimiento, 360)", "Month", "Antiguedad media del parque (30 anos en 1981, supuesto).", "01")
add("Obra terminada", "En construccion/tau obra", "Vivienda/Month", "C: viviendas terminadas.", "01")
add("Obra a venta", "(1-fraccion secundaria)*Obra terminada", "Vivienda/Month", "Terminadas que salen a la venta.", "01")
add("Obra a secundarias", "fraccion secundaria*Obra terminada", "Vivienda/Month", "Terminadas que son segunda residencia.", "01")
add("Reventa propietarios", "Uso propio/tau uso propio", "Vivienda/Month", "E_h.", "01")
add("Venta inversor", "Vacias inversor/tau vacia inversor", "Vivienda/Month", "E_i.", "01")
add("Puesta en alquiler", "fraccion alquiler*Vacias inversor/tau alquilar", "Vivienda/Month", "L_i.", "01")
add("Fin de contrato", "Alquiladas/tau contrato", "Vivienda/Month", "F_R.", "01")
add("Secundarias a venta", "Secundarias/tau secundaria", "Vivienda/Month", "Segundas residencias que se ponen a la venta.", "01")
add("Inicio obra", "Inicio base*MAX(0, 1+Sensibilidad margen*Margen obra/Margen ref)", "Vivienda/Month", "I_nuevo segun el margen.", "01")
add("Compra hogares", "Reparto*Demanda hogares", "Vivienda/Month", "B_h.", "01")
add("Compra inversora", "Reparto*Demanda inversora", "Vivienda/Month", "A_i.", "01")
add("Tasa deterioro", "(1/tau deterioro)*(Edad media/Edad ref)^Exponente edad", "1/Month", "Deterioro por mes; crece con la edad.", "01")
add("Deterioro venta", "Tasa deterioro*Viviendas venta", "Vivienda/Month", "", "01")
add("Deterioro uso propio", "Tasa deterioro*Uso propio", "Vivienda/Month", "", "01")
add("Deterioro vacias inversor", "Tasa deterioro*Vacias inversor", "Vivienda/Month", "", "01")
add("Deterioro alquiladas", "Tasa deterioro*Alquiladas", "Vivienda/Month", "", "01")
add("Deterioro secundarias", "Tasa deterioro*Secundarias", "Vivienda/Month", "", "01")
add("Rehabilitacion", "MIN(Deterioradas/tau rehabilitacion, Capacidad rehabilitacion)", "Vivienda/Month", "H: vuelve a venta.", "01")
add("Demolicion", "Deterioradas/tau demolicion", "Vivienda/Month", "Da.", "01")
add("Envejecimiento", "1", "Month/Month", "", "01")
add("Rejuvenecimiento", "Edad media*Obra terminada/Parque fisico", "Month/Month", "", "01")
# ---------- 02 Precio ----------
add("Precio", "INTEG(Cambio precio, Precio ref)", "Euro/Metro2", "P endogeno (euros de 2010).", "02")
add("Expectativa ge", "INTEG(Cambio expectativa, 0)", "1/Year", "g_e.", "02")
add("Precio efectivo", "IF THEN ELSE(Interruptor precio forzado=1, Precio dato, Precio)", "Euro/Metro2", "Precio usado por el resto: el dato si esta forzado.", "02")
add("Oferta venta", "Viviendas venta/tau venta", "Vivienda/Month", "Q_s.", "02")
add("Reparto", "MIN(1, Oferta venta/(Demanda hogares+Demanda inversora+Eps demanda))", "Dmnl", "lambda.", "02")
add("Factor credito", "Credito indice^Elasticidad credito", "Dmnl", "F_credito: crece con el credito a hogares.", "02")
add("Demanda hogares", "Demanda base hogares*(Hogares/Hogares ref)^Elasticidad hogares*((Ingreso/Precio efectivo)/(Ingreso ref/Precio ref))^Elasticidad asequibilidad*Factor credito", "Vivienda/Month", "D_h*.", "02")
add("Expectativa usada", "IF THEN ELSE(Interruptor expectativa=1, Expectativa ge, Expectativa externa)", "1/Year", "", "02")
add("Rentabilidad inversora", "12*Renta neta/Precio efectivo+Expectativa usada-Tipo capital-Coste mantenimiento-Riesgo regulacion", "1/Year", "r_i.", "02")
add("Demanda inversora", "Multiplicador inversor*Demanda base inversora*MAX(0, 1+Sensibilidad inversora*(Rentabilidad inversora-Rentabilidad ref))", "Vivienda/Month", "D_i*.", "02")
add("Presion", "(Demanda hogares+Demanda inversora)/(Oferta venta+Eps oferta)", "Dmnl", "", "02")
add("Cambio bruto precio", "Velocidad precio*Precio*MIN(Presion-1, Techo desequilibrio)", "Euro/Metro2/Month", "", "02")
add("Cambio precio", "IF THEN ELSE(Precio>Precio minimo, Cambio bruto precio, MAX(0, Cambio bruto precio))", "Euro/Metro2/Month", "", "02")
add("Cambio precio efectivo", "IF THEN ELSE(Interruptor precio forzado=1, Crecimiento precio dato*Precio dato/12, Cambio precio)", "Euro/Metro2/Month", "Variacion del precio usada para las expectativas.", "02")
add("Cambio expectativa", "(12*Cambio precio efectivo/Precio efectivo-Expectativa ge)/tau expectativa", "1/Year/Month", "", "02")
add("Precio minimo", "0.3*Precio ref", "Euro/Metro2", "", "02")
add("Coste suelo", "Fraccion suelo*Precio efectivo", "Euro/Metro2", "El suelo cuesta una fraccion del precio.", "02")
add("Coste obra", "Coste suelo+Coste materiales+Coste mano obra+Coste energia transporte+Coste calidad+Coste otros", "Euro/Metro2", "", "02")
add("Margen obra", "Precio efectivo-Coste obra-Margen minimo", "Euro/Metro2", "", "02")
# ---------- 03 Hogares ----------
add("Hogares", f"INTEG(Formacion hogares-Disolucion hogares, {f(H0,1)})", "Hogar", "H.", "03")
add("Hogares objetivo", "Hogares dato", "Hogar", "H* = hogares de la EPA.", "03")
add("Formacion hogares", "MAX(0, (Hogares objetivo-Hogares)/tau formacion)", "Hogar/Month", "", "03")
add("Disolucion hogares", "MAX(0, (Hogares-Hogares objetivo)/tau disolucion)", "Hogar/Month", "", "03")
# ---------- 04 Indicadores ----------
add("Parque habitable", "Viviendas venta+Uso propio+Vacias inversor+Alquiladas+Secundarias", "Vivienda", "", "04")
add("Parque fisico", "Parque habitable+Deterioradas", "Vivienda", "N.", "04")
add("Obras acumuladas", "INTEG(Obra terminada, 0)", "Vivienda", "", "04")
add("Error balance parque", f"Parque fisico-({f(Ntot,1)}+Obras acumuladas-Parque retirado)", "Vivienda", "Debe valer 0.", "04")
add("Vacancia", "(Viviendas venta+Vacias inversor)/Parque habitable", "Dmnl", "", "04")
add("Indice precio", "100*Precio efectivo/Precio ref", "Dmnl", "", "04")
add("Precio sobre ingreso", "Precio efectivo*Superficie tipo/(12*Ingreso)", "Year", "", "04")
add("Alquiler sobre ingreso", "Renta neta*Superficie tipo/Ingreso", "Dmnl", "", "04")
add("Disponibles por mil hogares", "1000*Viviendas venta/Hogares", "Vivienda/Hogar", "", "04")
add("Hogares sin alojar", "Hogares-(Uso propio+Alquiladas)", "Hogar", "", "04")
add("Desviacion parque", "(Parque fisico-Parque dato)/Parque dato", "Dmnl", "Frente a la estimacion oficial.", "04")
add("Desviacion precio", "(Precio efectivo-Precio dato)/Precio dato", "Dmnl", "Frente al indice real del BIS anclado.", "04")
# ---------- 05 Entradas externas (datos) ----------
add("Hogares dato", lk(epa), "Hogar", "Hogares de la EPA (INE); 1982-84 interpolados.", "05")
add("Ingreso indice", lk({y: gdp[y] / gdp[1981] for y in YEARS}), "Dmnl", "PIB per capita real / el de 1981 (proxy de la renta).", "05")
add("Tipo capital", lk(tipo_real), "1/Year", "Tipo oficial + 1,5 puntos - inflacion (real).", "05")
add("Credito indice", lk({y: cred[y] / cred[1981] for y in YEARS}), "Dmnl", "Credito a hogares / PIB, base 1981.", "05")
add("Precio dato", lk({y: precio[y] for y in YEARS}), "Euro/Metro2", "Indice real BIS x 19,31 (euros de 2010).", "05")
add("Crecimiento precio dato", lk(growth), "1/Year", "Variacion anual del precio dato (continua).", "05")
add("Parque dato", lk(parque, sorted(parque)), "Vivienda", "Parque total oficial (BdE hasta 2000, MIVAU desde 2001).", "05")
add("Ingreso", "Ingreso ref*Ingreso indice", "Euro/Month", "Ingreso real por hogar (euros de 2010).", "05")
# ---------- parametros ----------
Rnet0 = 0.04 * P0 / 12.0
i0 = tipo_real[1981]
r_ref = 12 * Rnet0 / P0 + 0.0 - i0 - 0.005 - 0.005
C = [
 ("tau uso propio", tau_O, "Month", "Permanencia media del propietario. A CALIBRAR."),
 ("tau vacia inversor", tau_Ei, "Month", "Se calcula para el equilibrio de 1981."),
 ("tau alquilar", tau_L, "Month", "Se calcula para el equilibrio de 1981."),
 ("fraccion alquiler", falq, "Dmnl", ""),
 ("tau contrato", tau_R, "Month", ""),
 ("tau venta", tau_s, "Month", ""),
 ("tau obra", tau_C, "Month", "A CALIBRAR."),
 ("tau secundaria", tau_sec, "Month", "Salida de segundas residencias a venta."),
 ("fraccion secundaria", f_sec, "Dmnl", "Parte de la obra que son segundas residencias; se calcula para 1981."),
 ("tau deterioro", tau_det, "Month", "A CALIBRAR."),
 ("Edad ref", 360, "Month", ""),
 ("Exponente edad", 0.5, "Dmnl", "A CALIBRAR."),
 ("tau rehabilitacion", tau_H, "Month", ""),
 ("Capacidad rehabilitacion", 40000.0, "Vivienda/Month", "A CALIBRAR."),
 ("tau demolicion", tau_D, "Month", "A CALIBRAR."),
 ("Demanda base hogares", Bh0, "Vivienda/Month", "Se calcula para el equilibrio de 1981."),
 ("Demanda base inversora", Ai0, "Vivienda/Month", "Se calcula para el equilibrio de 1981."),
 ("Elasticidad asequibilidad", 1.0, "Dmnl", "A CALIBRAR."),
 ("Elasticidad hogares", 1.0, "Dmnl", "A CALIBRAR."),
 ("Elasticidad credito", 0.3, "Dmnl", "A CALIBRAR."),
 ("Velocidad precio", 0.05, "1/Month", "A CALIBRAR."),
 ("Techo desequilibrio", 1.0, "Dmnl", ""),
 ("Eps oferta", 1.0, "Vivienda/Month", ""),
 ("Eps demanda", 1.0, "Vivienda/Month", ""),
 ("Renta neta", Rnet0, "Euro/Metro2/Month", "4 % neto sobre el precio de 1981."),
 ("Coste mantenimiento", 0.005, "1/Year", ""),
 ("Riesgo regulacion", 0.005, "1/Year", ""),
 ("Rentabilidad ref", r_ref, "1/Year", "Rentabilidad de 1981 (base de la demanda inversora)."),
 ("Sensibilidad inversora", 20.0, "Year", "A CALIBRAR."),
 ("Fraccion suelo", 0.35, "Dmnl", "A CALIBRAR."),
 ("Coste materiales", 0.28 * P0, "Euro/Metro2", ""),
 ("Coste mano obra", 0.22 * P0, "Euro/Metro2", ""),
 ("Coste energia transporte", 0.02 * P0, "Euro/Metro2", ""),
 ("Coste calidad", 0.03 * P0, "Euro/Metro2", ""),
 ("Coste otros", 0.05 * P0, "Euro/Metro2", ""),
 ("Margen minimo", 0.05 * P0, "Euro/Metro2", ""),
 ("Inicio base", C0, "Vivienda/Month", "Obra de 1981 (aumento del parque 1981-85)."),
 ("Sensibilidad margen", 2.0, "Dmnl", "A CALIBRAR."),
 ("Margen ref", 0.5 * P0, "Euro/Metro2", ""),
 ("Hogares ref", H0, "Hogar", "H0 de 1981 (EPA)."),
 ("Ingreso ref", 1250.0, "Euro/Month", "Ingreso por hogar en 1981, euros de 2010 (supuesto)."),
 ("Precio ref", P0, "Euro/Metro2", "Precio de 1981 (BIS real x 19,31)."),
 ("tau expectativa", 24.0, "Month", "A CALIBRAR."),
 ("Expectativa externa", 0.0, "1/Year", ""),
 ("Interruptor expectativa", 1.0, "Dmnl", "1 = expectativa endogena."),
 ("Interruptor precio forzado", 0.0, "Dmnl", "1 = usar el precio real como dato (para ajustar la oferta)."),
 ("Multiplicador inversor", 1.0, "Dmnl", ""),
 ("tau formacion", 24.0, "Month", ""),
 ("tau disolucion", 24.0, "Month", ""),
 ("Superficie tipo", 80.0, "Metro2", ""),
]
for n, v, u, c in C:
    add(n, f(v, 8) if isinstance(v, float) else str(v), u, c, None)

TARGET_PARQUE = parque
TARGET_PRECIO = {y: precio[y] for y in YEARS}

if __name__ == "__main__":
    print("P0=%.0f  Det0=%.0f Vs0=%.0f Vi0=%.0f  C0=%.0f/mes  Ei=%.0f  tau_Ei=%.0f tau_L=%.1f  f_sec=%.3f  Bh0=%.0f Ai0=%.0f" % (P0, Det0, Vs0, Vi0, C0, Ei0, tau_Ei, tau_L, f_sec, Bh0, Ai0))
    print("suma stocks inicial:", O0 + R0 + S0 + Vs0 + Vi0 + Det0, " objetivo", Ntot)

# ---- utilidades para el dibujo ----
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
