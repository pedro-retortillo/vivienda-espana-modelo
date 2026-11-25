import re, sys, csv
import pypdf
sys.stdout.reconfigure(encoding="utf-8")
D = "../archivos/datos/"
r = pypdf.PdfReader(D + "MIVAU_Observatorio_boletin_anual_2024.pdf")
num = lambda s: float(s.replace(".", "").replace(",", ".")) if re.fullmatch(r"-?[\d.]+,\d+|-?[\d.]+", s) else None
def rows(page, first, last, ncols=None):
    out = {}
    for line in (r.pages[page - 1].extract_text() or "").split("\n"):
        m = re.match(r"^\s*((?:19|20)\d\d)\s+(.*)$", line)
        if not m: continue
        y = int(m.group(1))
        if not (first <= y <= last): continue
        toks = m.group(2).split()
        if not toks or re.fullmatch(r"(19|20)\d\d", toks[0]): continue
        if ncols and len(toks) < ncols: continue
        out[y] = toks
    return out
res = {}
# 6.10 prestamo/valor (p77)
t = rows(77, 2004, 2024, 2); res["ltv"] = {y: (num(v[0]), num(v[1])) for y, v in t.items()}
# 6.11 plazo y tipo (p78)
t = rows(78, 2004, 2024, 2); res["plazo"] = {y: (num(v[0]), num(v[1])) for y, v in t.items()}
# 6.14 precio/renta y esfuerzo (p81)
t = rows(81, 2003, 2024, 2); res["acc"] = {y: (num(v[0]), num(v[1])) for y, v in t.items()}
# 6.12 deuda/PIB y RBD (p79)
t = rows(79, 2004, 2024, 3); res["deuda"] = {y: (num(v[0]), num(v[1])) for y, v in t.items()}
# 6.1 hipotecas de vivienda constituidas (p62): 3er numero
t = rows(62, 2004, 2024, 3); res["hip"] = {y: num(v[2]) for y, v in t.items()}
# 7.6 rentabilidades (p91): vivienda, alquiler, bonos(-), depositos(n.d.), bolsa
t = rows(91, 1996, 2024, 5)
def f(s): return None if s in ("-", "n.d.") else num(s)
res["rent"] = {y: tuple(f(x) for x in v[:5]) for y, v in t.items()}
for k, d in res.items():
    ys = sorted(d)
    print("%-6s filas %2d  %d-%d" % (k, len(d), ys[0], ys[-1]))
    assert len(ys) == ys[-1] - ys[0] + 1, (k, "faltan anos")
with open(D + "financiacion_hipotecas_2003_2024.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["anio", "prestamo_valor_pct", "creditos_rpv_mayor80_pct", "plazo_meses", "tipo_nuevas_hipotecas_pct", "precio_sobre_renta_bruta_hogar_anios",
                "esfuerzo_teorico_pct", "endeudamiento_hogares_pct_pib", "renta_bruta_disponible_Meur", "hipotecas_vivienda_constituidas"])
    for y in range(2003, 2025):
        g = lambda d, i=None: ("" if y not in d else (d[y] if i is None else d[y][i]))
        w.writerow([y, g(res["ltv"], 0), g(res["ltv"], 1), g(res["plazo"], 0), g(res["plazo"], 1), g(res["acc"], 0), g(res["acc"], 1), g(res["deuda"], 0), g(res["deuda"], 1), g(res["hip"])])
with open(D + "rentabilidad_vivienda_alternativas_1996_2024.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["anio", "rentabilidad_anual_vivienda_pct", "rentabilidad_bruta_alquiler_pct", "bonos_estado_10a_pct", "depositos_hogares_pct", "ibex35_pct"])
    for y in sorted(res["rent"]): w.writerow([y] + ["" if v is None else v for v in res["rent"][y]])
print("1996 rent:", res["rent"][1996], "| 2004 ltv/plazo/tipo:", res["ltv"][2004], res["plazo"][2004], "| 2007 acc:", res["acc"][2007], "| 2024 rent:", res["rent"][2024])
