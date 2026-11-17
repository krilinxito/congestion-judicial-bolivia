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

## Pendiente
- Revisar visualmente la presentación 3 en el navegador (el usuario rechazó las capturas automáticas).
- Commit (no se pidió todavía).
