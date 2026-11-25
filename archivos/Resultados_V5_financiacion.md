# Modelo V5: subsistema de financiación (2026-11-23)

Modelo `Vivienda_V5_Financiacion_2050.mdl` (178 variables, 6 vistas; la nueva es «06 Financiación»). Parámetros en `params_ajustados_V5.json`. Euros constantes de 2010. Ajuste a 1981-2024.

## Qué es el subsistema
Idea en una frase: los hogares compran con hipoteca, y lo que pueden pagar depende de su renta, de la cuota por euro prestado (tipo y plazo), de cuánto presta el banco sobre el valor y del ahorro que tienen para la entrada.

1. **Capacidad de compra hipotecaria.** Es el menor de dos límites, en años de renta:
   - por cuota: `esfuerzo máximo / (cuota anual por euro × préstamo/valor)`
   - por entrada: `ahorro en años de renta / (1 − préstamo/valor)`
   La demanda de los hogares sube o baja con el acceso (capacidad / precio sobre renta), y el precio tiende hacia lo que financia el sistema. **Esto sustituye al ancla estadística de la V4.**
2. **Deuda hipotecaria** como existencia: préstamos nuevos (compras financiadas × precio × préstamo/valor) menos amortización.
3. **Rentabilidad real del alquiler** del inversor, observada desde 1996, en lugar de la renta constante.

## Fuentes
- Préstamo/valor (tabla 6.10), plazo y tipo de las hipotecas nuevas (6.11), precio sobre renta y esfuerzo teórico (6.14), deuda de los hogares (6.12), hipotecas constituidas (6.1), rentabilidad por alquiler y de alternativas (7.6): Boletín Anual 2024 del Observatorio de Vivienda y Suelo (MIVAU), con datos de Banco de España y Registradores.
- Tipo oficial y crédito de los hogares sobre PIB: BIS. Hogares: INE (EPA). Renta, inflación, paro: Banco Mundial. Parque y precio: ver `FUENTES.md`.
- Los datos de financiación empiezan en 2003-2004; la rentabilidad, en 1996. Antes se mantiene el último valor conocido (supuesto): préstamo/valor y plazo de 2004, rentabilidad de 1996. El tipo anterior a 2004 es el oficial más 1,5 puntos.

## Ajuste a 1981-2024 (error cuadrático medio)

| | V4 (ancla) | V5 (financiación) |
|---|---|---|
| Precio | 10,2 % | 14,4 % |
| Parque | 1,3 % | 1,1 % |
| Viviendas terminadas | 10,2 % | 13,1 % |
| Deuda hipotecaria frente al BIS | (no ajustada) | 19,9 % |

Tres búsquedas independientes dan casi la misma solución. El ajuste libre sale algo peor que un reajuste local posterior (coste 2,15 frente a 1,94 en el perfil con sensibilidad inversora 0), así que hay margen pequeño de mejora.

## Comprobaciones
1. **Predicción de la crisis.** Ajustado solo hasta 2007, el error del precio en 2008-2024 es del 16-18 % (V4: 22 %, estructura original: 64 %). El parque se desvía un 15 %, y la obra no se anticipa (el freno por exceso de vivienda sin vender solo se aprende de la crisis).
2. **Capacidad de compra.** El modelo da 8 a 10 años de renta, frente al precio sobre renta observado de 7 a 9 años (2004-2024). Desde mediados de los años 90 el límite que manda es la entrada, no la cuota; antes mandaba la cuota (tipos de dos dígitos).
3. **Canal inversor con rentabilidad real.** Se fuerza la sensibilidad inversora a 0, 5, 20 y 80 y se reajusta el resto: el error del precio va de 13,9 % a 15,0 %. Con rentabilidades observadas, los datos agregados siguen sin distinguirlo.
4. **Sin piezas estadísticas.** Quitando las expectativas de los hogares y el paro, el error del precio sube de 14,4 % a 16,1 %. En ese caso el optimizador usa el canal inversor (sensibilidad 68): las dos explicaciones son intercambiables. Los datos necesitan una dinámica de expectativas que se retroalimenta con el precio, y no dicen quién la protagoniza.

## Parámetros destacados (ajuste libre)
Esfuerzo máximo 0,76 (no identificado: con ahorro binding casi nunca manda); ahorro 3,6 años de renta; elasticidad de acceso 1,85; relación precio/capacidad 0,75; velocidad financiera 0,040 al mes; fracción hipotecada 0,28; expectativas de hogares 12,3 (cerca del límite); sensibilidad inversora ~0. En el límite de su rango: fracción de vida media 1, velocidad del precio por presión 0,005, techo 0,3, tau de expectativas 60.

## Palancas de política de financiación (nuevas)
Préstamo/valor (puntos), plazo (meses) y tipos. Con el ajuste actual los tipos y el plazo no tienen efecto desde 2025 porque limita la entrada, no la cuota; subir el préstamo/valor 15 puntos sube la capacidad de 9,3 a 15,3 años de renta y el precio un 61 %. Esa política está fuera del rango observado (56-67 %).

## Avisos
- **La proyección a 2050 no es fiable.** Con financiación sobran 4 millones de viviendas en 2050 y se terminan 305.000 al año (2035-2050); con la V4 faltaban 3,9 millones y se terminaban 23.000. Ninguna extrapolación está cerca de las ~100.000 de 2024. El modelo no tiene restricciones de capacidad de construcción ni de suelo.
- Los supuestos anteriores a 2004 (préstamo/valor, plazo) y a 1996 (rentabilidad) son fijos y no observados.
- El panel publicado sigue siendo el de la V4. No se actualiza hasta revisar la proyección.

## Pendiente
- Restricción de capacidad de construcción y de suelo para que la proyección sea creíble.
- Mercado de alquiler propio (renta como variable) y segmentación de la oferta (qué es asequible).
- Datos de compradores (personas jurídicas, extranjeros) para decidir el canal inversor.
