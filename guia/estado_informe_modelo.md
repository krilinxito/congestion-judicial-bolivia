# Estado del trabajo: informe final (pizarra), presentación 3 y guía de estudio

Pausado el 2026-11-16. Plan aprobado completo en `C:\Users\barry\.claude\plans\hola-del-proyecto-existente-delightful-fairy.md`.

## Qué pidió la docente (pizarra)
1. Preprocesamiento (EDA, limpieza, conversión) → 2. Modelo (SVM, Bagging, Boosting, Stacking, hiperparámetros) →
3. Evaluación (importancia; comparar con todas las variables, con más variables y con las 5 más importantes) →
4. Despliegue (modelo de 5 variables). Los números 19/25/5 de la pizarra eran ejemplos.

## Decisiones tomadas
- Objetivo: `flag_acumula_mora` (resueltas < ingresos del año, tasa de resolución < 1; definición del notebook 10). Clasificación binaria.
- Despliegue: página web `web/prediccion.html` que corre el modelo en el navegador (JSON exportado).
- Informe: LaTeX compilado con pdflatex (MiKTeX ya instalado) en `informe/`.
- **Todo el código Python va en notebooks** (nada de `.py`).
- `scikit-learn 1.9.1` ya está instalado en `.venv` (falta agregarlo a `requirements.txt`).

## Hecho (actualizado 2026-11-16, segunda sesión)
- Filtro corregido a `atendidas > 0`: **1.240 filas, 608 acumulan (49,0 %)**, 992 entrenamiento / 248 prueba.
- Notebooks 19 → 22 re-ejecutados sin errores, con sus «Lecturas» escritas con las cifras reales.
- Resultados: CV ajustado Bagging 0,753 = Random Forest 0,753 = Stacking 0,753 > GB 0,744 > Logística 0,730 > SVM 0,729 > AdaBoost 0,728.
  Prueba: Bagging 0,729. Top 5: ingresos por juzgado, presión del stock, stock por juzgado, materia, ingresos del año.
  Versiones (Bagging CV/prueba): 19 → 0,735/0,712; 27 → 0,753/0,729; 5 → 0,704/0,658.
  Desplegado: Gradient Boosting 5 variables (200 árboles), prueba AUC 0,663, exactitud 0,589; JSON = sklearn (3e-16).
- `informe/informe.tex` → `informe.pdf` (15 páginas, compila sin advertencias). Compilar con `--disable-installer`
  (con `tcolorbox[most]` MiKTeX se colgaba pidiendo instalar un paquete).
- `requirements.txt` (scikit-learn 1.9.1) y `README.md` (notebooks 19-22, carpetas, orden) actualizados.
- `web/prediccion.html/.js`: textos con cifras calculadas desde el JSON (sin 1.122 fijo).

- Presentación 3 `web/presentacion-informe.html` (32 diapositivas, tres partes) y entrada en el menú «Presentar» de `web/app.js`.
- Guía de estudio `web/guia-informe.html`: recorre el informe sección por sección (resumen, introducción, tablas 1-8,
  figuras 1-7, cada hiperparámetro, conclusiones, limitaciones, referencias, anexo), con el ejemplo de Sucre y 26 preguntas.
  **El usuario pidió NO hacer guion**: no crear `guion_y_preguntas_informe.md`.
- Grupo «Informe final» en `PAGINAS` de `app.js` (guía + predicción); `app.js?v=1ee6d900` en todas las páginas.
- `web/limites.html` ya dice que los notebooks 19-22 sí entrenan modelos.
- `prediccion.html` verificada con Edge sin interfaz: 20/20 coinciden.

## Despliegue real (2026-11-16, tercera parte)
- Carpeta `despliegue/`: página pública (`sitio/`: index.html, estilos.css, prediccion.js, modelo JSON, escudo UMSA),
  `nginx.conf`, `Dockerfile` (nginx-unprivileged 1.27, puerto 8080, /salud) y `docker-compose.yml` (servicio prediccion-mora,
  solo lectura, cap_drop ALL, healthcheck). Sin Python en el servidor. Instrucciones en `despliegue/README.md`.
