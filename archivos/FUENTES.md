# Datos para calibrar el modelo de vivienda (España, 1980 en adelante)

Descargados el 2026-11-20 de fuentes oficiales de acceso público. Los CSV están en `datos\`.
El script `extrae_datos.py` (en `Vensim\generadores`) los extrae del PDF y de la API del BIS.

## Lo que sí hay

| Archivo | Contenido | Periodo | Fuente |
|---|---|---|---|
| `parque_hogares_1981_2024.csv` | Parque total (estimación BdE 1981-2020, MIVAU 2001-2023, censos), viviendas principales y hogares EPA | 1981, 1985-2024 | Boletín Anual 2024 del Observatorio de Vivienda y Suelo (MIVAU), tabla 8.1 |
| `parque_mivau_principal_noprincipal_2003_2023.csv` | Parque familiar, principal y no principal | 2003-2023 | mismo boletín, tabla 8.2 |
| `viviendas_iniciadas_terminadas_2003_2024.csv` | Iniciadas y terminadas (libres y protegidas) | 2003-2024 | mismo boletín, tabla 1.2 |
| `precio_valor_tasado_eur_m2_2003_2024.csv` | Precio de la vivienda libre y protegida, €/m² (4T de cada año) | 2003-2024 | mismo boletín, tablas 2.1 y 2.2 |
| `tenencia_viviendas_principales_censos.csv` | Propiedad, alquiler, cesión y otros | censos 1970-2021 | mismo boletín, tabla 5.4 (1981: 73,1 / 20,8 / 6,1) |
| `BIS_precio_vivienda_Espana_nominal_1971_.csv` y `..._real_...` | Índice de precios de la vivienda de España (base 2010 = 100), trimestral | 1971-Q1 a 2026-Q2 | BIS, conjunto WS_SPP (series del Banco de España) |
| `INE_censo2021_prensa.pdf`, `MIVAU_Observatorio_boletin_anual_2024.pdf` | Documentos originales | | INE y MIVAU |

## Condiciones iniciales de 1981 (censo)
- Viviendas totales (censo): 14.726.134; estimación BdE: 14.860.272.
- Viviendas principales (= hogares del censo): 10.431.327. Hogares EPA: 10.153.000.
- Tenencia de las principales: propiedad 73,1 %, alquiler 20,8 %, cesión y otros 6,1 %.
- No principales (1981, análisis del INAP del censo): secundarias 1.898.602 y desocupadas 2.396.205 (aprox. 4,3 M).

## Precio: cómo se une la serie larga
El índice del BIS (Banco de España) empieza en 1971 pero es un índice, no €/m². Anclado al valor tasado del MIVAU en el 4T de 2005 (1.824,3 €/m² = índice 94,5), 1 punto = 19,31 €/m². Con ese ancla:
- 1980: unos 135 €/m² nominales; 1990: 595; 2000: 893; 2007: 2.150 (MIVAU 2.086); 2014: 1.395 (MIVAU 1.463); 2024: 2.383 (MIVAU 1.972).
- Desviación media frente al MIVAU 2003-2024: 6,2 %, y llega al +21 % en 2024. Las dos series no miden lo mismo (la del BIS usa otras fuentes desde 2007). Para 2003-2024 se usa el MIVAU; antes de 2003, el índice anclado, con más incertidumbre.

## Avisos
- El parque BdE se queda en 25,07 M desde 2012 mientras el MIVAU y el censo 2021 (26,62 M) siguen creciendo: la serie BdE no está actualizada. Se usa BdE 1981-2000 y MIVAU 2001-2023.
- Los censos cuentan viviendas familiares; el MIVAU y el BdE, estimaciones. Hay diferencias de 1-2 % entre ellas.
- El precio de 1980 a 1995 es una reconstrucción, no una serie oficial de €/m².

## Entradas externas descargadas el 2026-11-20

| Archivo | Contenido | Periodo | Fuente |
|---|---|---|---|
| `WB_Espana_PIB_per_capita_USD2015_1975_2025.csv` | PIB per cápita en USD constantes de 2015 (proxy de la renta real: solo importa su evolución relativa) | 1975-2025 | Banco Mundial, NY.GDP.PCAP.KD |
| `WB_Espana_inflacion_IPC_pct_1975_2025.csv` | Inflación del IPC (% anual); sirve para deflactar | 1975-2025 | Banco Mundial, FP.CPI.TOTL.ZG |
| `WB_Espana_poblacion_1975_2025.csv` | Población total | 1975-2025 | Banco Mundial, SP.POP.TOTL |
| `BIS_credito_hogares_pct_PIB_Espana_1980_.csv` | Crédito a hogares, % del PIB, trimestral | 1980-Q4 a 2026-Q1 | BIS, WS_TC |
| `BIS_tipo_oficial_Espana_1945_1998.csv` y `BIS_tipo_oficial_zona_euro_1999_.csv` | Tipo oficial del banco central (%) | 1945-1998 y 1999-2026 | BIS, WS_CBPOL |

Comprobaciones de sentido: el PIB per cápita se multiplica por 1,96 entre 1980 y 2024 (27.339 en 2007, 24.499 en 2013); el IPC pasa del 15,6 % en 1980 al 3,4 % en 2000; el crédito a hogares va del 24 % del PIB en 1980 al 85 % en 2009 y baja al 44 % en 2024; el tipo oficial va del 19 % en 1981 al 3 % en 1998 y al 0,25 % en 2013.

## Financiación y rentabilidad de inversores (2026-11-23)
Extraídas del Boletín Anual 2024 del Observatorio de Vivienda y Suelo (MIVAU) con `extrae_fin.py`:

| Archivo | Contenido | Periodo | Tabla y fuente original |
|---|---|---|---|
| `financiacion_hipotecas_2003_2024.csv` | Préstamo/valor y % de créditos con préstamo/valor > 80 % | 2004-2024 | 6.10, Estadística Registral Inmobiliaria |
| | Plazo medio (meses) y tipo de las nuevas hipotecas | 2004-2024 | 6.11, Banco de España y Registradores |
| | Precio/renta bruta del hogar (años) y esfuerzo teórico anual (%) | 2003-2024 | 6.14, Banco de España |
| | Endeudamiento de los hogares (% PIB) y renta bruta disponible | 2004-2024 | 6.12, Banco de España |
| | Hipotecas de vivienda constituidas (unidades) | 2004-2024 | 6.1, Registradores |
| `rentabilidad_vivienda_alternativas_1996_2024.csv` | Rentabilidad anual de la vivienda, bruta por alquiler, bonos a 10 años, depósitos e IBEX-35 | 1996-2024 | 7.6, Banco de España |

Avisos: los datos de financiación empiezan en 2003-2004 (la rentabilidad, en 1996); antes de esas fechas solo hay el tipo oficial y el crédito/PIB del BIS. Los bonos y los depósitos tienen años sin dato.

## Decisión de modelización (2026-11-20)
Se calibra en **euros constantes** (reales). El índice de precios del BIS tiene versión real. Renta, costes y rentas de alquiler se deflactan con el IPC.

## Lo que falta
- Viviendas terminadas 1981-2002 (el boletín solo da desde 2003). Mientras tanto, el aumento anual del parque estimado da una aproximación (terminadas menos demoliciones).
- Tipo de interés hipotecario real: no se encontró una serie larga automática. Se aproximará con el tipo oficial más un diferencial fijo.
- Costes de construcción, rentas de alquiler y migración año a año desde 1980. La población y los hogares de la EPA cubren la demografía.
- Demoliciones y salidas del parque.
- Renta de los hogares en sentido estricto: el PIB per cápita es solo un proxy.

## Costes de construcción (V6)
- **Precios de materiales de construcción** (cemento, cerámica, madera, acero, energía, cobre, aluminio, ligantes), mensual desde 1995: INE, operación «Índices de Precios de Materiales y Energía e Índices Nacionales de la Mano de Obra», tabla 49298 (base 1964, península y Baleares). En el modelo: media simple de los 8, deflactada con el IPC (Banco Mundial) y relativa a 1981.
- **Índice nacional de la mano de obra en construcción**, mensual desde 1995: INE, misma operación, tabla 8377. Según su metodología reproduce el 85 % de la variación del índice salarial general: es una convención, no el coste efectivo de las cuadrillas.
- **Antes de 1995** no se usa dato: se mantiene el coste real constante (supuesto).
- **Escalones normativos** (CTE 2006, DB-HE 2013, DB-HE 2019): fechas de entrada en vigor; el tamaño de cada escalón es un supuesto que el ajuste no identifica.
- Precio medio del suelo urbano (Boletín del Observatorio de Vivienda y Suelo, tabla 3.3, desde 2004): disponible, no se usa en el ajuste; el suelo entra como fracción del precio.
- Archivos: `datos/INE_costes_construccion_1995_2025.csv` y `datos/indice_coste_construccion_1981_2024.csv`.
