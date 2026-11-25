import sys, os, json, glob, csv
os.environ["VIV_MODEL"] = "vfin_model"
sys.path.insert(0, ".")
import vfin_model as M
D = M.D
def rd(fn): return list(csv.DictReader(open(D + fn, encoding="utf-8")))
P = json.load(open("params_final5.json"))
fin = {int(r["anio"]): r for r in rd("financiacion_hipotecas_2003_2024.csv")}
rent = {int(r["anio"]): r for r in rd("rentabilidad_vivienda_alternativas_1996_2024.csv")}
term = {int(r["anio"]): float(r["total_terminadas"]) for r in rd("viviendas_iniciadas_terminadas_2003_2024.csv")}
cred = {}
for r in rd("BIS_credito_hogares_pct_PIB_Espana_1980_.csv"):
    if r["periodo"].endswith("Q4"): cred[int(r["periodo"][:4])] = float(r["valor"])
data = {
 "precio": {y: round(M.precio[y], 1) for y in range(1981, 2025)},
 "parque": {y: v for y, v in M.parque.items() if y <= 2023},
 "epa": {y: v for y, v in M.epa.items()},
 "term": term,
 "tipo": {y: round(M.tipo_hip[y] * 100, 2) for y in range(1981, 2025)},
 "ltv": {y: round(M.ltv[y] * 100, 1) for y in range(2004, 2025)},
 "credito": {y: cred[y] for y in range(1981, 2025) if y in cred},
 "pyi": {y: float(fin[y]["precio_sobre_renta_bruta_hogar_anios"]) for y in range(2003, 2025)},
 "yld": {y: float(rent[y]["rentabilidad_bruta_alquiler_pct"]) for y in range(1996, 2025)},
}
prof = {}
for f in glob.glob("profvp_*.json"):
    d = json.load(open(f)); prof["%g_%g" % (d["vf"], d["vp"])] = round(d["metrics"]["1981-2024"][0], 1)
SP = {"Sensibilidad margen": (0.05, 6.0), "Fraccion suelo": (0.1, 0.7), "tau obra": (6.0, 48.0), "Exponente inventario": (0.0, 6.0), "Elasticidad credito obra": (0.0, 1.5),
 "Esfuerzo maximo": (0.15, 0.9), "Ahorro anios": (0.2, 5.0), "Elasticidad acceso": (0.2, 8.0), "Relacion precio capacidad": (0.3, 2.0), "Velocidad financiera": (0.0, 0.2),
 "Fraccion hipotecada": (0.2, 1.0), "Fraccion vida media": (0.2, 1.0), "Velocidad precio": (0.005, 0.3), "Elasticidad hogares": (0.1, 2.0), "Techo desequilibrio": (0.3, 3.0),
 "tau expectativa": (3.0, 60.0), "Elasticidad expectativa hogares": (0.0, 15.0), "Elasticidad empleo": (0.0, 25.0), "Sensibilidad inversora": (0.0, 80.0)}
META = [
 ("Financiación", "Esfuerzo maximo", "Esfuerzo máximo", "fracción de la renta", "Parte de la renta que un hogar dedica como máximo a la cuota. Casi nunca limita desde los años 90: no está bien identificado."),
 ("Financiación", "Ahorro anios", "Ahorro para la entrada", "años de renta", "Ahorro que un hogar medio aporta como entrada."),
 ("Financiación", "Elasticidad acceso", "Elasticidad de la demanda al acceso", "—", "Cuánto cambia la demanda de los hogares cuando cambia su capacidad de compra respecto al precio."),
 ("Financiación", "Relacion precio capacidad", "Relación precio / capacidad", "—", "A qué fracción de la capacidad de compra tiende el precio."),
 ("Financiación", "Velocidad financiera", "Velocidad hacia lo que financia el sistema", "1/mes", "Rapidez con que el precio se acerca a su valor financiable."),
 ("Financiación", "Fraccion hipotecada", "Parte de las compras con hipoteca", "fracción", "Para el stock de deuda. Compensa con la vida media de los préstamos."),
 ("Financiación", "Fraccion vida media", "Vida media restante de los préstamos", "fracción del plazo", "Para el stock de deuda."),
 ("Oferta", "Sensibilidad margen", "Respuesta de la obra al margen", "—", "Cuánto aumentan los inicios de obra cuando el margen sube."),
 ("Oferta", "Fraccion suelo", "Coste del suelo sobre el precio", "fracción", "El suelo cuesta una fracción del precio de la vivienda."),
 ("Oferta", "tau obra", "Plazo de obra", "meses", "Tiempo medio hasta terminar una vivienda."),
 ("Oferta", "Exponente inventario", "Freno por vivienda sin vender", "—", "Cuánto se frena la obra si hay más vivienda en venta por hogar que en 1981."),
 ("Oferta", "Elasticidad credito obra", "Efecto del crédito sobre la obra", "—", "Ajustado a cero: los datos no lo necesitan."),
 ("Precio y demanda", "Velocidad precio", "Respuesta del precio a la presión", "1/mes", "Cuánto sube el precio cuando la demanda supera la oferta. Es la clave de la tesis: ver el mapa de condiciones."),
 ("Precio y demanda", "Elasticidad hogares", "Elasticidad de la demanda al número de hogares", "—", "Escala de la demanda con los hogares."),
 ("Precio y demanda", "Techo desequilibrio", "Techo del desequilibrio", "—", "Límite a la velocidad de subida del precio."),
 ("Precio y demanda", "tau expectativa", "Memoria de las expectativas", "meses", "Retraso con que la expectativa sigue al precio."),
 ("Pieza estadística", "Elasticidad expectativa hogares", "Expectativas de los hogares", "—", "Pieza estadística: mejora el ajuste, pero no se deduce de una estadística concreta."),
 ("Pieza estadística", "Elasticidad empleo", "Efecto del paro sobre la demanda", "—", "Pieza estadística: el paro reduce la demanda de compra."),
 ("Canal inversor", "Sensibilidad inversora", "Respuesta de la inversión a la rentabilidad", "años", "Ajustada a cero: con datos agregados el canal no se distingue (ver «Lo que no sabemos»)."),
]
def fmt(v):
    s = "%.3g" % v
    return s.replace(".", ",")