- El notebook 22 escribe el JSON también en `despliegue/sitio/modelo/` y verifica que sea idéntico.
- El JS de la página pública se probó con Node.js en los 248 procesos de prueba: coincide con scikit-learn (2e-16).
- `docker compose config` valida. Publicado con Dokploy (Compose desde GitHub `main`, ruta `./despliegue/docker-compose.yml`,
  dominio con Traefik + Let's Encrypt al puerto 8080) en https://proyanalisis.maxi42.space/ — `/salud` responde `ok`.
- Presentación 3: QR de la URL en la portada (`web/img/qr-proyanalisis.svg`, generado con segno y verificado con OpenCV);
  diapositivas 30, 31 y 33 con la URL real. Guía: dominio, HTTPS, DNS, Dokploy y Traefik explicados.
- Informe: portada con escudo UMSA, materia Análisis de Datos, docente M.Sc. Madelina Loza Soliz; sección 4 con 4.1-4.3
  (modelo exportado, página, VPS con Docker Compose). Presentación 3: portada con escudo y diapositiva 30 de Docker (33 en total).
  Guía de estudio: VPS, Docker, nginx y Compose explicados desde cero.

## Cierre de la presentación 3 (2026-11-17)
- Final reescrito con enfoque judicial (40 diapositivas): 32 portada «Qué nos dice esto sobre la justicia»,
  33-37 cinco hallazgos (carga por juzgado; personal no explica, n = 9; rezago concentrado 6 % → 73 %;
  stock heredado alto tiende a bajar, asociación; datos no abiertos), 38 aplicación (alerta temprana, 49 % → 64 %),
  39 límites, 40 resumen con los cinco hallazgos. El informe LaTeX no se cambió.

## Página pública utilitaria (2026-11-17)
- `despliegue/sitio/` reescrita para la gente: se elige materia, tipo y lugar (19 lugares) y muestra la fila hoy
  (pendientes ÷ resueltas × 365), si es probable que crezca el año siguiente (3 niveles: >= 60 %, 40-60 %, < 40 %),
  2023, el mismo trámite en otros lugares y una tabla de prioridades (p >= 60 %, ordenada por pendientes).
- Datos: `notebooks/23_sitio_publico.ipynb` -> `despliegue/sitio/datos/procesos.json` (1.240 procesos, 59 KB).
  Escenario: stock = pendientes al cierre 2023, mismos juzgados e ingresos. 408 crece / 423 incierto / 409 no crece.
  Variación nacional de ingresos: mediana 6,3 %. Proyección NO validada (un solo Anuario).
- La página recalcula las 1.240 probabilidades y las compara con Python: 1.240 / 1.240 (probado con Edge headless).
- nginx: `location ~ ^/(modelo|datos)/` sin caché. `web/prediccion.html` (versión de clase) no se tocó.
- Presentación 3: diapositivas 30, 31, 38 y 39 actualizadas; guía de estudio (parte 4) actualizada.

## Pendiente
- El informe LaTeX (sección 4.3 y anexo) todavía usa `IP-DEL-VPS` y no menciona la URL ni Dokploy.

## Cambio de objetivo: «¿cuánto va a tardar mi caso?» (2026-11-19) — EN PAUSA
Se reemplazó el objetivo `flag_acumula_mora` (clasificación) por el **tiempo de la fila** (pendientes al cierre ÷ resueltas
× 365, días; regresión sobre log(1 + días), tope 10 años) usando la historia 2007-2023 del capítulo 9.
Hecho (sin commit todavía):
- Notebooks `modulos/modelado`, 19-23 reescritos y ejecutados, con sus «Lecturas». Conjunto: 808 procesos (≥ 10 causas
  atendidas y alguna resuelta), 646/162. Historia: vaciado real vs estimado 11,7 % (47 comprobaciones), año anterior 8,8 %.
  Mejor: Stacking (MAE log 0,738 CV; prueba 0,694, 67 % dentro del doble). Top 5: log stock, presión, log ingresos,
  ingresos/juzgado, stock/juzgado (3 datos). Desplegado: Gradient Boosting 5 var (100 árboles, 68 % dentro del doble),
  rango por tamaño (bandas.csv, cobertura 57 %). Variable histórica `tendencia_resueltas_materia` (puesto 17).
- `despliegue/sitio/` (index.html, prediccion.js, estilos.css v=3) reescrito: estimación + rango + 2023 + ritmo de la
  materia + historia (SVG) + «dónde tarda más». Verificado en Edge: 1.240/1.240. README y Dockerfile actualizados
  (el servicio sigue llamándose `prediccion-mora` para no romper Dokploy).
- `web/prediccion.html/.js` (versión de clase) en regresión: 20/20. `app.js` (menú, ?v=2b7c41d0), `limites.html`.
- `informe/informe.tex` reescrito → `informe.pdf` 18 páginas, sin advertencias (tablas nuevas: historia_vaciado,
  historia_formas, tamano, bandas). Ya incluye la URL y Dokploy.
- `web/presentacion-informe.html`: 39 diapositivas nuevas.

Terminado el 2026-11-19 (segunda parte):
- **Guía `web/guia-informe.html` completa** (para qué sirve primero; luego portada, introducción, partes 1-4 con
  tablas 1-13 y figuras 1-8, cada hiperparámetro, conclusiones, limitaciones, referencias, anexo, cifras, diccionario;
  44 preguntas de autoevaluación). El divorcio en Sucre se sigue hasta el modelo publicado (5 variables → 4,218 → 67 días,
  rango 44-97). Borradores borrados. Verificada con Edge sin interfaz.
- README.md: objetivo nuevo, resultados, orden con el 23, URL pública.

Pendiente: revisar y hacer commit (y push, que vuelve a publicar la página con Dokploy).
