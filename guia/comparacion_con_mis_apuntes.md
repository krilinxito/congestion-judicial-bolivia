# Comparación: guía de clase vs tus apuntes (Colab)

Cruza la checklist de la sección 7 de `guia_clase_preprocesamiento.md` con tus dos notebooks:

| Notebook | Celdas | Contenido |
|---|---|---|
| `a1.ipynb` | 75 (todas de código) | Feature engineering, discretización, variables temporales, práctica Bike Sharing, balanceo (SMOTE), correlación, PCA, chi², RFE, SFS, `concat`/`merge`/`join`, K-Means y Mall Customers |
| `anal.ipynb` | 54 (1 de markdown) | Faltantes, imputación, outliers (IQR, 3σ, winsorización, mediana, log, DBSCAN, LOF, RANSAC), Titanic, California Housing, escalado (MinMax y Standard), duplicados, y de nuevo transformaciones y discretización |

Referencias: `a1[n]` y `anal[n]` = celda número *n* contando desde 0 (la primera celda de cada notebook es la 0).
Leí el código y las salidas guardadas de las dos libretas.

Leyenda: **✔** lo tienes · **◐** lo tienes a medias · **✘** no lo tienes · **—** es solo teoría, no hay código que comparar.

## 1. Resumen

De los 45 puntos de la checklist: **27 ✔, 8 ◐, 6 ✘, 4 —**.

- Tus apuntes **completan los huecos de las fotos** en dos temas: el **4 (normalización/estandarización)** con `MinMaxScaler` y `StandardScaler` bien hechos (separar antes, `fit` solo en train), y el **7 (duplicados)** con un ejercicio completo.
- Los dos temas que siguen **sin cubrirse ni en las fotos ni en tus apuntes** son la **codificación de categóricas** (tema 6) y la **conversión de tipos** (tema 5, solo hay `to_datetime` y `dtypes`). Tienes `LabelEncoder` y `OrdinalEncoder` importados en `a1[4]` y nunca usados. Conviene preguntarle a la profe o buscar ese material.
- Ninguno de los dos notebooks da error. Solo `a1[74]` está vacía (sin ejecutar).

## 2. Checklist con estado

| # | Técnica | Estado | Dónde |
|---|---|---|---|
| 1 | Detectar nulos (`isnull().sum()`, %, mapa) | ✔ | `anal[0]` |
| 2 | Regla de umbrales 5 / 30 / 50 % | — | Es una tabla de decisión; no hay código |
| 3 | `dropna` filas y columnas | ◐ | `anal[1]` solo filas; falta `dropna(axis=1)` |
| 4 | Imputar media / mediana / moda | ✔ | `anal[2]`, `anal[5]` (ver 4.1) |
| 5 | Imputar con "Desconocido" | ✘ | |
| 6 | Interpolación (`interpolate`) | ✘ | |
| 7 | `KNNImputer` | ✔ | `anal[3]` |
| 8 | Titanic (drop `deck`/`alive`, `age` mediana, `embarked` moda) | ✔ | `anal[4]`, `anal[5]` |
| 9 | Tipos de outlier | — | Teoría |
| 10 | Boxplot / histograma / scatter / violin | ✔ | `anal[8]`, `[9]`, `[10]`, `[38]` |
| 11 | Regla IQR | ✔ | `anal[6]` |
| 12 | Regla 3σ | ✔ | `anal[7]` |
| 13 | DBSCAN para outliers | ✔ | `anal[18]` |
| 14 | LOF | ✔ | `anal[19]` (ver 4.3) |
| 15 | Winsorización | ✔ | `anal[12]`, `[13]`, `[23]`, `[33]`, `[43]` (ver 4.2) |
| 16 | `log1p` y asimetría antes/después | ✔ | `anal[17]` (con `sqrt`), `[29]`, `[36]`, `[41]` |
| 17 | Reemplazo por mediana | ✔ | `anal[13]` |
| 18 | Eliminación por límites IQR | ✔ | `anal[11]`, `[27]`, `[39]` |
| 19 | RANSAC / modelos robustos | ✔ | `anal[20]`, `[31]`, `[32]` |
| 20 | Comparar estrategias y elegir método | ◐ | Comparas medias (`anal[16]`) y % de outliers antes/después (`anal[42]`); falta una conclusión escrita de cuál método usar y por qué |
| 21 | Escalado con `fit` solo en train | ✔ | `anal[45]`, `[46]`; `a1[49]`, `[50]` |
| 22 | `pd.to_datetime` antes de `.dt` | ✔ | `a1[15]` |
| 23 | `pd.cut` vs `pd.qcut` | ✔ | `a1[5]`, `[22]`, `[29]`; `anal[52]` |
| 24 | `LabelEncoder` / `OrdinalEncoder` / `OneHot` | ✘ | Solo el `import` en `a1[4]` |
| 25 | Duplicados exactos y `keep` | ✔ | `a1[18]`, `[19]`; `anal[47]` |
| 26 | Duplicados por clave con valores distintos | ✔ | `a1[20]`, `[21]`; `anal[48]` |
| 27 | Transformaciones matemáticas | ◐ | `log`, diferencia, media, máx, z-score (`a1[1]`), `sqrt` (`anal[17]`); faltan polinomios/`PolynomialFeatures` e interacciones `A*B` |
| 28 | Features temporales (día, mes, fin de semana, festivo, franja) | ✔ | `a1[8]`–`[12]` |
| 29 | Lags y `rolling` | ✘ | |
| 30 | Codificación cíclica seno/coseno | ✘ | |
| 31 | `groupby` + `agg` + `merge` de vuelta | ◐ | `groupby`/`agg` en `a1[23]`–`[28]`, `[31]`; `anal[50]`; falta devolver el resultado con `merge(..., suffixes=...)` o `transform('mean')` |
| 32 | Target encoding | ✘ | |
| 33 | Métricas para desbalance | ✔ | `a1[38]`–`[41]` |
| 34 | Under / over-sampling, SMOTE, `class_weight` | ◐ | `a1[35]`–`[42]`; faltan Tomek Links y NearMiss |
| 35 | Protocolo anti-leakage en balanceo | ◐ | Separas con `stratify` antes de balancear (`a1[42]`); faltan `imblearn.pipeline.Pipeline` y `StratifiedKFold` (los importas en `a1[35]` y no los usas, igual que `cross_val_score`) |
| 36 | Matriz de correlación y umbral 0.9 | ✔ | `a1[43]`–`[45]` |
| 37 | Selección vs extracción | — | Teoría (en la práctica ya tienes ambas) |
| 38 | PCA con estandarización | ✔ | `a1[46]`, `[47]` |
| 39 | `SelectKBest(chi2)` | ✔ | `a1[48]`, `[49]` |
| 40 | RFE y compatibilidad de estimadores | ◐ | Logística `a1[50]`, lineal `[51]`, árbol `[53]`, Random Forest `[54]`; falta **SVM lineal** |
| 41 | `SequentialFeatureSelector` (KNN) | ✔ | `a1[52]` (ver 4.4) |
| 42 | `merge`, `join`, `concat` | ◐ | `a1[55]`; en `merge` solo `how='inner'`, faltan `outer`, `left` y `right` |
| 43 | K-Means, k-means++, codo, silhouette | ✔ | `a1[56]`–`[59]` |
| 44 | Mall Customers | ✔ | `a1[60]`–`[73]` (2 variables con k=5; 3 variables con k=6 y gráfico 3D) |
| 45 | Errores frecuentes | — | Teoría |