ptab = []
for grp, key, lab, unit, note in META:
    lo, hi = SP[key]; v = P[key]
    lim = abs(v - lo) < 0.01 * (hi - lo) or abs(v - hi) < 0.01 * (hi - lo)
    ptab.append([lab, fmt(v), unit, note, lim])
ptab.append(["Deterioro, demolición, edad", "fijos", "—", "Deterioro con vida de 2.400 meses y demolición de 1.500: no hay datos que los identifiquen, se dejan casi apagados.", False])
dg = open("panel/diagramas.svgs", encoding="utf-8").read().split("\n<!--SEP-->\n")
src = open("panel/web.src.html", encoding="utf-8").read()
model = open("panel/model5.js", encoding="utf-8").read()
js = "const DATA=" + json.dumps(data) + ";\nconst PROFV=" + json.dumps(prof) + ";\nconst PTAB=" + json.dumps(ptab, ensure_ascii=False) + ";"
art = src.replace("/*MODEL*/", model).replace("/*DATA*/", js)
for i in range(4): art = art.replace("<!--DG%d-->" % (i + 1), dg[i])
ORIG = "El modelo para Vensim (versión V5, con seis vistas), los datos en CSV con su fuente y los scripts de ajuste están disponibles junto a esta página."
CLOUD = "El modelo para Vensim (versión V5, con seis vistas), los datos en CSV con su fuente y los scripts de ajuste forman parte del estudio, pero esta copia en línea no los incluye: se publicarán junto a la versión alojada de la página."
assert ORIG in art
open("panel/web_artifact.html", "w", encoding="utf-8").write(art.replace(ORIG, CLOUD))
import os as _os
_files = ["archivos/Vivienda_V5_Financiacion_2050.mdl|Modelo de Vensim (V5, con 6 vistas)", "archivos/Vivienda_V5_Financiacion_2050_solo_ecuaciones.mdl|Modelo de Vensim, solo ecuaciones",
          "archivos/params_ajustados_V5.json|Parámetros ajustados (JSON)", "archivos/FUENTES.md|Inventario de datos y fuentes", "archivos/Resultados_V5_financiacion.md|Resultados detallados del modelo V5"]
_csv = sorted(_os.listdir(D + "")) if False else sorted(f for f in _os.listdir(D) if f.endswith(".csv"))
_files += ["archivos/datos/%s|Datos: %s" % (c, c) for c in _csv]
_files += ["scripts/|Scripts de extracción, ajuste y generación de esta página"]
_links = '<ul class="tight">' + "".join('<li><a href="%s">%s</a></li>' % tuple(x.split("|")) for x in _files) + "</ul>"
TAIL = "El modelo se ha construido con Vensim PLE, de uso personal y educativo.</p>"
assert TAIL in art
art_local = art.replace(TAIL, TAIL + _links)
OGT = "¿Pueden crecer los fondos de inversión mientras se reduce la vivienda accesible?"
OGD = "Estudio abierto: un modelo de dinámica de sistemas de la vivienda en España, con datos oficiales, calibración 1981-2024, el subsistema de financiación y lo que se puede (y no se puede) concluir sobre los fondos."
_url = os.environ.get("SITE_URL", "")
_og = ('<meta name="description" content="%s">\n<meta property="og:type" content="article">\n<meta property="og:locale" content="es_ES">\n'
       '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n<meta name="twitter:card" content="summary">\n' % (OGD, OGT, OGD))
if _url:
    _og += '<meta property="og:url" content="%s">\n' % _url
full = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + _og + '<style>:root{color-scheme:light}body{margin:0}</style>\n</head>\n<body>\n' + art_local + '\n</body>\n</html>\n')
open("panel/Estudio_vivienda.html", "w", encoding="utf-8").write(full)
print("web", len(art), "bytes; completo", len(full), "; perfil:", prof)
