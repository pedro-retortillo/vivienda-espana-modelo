# Scripts

Scripts de trabajo con los que se extrajeron los datos, se ajustó el modelo y se generó la página. Son el código tal como se usó: pueden necesitar ajustes de rutas (por ejemplo, las carpetas `panel/` y la variable de entorno `VIV_DATOS`) y las bibliotecas `numpy`, `scipy` y `pypdf`.

- `engine.py`: motor de simulación que lee las ecuaciones en sintaxis de Vensim.
- `v2_model.py`, `v3_model.py`, `v4_model.py`, `vfin_model.py`: el modelo, versión a versión (`vfin_model.py` es la V5, con financiación; `v6_model.py` es la V6, con costes de construcción).
- `calib.py`, `run_calib.py`, `run_defin.py`, `profile_vp.py`, `profile_beta5.py`: ajuste con evolución diferencial y pruebas de perfil.
- `extrae_datos.py`, `extrae_fin.py`: extracción de las tablas del Boletín del Observatorio de Vivienda y Suelo y de las APIs del BIS y del Banco Mundial.
- `make_diagrams.py`, `gen_js2.py`, `build_web.py`, `web.src.html`: generación de la página.
