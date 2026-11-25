# Vivienda en España 1981-2050: un estudio abierto

¿Pueden crecer los fondos de inversión mientras se reduce la vivienda accesible?

Este repositorio contiene un modelo de dinámica de sistemas de la vivienda en España, construido desde el censo de 1981 y contrastado con datos oficiales, y la página web que explica el estudio.

**Ver la web:** https://pedro-retortillo.github.io/vivienda-espana-modelo/

## Qué incluye
- `index.html`: la web del estudio (se abre con doble clic en cualquier navegador, sin conexión).
- `archivos/`: el modelo para Vensim (V5, con seis vistas) y su versión de solo ecuaciones, los parámetros ajustados, el inventario de fuentes, los resultados detallados y los datos en CSV.
- `scripts/`: el código de extracción de datos, ajuste y generación de la página.

## Resumen
- Un modelo con siete subsistemas (parque de viviendas, hogares, demandas, precio, obra, financiación y políticas) que reproduce el parque, el precio, las viviendas terminadas y la deuda hipotecaria de 1981 a 2024.
- Ajustado solo hasta 2007, predice el precio de la crisis con un error del 16-18 %.
- Con datos agregados no se puede distinguir si el precio lo mueven los fondos o los hogares con expectativas.
- La proyección hasta 2050 no es una predicción: depende de supuestos y no es fiable en niveles.

## Fuentes
Observatorio de Vivienda y Suelo (Ministerio de Vivienda y Agenda Urbana), INE, Banco de España, Registradores, BIS y Banco Mundial. El detalle está en `archivos/FUENTES.md`. Los datos conservan las condiciones de uso de sus fuentes originales.

## Avisos
Es un modelo conceptual: explora supuestos, no predice. Los supuestos anteriores a 2004 (préstamo sobre valor y plazo) y anteriores a 1996 (rentabilidad por alquiler) no son datos observados y están marcados como tales. El modelo se ha construido con Vensim PLE, de uso personal y educativo.

## Autor
Pedro Manuel Retortillo Atienza. Versión del 25 de noviembre de 2026.

## Licencia
Ver el archivo `LICENSE`.