## 3. Lo que te falta, en orden de prioridad

1. **Codificación de categóricas** (`OneHotEncoder`, `OrdinalEncoder`, `LabelEncoder`): es un tema entero del temario y no está en las fotos ni en tus apuntes.
2. **Variables temporales avanzadas** (`shift`/lag, `rolling`, seno/coseno): es lo que más rinde para una serie como la del proyecto (`causas_serie_historica`, 2007-2023).
3. **Imputación con "Desconocido"**, `interpolate` y `dropna(axis=1)`: tres técnicas de la clase sobre faltantes que no practicaste.
4. **Agregados devueltos al dataframe**: `groupby(...).transform('mean')` o `merge` con `suffixes`.
5. **Balanceo completo**: Tomek Links, NearMiss y un `imblearn` `Pipeline` con `StratifiedKFold` (ya tienes los imports).
6. **Cierres menores**: RFE con SVM lineal y `merge` con `outer`/`left`/`right`.

## 4. Cosas a revisar en tu código

### 4.1 `anal[2]`: la "moda" de `Nombre` no es la moda
`df_trt["Nombre"].fillna(df_trt["Nombre"].mode())` rellena alineando por índice, no con un valor. Como todos los nombres son distintos, `mode()` devuelve los cuatro nombres ordenados y el hueco del índice 2 se llena con el que tiene ese mismo índice: salió **"Lucia"**, por coincidencia. La moda verdadera con empate sería la primera, **"Ana"**. Usa `.mode()[0]`, como ya haces bien con `embarked` en `anal[5]`. La diapo de clase tiene el mismo patrón sin `[0]`.

### 4.2 `anal[13]`: la winsorización con `limits=(0.025, 0.025)` no cambia nada
Con 15 datos, `floor(15 × 0.025) = 0`, así que no recorta ningún valor. Se nota en `anal[16]`: la media "Winsorización" sale **64.13, igual que la original**, y el tercer gráfico de `anal[15]` es idéntico a los datos originales. En cambio `anal[12]` con `limits=(0, 0.14)` sí funciona (120 y 500 pasan a 31). Para comparar bien, usa en `anal[13]` los mismos límites que en `anal[12]`. Además: en `anal[15]` el panel de winsorización debería mostrar los valores recortados.

