# Congestión judicial en Bolivia — Anuario Estadístico Judicial 2023

El Consejo de la Magistratura de Bolivia publica cada año las estadísticas de
todos los juzgados del país en un PDF de 774 páginas, sin datos abiertos. Este
proyecto lo convierte en **doce tablas (85.953 filas)**, cada fila con su cuadro
y su página de origen; las verifica contra las identidades contables del propio
Anuario; las organiza en una capa analítica sin multiplicar datos, y calcula
indicadores de congestión judicial por materia, tipo de proceso y territorio.

**Toda la documentación está en la web del proyecto (`web/`)**: conceptos
jurídicos, la fuente, cada tabla y cada columna, cada notebook, las técnicas de
extracción, las auditorías, los resultados, las decisiones y los errores.

Para verla localmente:

```bash
cd web && python -m http.server 8000     # abrir http://localhost:8000
```

## Qué hay

```
notebooks/        todo el código, en notebooks ejecutados (se leen sin correr nada)
  01 … 08         extracción, normalización, validación, exportación, integración
  09 … 12         nulos, indicadores, outliers, reporte
  13              verificación final
  14 … 18         ampliación: capítulo 9, serie 2007-2023, diagnóstico, técnicas de la clase y recursos
  modulos/        funciones y tablas compartidas, cargadas con %run -i
data/processed/   las 12 tablas en CSV y Parquet (el Parquet es la referencia)
  auditoria/      evidencia de cada decisión y cada validación
  analitico/      capa analítica: 5 tablas relacionadas + diccionario
data/curated/     tabla analítica con indicadores y tratamientos del EDA
reports/          tablas resumen y figuras
web/              la documentación
```

## Resultados principales

La justicia **no penal** (47,5 % de las causas: las materias penales no publican
causas resueltas) resolvió en 2023 el **100,7 %** de lo que recibió, pero su
stock heredado casi no baja (−1,3 %). Coactivo Fiscal y Tributario tardaría unos
1.417 días en vaciar su stock; Civil y Comercial, unos 162. La brecha entre
capitales y provincias es moderada (213 contra 238 días).

**Ampliación (notebooks 14 a 18).** Con el capítulo 9 del Anuario se cubren todas las materias: en 2023 el
stock nacional subió 19.114 causas dentro del año y casi todo es penal (no penal −1.379, penal +13.134,
ejecución penal +7.359). Con las fórmulas del CEJA, Bolivia 2023 tiene tasa de resolución 0,95 y de
congestión 1,93, y las cifras de 2019 a 2022 coinciden con las del CEJA. El 6 % de los procesos no
penales concentra el 73 % del rezago, y lo que más explica la duración es el tipo de proceso, no
ser capital o provincia. El notebook 18 cruza la carga con el personal de cada departamento: 2,6 veces entre Pando (33 causas
ingresadas por puesto ocupado) y Santa Cruz (85), sin relación significativa con los resultados (n = 9).
El notebook 17 pone las técnicas de la clase de preprocesamiento (asimetría, discretización, contexto de grupo,
variables temporales, correlación, PCA, outliers multivariados) frente al proyecto. Ver `web/ampliacion.html` y la
presentación `web/presentacion-ampliacion.html`.

> Corrección: una primera versión decía 83,4 %. Contaba como ingreso las causas
> `readecuadas_ley_439`, que en civil son el stock inicial (ocupan el lugar de
> `pendientes_inicio` y suman lo mismo que el cuadro 9.1.x). Ver
> `web/decisiones.html#las-readecuadas`.

## Reproducir

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt       # Windows: .venv\Scripts\pip
# poppler (pdftotext) solo para los notebooks 01, 02, 03 y 07
# el PDF va en data/raw/anuario_2023.pdf (ver data/raw/README.md)
```

Orden de ejecución: `01 → 02 → 03 → 07 → 04 → 05 → 06 → 08 → 09 → 10 → 11 →
12 → 14 → 15 → 16 → 17 → 18 → 13`. Desde el 08 no hace falta el PDF. Detalle en la página «Cómo
reproducir» de la web.

## Fuente

Consejo de la Magistratura de Bolivia, *Anuario Estadístico Judicial 2023*,
Jefatura Nacional de Estudios Técnicos y Estadísticos. SHA-256 del PDF:
`8B860105762A5987509C65AA4482B240FA21FDE2E6E6EC5C0902022AC243F851`.

Proyecto de Análisis de Datos · Andrés Maximiliano Espinoza Romero · Andrés
Gabriel Maydana García · Maximiliano Gómez Mallo.
