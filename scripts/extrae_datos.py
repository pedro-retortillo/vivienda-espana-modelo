import re, sys, csv, io, urllib.request
import pypdf
sys.stdout.reconfigure(encoding="utf-8")
D = sys.argv[1]
r = pypdf.PdfReader(D + "/MIVAU_Observatorio_boletin_anual_2024.pdf")

def big(s):  # numero entero con o sin puntos de millar
    return int(s.replace(".", ""))
BIGRE = re.compile(r"(?<![\d,.])(\d{1,2}(?:\.\d{3}){2}|\d{7,8})(?![\d,])")

# ---- Tabla 8.1 (pag. 101) parque y hogares ----
t = r.pages[100].extract_text()
rows = {}
for line in t.split("\n"):
    m = re.match(r"^\s*(19[89]\d|20[0-2]\d)\s+(.*)$", line)
    if not m: continue
    y = int(m.group(1)); rest = m.group(2)
    if "s.d" in rest:
        nums = [big(x) for x in BIGRE.findall(rest)]
        rows[y] = dict(hogares_epa=nums[-1]) if nums else {}
        continue
    nums = [big(x) for x in BIGRE.findall(rest)]
    d = {}
    if y in (1981, 1991): keys = ["total_bde", "total_censo", "vp_censo", "hogares_epa"]
    elif 1985 <= y <= 2000: keys = ["total_bde", "hogares_epa"]
    elif y in (2001, 2011): keys = ["total_mivau", "total_bde", "total_censo", "vp_mivau", "vp_censo", "hogares_epa"]
    elif y == 2021: keys = ["total_mivau", "total_censo", "vp_mivau", "vp_censo", "hogares_epa"]
    elif y in (2022, 2023): keys = ["total_mivau", "vp_mivau", "hogares_epa"]
    else: keys = ["total_mivau", "total_bde", "vp_mivau", "hogares_epa"]
    assert len(nums) == len(keys), (y, rest, nums, keys)
    rows[y] = dict(zip(keys, nums))
cols = ["total_mivau", "total_bde", "total_censo", "vp_mivau", "vp_censo", "hogares_epa"]
with open(D + "/parque_hogares_1981_2024.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f); w.writerow(["anio"] + cols)
    for y in sorted(rows): w.writerow([y] + [rows[y].get(c, "") for c in cols])
print("parque_hogares: filas", len(rows), "1981..", max(rows))

# ---- Tabla 8.2 (pag. 103) familiar / principal / no principal 2003-2023 ----
t = r.pages[102].extract_text(); out = []
for line in t.split("\n"):
    m = re.match(r"^\s*(20[0-2]\d)\s+(\d{2}\.\d{3}\.\d{3})\s+(\d{2}\.\d{3}\.\d{3})\s+(\d\.\d{3}\.\d{3})", line)
    if m: out.append([int(m.group(1))] + [big(m.group(i)) for i in (2, 3, 4)])
with open(D + "/parque_mivau_principal_noprincipal_2003_2023.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f); w.writerow(["anio", "vivienda_familiar", "vivienda_principal", "vivienda_no_principal"]); w.writerows(out)
print("parque 8.2: filas", len(out))

# ---- Tabla 1.2 (pag. 7) iniciadas y terminadas 2003-2024 ----
t = r.pages[6].extract_text(); out = []
for line in t.split("\n"):
    m = re.match(r"^\s*(20[0-2]\d)\s+((?:\d[\d.]*\s+){6})", line)
    if m:
        n = [big(x) for x in m.group(2).split()]
        out.append([int(m.group(1))] + n)
with open(D + "/viviendas_iniciadas_terminadas_2003_2024.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f); w.writerow(["anio", "VL_iniciadas", "VL_terminadas", "VP_calif_prov", "VP_calif_def", "total_iniciadas", "total_terminadas"]); w.writerows(out)
print("terminadas: filas", len(out))

# ---- Tabla 2.1 (pag. 16) precio VL y VP 2005-2024 y 2.2 (pag. 17) 2003-2004 ----
out = {}
for line in r.pages[15].extract_text().split("\n"):
    m = re.match(r"^\s*(20[0-2]\d)\s+(\d\.\d{3},\d)\s+([\d.]+,\d)", line)
    if m: out[int(m.group(1))] = [float(m.group(2).replace(".", "").replace(",", ".")), float(m.group(3).replace(".", "").replace(",", "."))]
for line in r.pages[16].extract_text().split("\n"):
    m = re.match(r"^\s*(200[34])\s+(\d\.\d{3},\d)", line)
    if m and int(m.group(1)) not in out: out[int(m.group(1))] = [float(m.group(2).replace(".", "").replace(",", ".")), ""]
with open(D + "/precio_valor_tasado_eur_m2_2003_2024.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f); w.writerow(["anio", "vivienda_libre_eur_m2", "vivienda_protegida_eur_m2"])
    for y in sorted(out): w.writerow([y] + out[y])
print("precio: filas", len(out))

# ---- Tabla 5.4 (pag. 58) tenencia censos ----
ten = [[1970, 63.4, 30.1, 6.5], [1981, 73.1, 20.8, 6.1], [1991, 78.3, 15.2, 6.5], [2001, 82.1, 11.4, 6.5], [2011, 78.9, 13.5, 7.6], [2021, 75.4, 16.1, 8.4]]
txt = r.pages[57].extract_text()
for y, a, b, c in ten:   # comprobar contra el texto
    assert re.search(rf"{y}\s+{str(a).replace('.', ',')}\s+{str(b).replace('.', ',')}\s+{str(c).replace('.', ',')}", txt), y
with open(D + "/tenencia_viviendas_principales_censos.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f); w.writerow(["censo", "propiedad_pct", "alquiler_pct", "cesion_otros_pct"]); w.writerows(ten)
print("tenencia ok")

# ---- BIS: indice de precios de la vivienda (nominal y real) ----
for tag, code in (("nominal", "N"), ("real", "R")):
    u = f"https://stats.bis.org/api/v1/data/WS_SPP/Q.ES.{code}.628?format=csv"
    raw = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8")
    rd = list(csv.DictReader(io.StringIO(raw)))
    with open(D + f"/BIS_precio_vivienda_Espana_{tag}_1971_.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["trimestre", "indice"])
        for x in rd: w.writerow([x["TIME_PERIOD"], x["OBS_VALUE"]])
    v10 = [float(x["OBS_VALUE"]) for x in rd if x["TIME_PERIOD"].startswith("2010")]
    print("BIS", tag, "obs", len(rd), rd[0]["TIME_PERIOD"], "->", rd[-1]["TIME_PERIOD"], "media 2010 = %.1f" % (sum(v10) / len(v10)))