### 4.3 `anal[19]`: el comentario no coincide con el código
El comentario dice «5 % de datos considerados outliers» pero el código usa `contamination='auto'`. La diapo usa `contamination=0.05`. Una de las dos cosas hay que corregir.

### 4.4 `a1[52]`: `direction='backward'`
La diapo usa `direction='forward'`. Con 4 variables y `n_features_to_select=2` ambos dan `petal length` y `petal width` (tu salida: exactitud 0.9111, igual que la diapo), pero conviene saber que cambiaste la dirección.

### 4.5 Avisos de pandas
`anal[5]`, `[29]` y `[33]` lanzan `FutureWarning` / `SettingWithCopyWarning`:
`df['age'].fillna(..., inplace=True)` sobre una columna, y asignar columnas sobre un `df` filtrado. Se evitan con `df['age'] = df['age'].fillna(...)` y `df = df[...].copy()`.

### 4.6 Detalles menores
- `a1[29]` y `a1[30]` repiten el mismo `qcut`.
- `a1[40]` y `a1[41]` definen dos veces `mostrar_reporte`; la segunda pisa a la primera.
- `anal[36]` dibuja el histograma con `df_cal` pero pone el rango y la media de `df` (que ya está filtrado en `anal[27]`); los títulos no corresponden al mismo conjunto.

## 5. Lo que tienes y la guía no traía

Estas partes de tus apuntes no estaban en las diapositivas fotografiadas; conviene incorporarlas a la guía:

| Qué | Dónde | Para qué sirve |
|---|---|---|
| `MinMaxScaler` y `StandardScaler` con `train_test_split` antes, parámetros aprendidos (`mean_`, `scale_`) | `anal[45]`, `[46]` | Cubre el tema 4 que las fotos no traen |
| Ver rangos y asimetría de todas las columnas **antes** de escalar | `anal[34]`, `[36]` | Justifica por qué escalar |
| Porcentaje de outliers por columna antes y después (`get_outlier_pct`) | `anal[42]` | Mide si el tratamiento funcionó |
| `clip` con límites IQR (capping) | `anal[21]` | Alternativa manual a `winsorize` |
| Quitar `HouseValue >= 500000` (valores censurados en el dataset) | `anal[27]`, `[39]` | Ejemplo de eliminar un outlier **entendiendo su origen** (regla de oro) |
| Consolidar duplicados con `groupby().agg` y criterio de "quedarse con el mejor" | `anal[49]`, `[50]` | Más allá de `drop_duplicates` |
| `df.groupby(...).ngroup()` para marcar grupos de duplicados | `anal[47]` | Diagnóstico |
| Horas ausentes en una serie temporal (`date_range` vs filas): **165** en Bike Sharing | `a1[16]` | Chequeo de huecos que no estaba en la diapo |
| `pd.Categorical(..., ordered=True)` | `a1[22]` | Categórica ordinal con orden explícito |
| `pivot_table`, `crosstab(normalize=...)` y el **índice contra la base** (1.0 = lo esperado) | `a1[26]`, `[31]`–`[34]` | Caracterizar los segmentos de demanda |
| Silhouette por k en Mall Customers | `a1[63]`, `[70]` | 2 variables: mejor k=5 (0.5547); 3 variables: mejor k=6 (0.4311) |
| Gráfico 3D con Plotly | `a1[72]` | Visualizar clusters |
| Bike Sharing: etapas 3 y 4 de la práctica | `a1[15]`–`[17]` y `[22]` | Tus notebooks sugieren cómo se resolvieron las etapas que no están en las fotos: tipos y revisión de nulos/`cnt`, y creación de `temporada`, `franja_dia` y `tipo_dia`. **[Suposición]** sobre cuál etapa era cuál |

## 6. Qué te sirve de aquí para el proyecto

Los puntos de la sección 8.2 de la guía (candidatos para el proyecto) ya tienen el código escrito en tus apuntes; solo hay que adaptarlo a las columnas del Anuario:

| Candidato para el proyecto | Código que ya tienes |
|---|---|
| Asimetría antes/después del log | `anal[17]`, `[36]`, `[41]` |
| Segmentar la congestión en bajo/medio/alto | `a1[29]`–`[34]` (`qcut` con `retbins` y `crosstab`) |
| Outliers multivariados | `anal[18]` (DBSCAN) y `anal[19]` (LOF) |
| Clustering de territorios/materias | `a1[62]`–`[66]` (escalar, codo, silhouette, clusters) |
| PCA para visualizar | `a1[46]`, `[47]` |
| Porcentaje de outliers antes/después de tratar | `anal[42]` |
| Correlación entre indicadores | `a1[43]`–`[45]` (con la advertencia de que `atendidas = resueltas + pendientes_fin` es una identidad contable) |

Recuerda que `requirements.txt` del proyecto no incluye `scikit-learn` (ni `seaborn`, `plotly`): hay que añadirlos antes de usar cualquiera de estos fragmentos.
