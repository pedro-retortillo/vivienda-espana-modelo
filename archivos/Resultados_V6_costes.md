# Resultados V6: costes de construcción reales

Modelo V5 más costes de construcción con series del INE (materiales y mano de obra, 1995-2024), escalones normativos y un precio de coste que actúa como suelo del precio. Ajuste 1981-2024 por evolución diferencial.

## Modelo base publicado
Costes reales solo a través del margen de la obra. El suelo de coste y los escalones normativos están en el modelo, pero apagados (valor 0): los datos no los sostienen (ver más abajo). Parámetros en `params_ajustados_V6.json`; el ajuste con ambos libres, en `params_ajustados_V6_completa.json`.

## Ajuste 1981-2024 (suma de errores al cuadrado; menos es mejor)
| Modelo | Coste |
|---|---|
| V5 | 2,15 a 2,24 |
| V6 base (costes reales por el margen) | 2,056 |
| V6 con suelo de coste y normativa libres | 2,045 |

## Errores medios 1981-2024
| | Precio | Parque | Terminadas |
|---|---|---|---|
| V5 | 14,4 % | 1,15 % | 13,1 % |
| V6 base | 14,4 % | 1,2 % | 12,1 % |

## Predicción fuera de muestra (ajustar hasta 2007, predecir el precio 2008-2024), dos semillas
| Modelo | Semilla 1 | Semilla 2 |
|---|---|---|
| V5 | 17,8 % | 16,0 % |
| V6 base | 18,2 % | 41,1 % |
| V6 con suelo de coste y normativa libres | 149 % | 28 % |

Con costes reales la predicción depende del ajuste. Con el suelo de coste y la normativa libres empeora y se vuelve inestable: los parámetros toman valores altos y distintos en cada semilla, señal de que no están identificados.

## Lectura
Los costes explican algo de cuánto se construye (obra terminada 2021-22: dato 94.700 y 89.500; V5 77.500 y 80.000; V6 83.000 y 85.200), no el precio. Añadirlos no mejora la predicción de la crisis, y la hace menos robusta. La tesis sobre los fondos queda tan abierta como antes. La proyección a 2050 sigue sin ser fiable (sobran ≈4,2 millones de viviendas; ≈254.000 terminadas al año).

## Límites
Mano de obra: índice del INE que sigue la variación salarial general (no mide el coste efectivo). Materiales: media simple, sin ponderar. Antes de 1995: coste real constante. Normativa: tamaño supuesto. Solo dos semillas en la prueba fuera de muestra.
