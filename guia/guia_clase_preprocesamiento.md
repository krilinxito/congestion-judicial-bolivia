# Guía de clase: preprocesamiento de datos (y aprendizaje no supervisado)

Reconstruida a partir de **200 fotos de las diapositivas** (carpeta `diapos/`, dos zips de WhatsApp).
Sirve para dos cosas: (1) cruzarla con tus apuntes de notebooks y ver qué falta o qué difiere,
(2) decidir qué técnicas de la clase se aplican a este proyecto (sección 8).

Convención: los títulos entre comillas son los **títulos exactos de la diapositiva**, para que los
ubiques en las fotos. Lo que es mi lectura o suposición, y no algo que la diapositiva diga, está
marcado como **[Suposición]**.

---

## 0. Cómo usar esta guía

1. Lee la sección 1 y 2 para saber qué cubren las fotos y qué **no**.
2. Recorre la sección 7 (checklist) con tus notebooks al lado y marca qué tienes.
3. Lo que no tengas marcado, búscalo en la sección 3 a 6 (qué dijo la clase y con qué código).
4. La sección 8 propone qué aplicar al proyecto; es **mi propuesta**, no viene de las diapositivas.

---

## 1. Qué hay en las fotos

| Hecho | Detalle |
|---|---|
| Cantidad | 200 fotos, muchas repetidas (la misma diapositiva 2 a 4 veces); sirven para confirmar lectura |
| Presentaciones | **Dos** distintas: (A) *Aprendizaje no supervisado / clustering* (fondo blanco, franja naranja, ~12 diapos) y (B) *Preprocesamiento de datos* (borde amarillo/verde, el grueso) |
| Orden | Las fotos están en **orden inverso** al de la clase (primero las últimas diapositivas, al final la introducción). En esta guía todo va en el orden lógico del temario |
| Qué se ve en las fotos de B | Los temas 1, 2, 3, 8, 9, 10 y 11 con bastante detalle; la **práctica Bike Sharing** (parcial) |
| Qué **no** se ve | Casi nada de los temas **4** (normalización/estandarización), **5** (conversión de tipos), **6** (codificación de categóricas, salvo discretización) y **7** (duplicados, salvo en la práctica). Es posible que esas diapositivas no se hayan fotografiado o que se dieran en otra clase. Tus apuntes son la fuente para ellos |

Un detalle de contexto: las diapositivas de la presentación A (clustering) **no son preprocesamiento**
en sentido estricto, pero están en la misma carpeta, y la diapo «Variable categórica» (K-Means) conecta
con codificación. Las incluyo como Parte B porque pueden servir para el proyecto.

## 2. Temario de la clase (diapositiva «Contenido»)

| # | Tema | Cobertura en fotos |
|---|---|---|
| 1 | Introducción al preprocesamiento de datos | Completa |
| 2 | Manejo de datos faltantes | Completa |
| 3 | Detección y manejo de valores atípicos (outliers) | Completa (la más larga) |
| 4 | Normalización y estandarización de datos | Solo menciones sueltas |
| 5 | Conversión de tipos de datos | Solo `pd.to_datetime` suelto |
| 6 | Codificación de variables categóricas | Solo discretización (`cut`/`qcut`) |
| 7 | Tratamiento de datos duplicados | Solo en la práctica |
| 8 | Creación de nuevas variables (feature engineering) | Completa |
| 9 | Balanceo de datos en problemas desbalanceados | Completa |
| 10 | Reducción de dimensionalidad | Completa (selección, correlación, PCA) |
| 11 | Integración y fusión de datos | Completa (`merge`, `join`, `concat`) |

---

## 3. Preprocesamiento, tema por tema

### 3.1 Introducción al preprocesamiento

- Es una de las etapas más importantes del ciclo de vida del análisis. Objetivo: transformar datos
  crudos en un formato adecuado para análisis y modelado, mejorando la calidad de los resultados.
- Los datos originales suelen estar **desordenados, incompletos y ruidosos**. Datos mal procesados
  llevan a resultados erróneos, sesgados o poco confiables.
- «**80 % del tiempo** en ciencia de datos se dedica al preprocesamiento».
- «Impacto de los datos sucios»: valores faltantes; valores atípicos; inconsistencias de formato
  (unidades, fechas mal formateadas); errores tipográficos ("Bolivia" vs "BOLIVIA" vs "Boliva");
  duplicados. Consecuencias: modelos menos precisos y con mala generalización, conclusiones erróneas,
  decisiones incorrectas, overfitting o underfitting.
- «Herramientas y librerías»: Python (pandas, numpy, `sklearn.preprocessing`, scipy), R (dplyr,
  tidyverse, caret), SQL; Excel/Google Sheets, OpenRefine, Power BI/Tableau; Spark, Hadoop, BigQuery,
  AWS Glue; automatización con `Pipeline` y `ColumnTransformer` de scikit-learn y herramientas ETL.

### 3.2 Datos faltantes

**Por qué aparecen** («Identificación de valores faltantes»): errores de captura, integración de fuentes
distintas, fallas de sensores o sistemas de registro, respuestas opcionales en encuestas.

**Cómo detectarlos** (pandas):

```python
df.isnull().sum()                                         # cantidad por columna
(df.isnull().sum() / len(df) * 100).round(2).astype(str) + "%"   # porcentaje
df.isnull()                                               # mapa True = faltante
```

**Regla de umbrales** (diapositiva «Regla de umbrales»):

| % de nulos | Decisión recomendada |
|---|---|
| Menor a 5 % | Eliminar filas (pérdida despreciable) |
| De 5 % a 30 % | Imputar valores |
| Mayor a 30 % en columna | Eliminar la columna completa |
| Mayor a 50 % en fila | Eliminar la fila |

**Eliminar** («Métodos para manejar valores faltantes»): `df.dropna()` (filas), `df.dropna(axis=1)`
(columnas). Desventaja: se pierden datos; mal si el porcentaje es alto.

**Imputar** («Imputación de valores faltantes»), cuando eliminar no es recomendable:

```python
df_trt = df.copy()
df_trt['Edad']    = df_trt['Edad'].fillna(df_trt['Edad'].mean())          # media
df_trt['Salario'] = df_trt['Salario'].fillna(df_trt['Salario'].median())  # mediana
df_trt['Nombre']  = df_trt['Nombre'].fillna(df_trt['Nombre'].mode()[0])   # moda
df_trt['Nombre']  = df_trt['Nombre'].fillna('Desconocido')                # valor específico
```

Por tipo de dato:

| Tipo | Métodos que enseñó |
|---|---|
| Numéricos («Métodos de manejo de datos numéricos») | 1) media/mediana/moda (si hay distribución normal o pocos faltantes); 2) **interpolación** si hay progresión lógica, p. ej. temperatura en el tiempo: `df['temperatura'].interpolate(method='linear')`; 3) modelos predictivos (KNN, regresión) |
| Categóricos (ordinales: nivel educativo; nominales: colores, ciudades) | 1) moda (si hay categoría dominante); 2) "Desconocido"/"Otro" (para no suponer nada); 3) modelo de ML si el dataset es grande |
| Temporales («Métodos de manejo de datos temporales») | 1) interpolación temporal; 2) fecha más frecuente (`.fillna(...mode()[0])`); 3) extraer `.dt.month`, `.dt.year` |

**Imputación con modelos** («Imputación con modelos predictivos»):

```python
from sklearn.impute import KNNImputer
imputer = KNNImputer(n_neighbors=2)
df_trt2[['Edad', 'Salario']] = imputer.fit_transform(df[['Edad', 'Salario']])
```

Ventaja: mejor alternativa cuando hay **correlaciones entre variables**. Advertencia de la imputación
simple: no se pierden datos, pero la media/mediana **puede sesgar** los resultados.

**Ejemplo Titanic** (891 pasajeros, 12 variables): se ve el % de nulos por columna, luego se elimina
`deck` y `alive` («>77 % nulos / redundante»), `age` se rellena con la **mediana**, `embarked` con la
**moda**, y se verifica al final que no queden nulos (`df.isnull().sum()[df.isnull().sum() > 0]`).

### 3.3 Valores atípicos (outliers)

**Qué son:** datos que se alejan significativamente del resto y pueden afectar el análisis y los modelos.

**Clasificación** («Clasificación de outliers»):

| Tipo | Ejemplo de la diapo |
|---|---|
| Univariado | edad = 150 años |
| Multivariado | persona de 30 años con salario de director general (normales por separado, anómalo en conjunto) |
| Puntual | observación individual aislada |
| Contextual | 40 °C en invierno |

**Impacto en modelos:** regresión lineal (un solo outlier cambia la pendiente); K-Means (los outliers
«atraen» los centroides y distorsionan los clusters).

**Cómo detectarlos:**

| Método | Regla / código | Notas de la clase |
|---|---|---|
| Visuales («Métodos visuales») | Boxplot (mediana, Q1, Q3, bigotes; puntos fuera = candidatos), histograma (cola larga o picos aislados), scatter con límite marcado, violin plot | El scatter pinta outliers en rojo con una línea en el límite superior |
| **Regla de los cuartiles (IQR)** | `Q1 = quantile(0.25)`, `Q3 = quantile(0.75)`, `IQR = Q3 - Q1`; outlier si `< Q1 - 1.5*IQR` o `> Q3 + 1.5*IQR` | Ejemplo: Edad con 120 y 500 → Q1=24.5, Q3=29.5, IQR=5.0, rango válido [17.0, 37.0], 2 outliers; media con outliers **64.1**, sin ellos **26.3** |
| **Desviación estándar (3σ)** | límites `media ± 3*std` | **Asume distribución normal** |
| **DBSCAN** («Detección de outliers con DBSCAN») | `DBSCAN(eps=1.5, min_samples=5)`; etiqueta **-1 = outlier** | Útil cuando IQR y desviación estándar fallan (formas complejas, alta dimensionalidad). Clasifica puntos centrales, de borde y atípicos. No requiere K. Depende de `eps` y `min_samples`. Se estandariza antes (`StandardScaler`) |
| **LOF** (Local Outlier Factor) | `LocalOutlierFactor(n_neighbors=10, contamination=0.05)`; `-1` = outlier | Mide la densidad relativa frente a los vecinos; no asume normalidad; bueno con densidades variables; sensible a `n_neighbors`; mayor costo |

**Cómo manejarlos** («Métodos para el manejo de outliers»):

| Estrategia | Descripción | Ventaja / desventaja |
|---|---|---|
| Eliminar | Quitar el outlier. **Solo si es claramente un error** (edad = 500) | Fácil y rápido / puede eliminar datos importantes |
| Reemplazo por mediana | Sustituir por valor central robusto; conserva la observación pero cambia su valor | `np.where((x<li)\|(x>ls), mediana, x)` |
| **Winsorización** | Limitar a percentiles (5 y 95); «recorta» extremos; ideal cuando son válidos pero exagerados | Mantiene los datos / modifica algo la distribución |
| **Transformación logarítmica** | `np.log1p(x)` = log(1+x), evita log(0); comprime la escala | Reduce el impacto / **no sirve con negativos** (`log1p` tolera 0) |
| Modelos robustos | Árboles, Random Forest, regresión con pérdida Huber, **RANSAC**, MAD | Ignoran outliers sin eliminarlos / más complejos |

```python
from scipy.stats.mstats import winsorize
df['fare_winsor'] = winsorize(df['fare'], limits=[0.05, 0.05])   # percentil 5 y 95
df['fare_log']    = np.log1p(df['fare'])
```

- Con `limits=[0.14, 0.14]` el 14 % más bajo y el 14 % más alto se reemplazan por los percentiles 14 y 86;
  se guarda en columna **nueva** para preservar la original.
- **Tarea mencionada en la diapo:** el boxplot tras winsorizar «no reduce la cantidad de outliers»;
  *«como tarea ampliar el rango y reducir los outliers»*. **[Suposición]** significa probar otros límites.
- Medir la asimetría antes y después de transformar con `.skew()`: ejemplo salarios, **2.96 → 1.93**
  tras `log1p`. Escala: 0 simétrica · ±0.5 aproximadamente simétrica · ±1 moderada · >±1 importante.
  Frase modelo: *«la variable presentó una marcada asimetría positiva (2.96). Tras la transformación
  logarítmica disminuyó a 1.93, evidenciando una mejora, aunque la distribución continuó presentando
  asimetría positiva.»*
- **RANSAC** («Modelos robustos a outliers»): ignora outliers y ajusta solo con los datos más confiables;
  úsalo cuando hay **pocos** outliers y se quieren conservar todos los datos. Ejemplo con
  `y=[2,4,5,6,8,100,12,...]` comparando `LinearRegression` vs `RANSACRegressor`.

**¿Cuál método utilizar?** (diapositiva con ese título):

- Outliers que son **errores claros** → eliminación.
- Outliers **válidos pero extremos** → winsorización o reemplazo con mediana.
- Datos **sesgados** → transformaciones logarítmicas o normalización.
- **Regla de oro:** *nunca eliminar un outlier sin antes entender su origen.* Puede ser el dato más
  valioso (fraude bancario, fallo de máquina, caso médico raro).

Datasets de ejemplo: Titanic (`fare`, `age`), California Housing (`MedInc`, `HouseAge`, `AveRooms`,
`AveBedrms`, `Population`, `AveOccup`, `Latitude`, `Longitude`; precio objetivo ×100000), listas de
edades y salarios.

### 3.4 Normalización y estandarización (solo lo que aparece de pasada)

No hay diapositivas propias en las fotos. Lo que sí se dijo, en otros temas:

- **`StandardScaler`**: media ≈ 0, desviación ≈ 1. Recomendado cuando las variables tienen unidades o
  escalas distintas. Obligatorio antes de **PCA** (usa varianza), y aconsejado para **KNN** y **SVM**.
- **`MinMaxScaler`**: necesario para **chi²** (exige valores ≥ 0).
- Los **árboles y Random Forest no necesitan** estandarización (dividen por umbrales).
- z-score manual: `(x - x.mean()) / x.std(ddof=1)`.
- Regla clave: el escalador se **ajusta solo con entrenamiento** y luego solo transforma validación y
  prueba (evitar fuga). Dentro de un `Pipeline`, el escalado se reajusta en cada entrenamiento.

### 3.5 Conversión de tipos (solo lo que aparece de pasada)

- `df['fecha'] = pd.to_datetime(df['fecha'])` **antes** de usar el accesor `.dt`.
- En la tarea Bike Sharing se pregunta qué variables son numéricas y cuáles categóricas.

### 3.6 Codificación y discretización de variables categóricas

Lo visible es la **discretización** («Creación de variables categóricas a partir de variables numéricas»):

| Función | Cuándo | Ejemplo de la diapo |
|---|---|---|
| `pd.cut(bins=[...])` | Intervalos definidos por el experto, con significado de negocio | `bins=[0,25,35,100]`, `labels=["Joven","Adulto","Mayor"]`, `right=False`; salario `bins=[0,3000,4000,5000]` → Bajo/Medio/Alto |
| `pd.qcut(q=...)` | Cuantiles con igual cantidad de datos por bin; mejor si la distribución es asimétrica | `pd.qcut(nota_promedio, q=3, labels=["Regular","Bueno","Excelente"], duplicates="drop")` |

- Beneficios: captura relaciones no lineales que los modelos lineales ignoran; más interpretable para
  gente no técnica.
- **Atención (diapo):** discretizar descarta información continua; evaluar si el modelo gana o pierde
  poder predictivo antes de aplicarla definitivamente.
- El código importa `LabelEncoder` y `OrdinalEncoder`, pero en las fotos legibles **no aparece** su uso
  ni `OneHotEncoder`. **[Falta en las fotos]**
- En K-Means («Variable categorica»): `Gender` hay que pasarlo a número (`LabelEncoder` u
  `OneHotEncoder`) y el valor numérico queda **arbitrario** (0 hombre / 1 mujer; «no hay un género
  1.5»), lo que introduce sesgo o ruido; suele no mejorar los clusters, porque ingreso y gasto
  pesan más.

### 3.7 Duplicados (solo en la práctica)

Preguntas de la tarea Bike Sharing (Etapa 2):

- `df.duplicated().sum()`: ¿cuántos duplicados **exactos**?
- ¿Qué diferencia hay entre `keep="first"`, `keep="last"` y `keep=False`?
- ¿Hay registros con la **misma fecha y hora pero valores diferentes**? (duplicado de clave, no exacto)
- ¿Qué estrategia es apropiada para este dataset y por qué?

### 3.8 Creación de nuevas variables (feature engineering)

«El Feature Engineering es posiblemente la habilidad más impactante de un científico de datos»:
codifica conocimiento del dominio en representaciones numéricas. Cuatro categorías:

**(1) Transformaciones matemáticas y estadísticas** («Transformaciones matemáticas y estadísticas»):
abordan distribuciones sesgadas, reducen el efecto de outliers y linealizan relaciones; esenciales en
regresión lineal (supone normalidad de residuos).

| Transformación | Cuándo |
|---|---|
| `np.log1p(x)` | Sesgo positivo (salarios, precios); maneja ceros |
| `np.sqrt(x)` | Suaviza extremos menos que el log; útil en conteos |
| `x**2`, `x**3` / `PolynomialFeatures` | Relaciones cuadráticas |
| Diferencias e interacciones (`A-B`, `A*B`) | Relaciones que los modelos lineales no capturan solos |
| Media/desv. por grupo: `df.groupby('cat')['val'].transform('mean')` | Muy potente en boosting |

Ejemplo de empleados: `log_salario`, `diferencia_notas`, `media_notas`, `nota_max`, `salario_zscore`,
`categoria_edad` con `pd.cut(..., bins=[0,25,35,np.inf])`.

**(2) Discretización:** `pd.cut` / `pd.qcut` (ver 3.6).

**(3) Variables temporales** («Generación de variables basadas en el tiempo»): extraer componentes
aporta estacionalidad, ciclos y tendencias que el algoritmo no deduce de un timestamp crudo.

- Base: `.dt.day/.month/.year/.hour/.weekday` (0 = lunes), `quarter`, `isocalendar().week`, `day_of_year`.
- Binarios: `es_fin_semana` (`weekday >= 5`), `es_festivo` (lista de fechas; la librería `holidays` lo
  automatiza por país; el ejemplo usa feriados de **Bolivia 2023**), `es_laboral = ~fin_semana & ~festivo`.
- **Lags:** `df['lag_1'] = df['ventas'].shift(1)` (el valor de hoy depende del de ayer).
- **Ventanas móviles:** `df['media_7d'] = df['ventas'].rolling(7).mean()`.
- **Codificación cíclica:** `sin(2π·mes/12)` y `cos(2π·mes/12)` para que diciembre no parezca lejos de enero.
- Franja del día: `<6` Madrugada, `<12` Mañana, `<18` Tarde, resto Noche.

**(4) Agrupación y segmentación** («Agrupaciones y segmentaciones»): transforma datos individuales en
features de **contexto de grupo**.

- `pd.cut` por rangos de dominio (alta interpretabilidad).
- `groupby` + `agg` por zona, y devolverlo al dataframe:
  `df.merge(df_agrupado, on='zona', suffixes=('', '_zona'))`.
- **K-Means como feature:** el cluster de cada fila como variable categórica en un modelo supervisado.
- **Target encoding:** reemplazar la categoría por la media del target; efectivo en XGBoost/LightGBM;
  usar validación cruzada.
- **Precaución data leakage:** las estadísticas de grupo se calculan **solo con entrenamiento** y se
  aplican luego a prueba.

**Advertencia general:** demasiadas features sin criterio causan multicolinealidad y sobreajuste; validar
con `SelectKBest` o importancia de features.

### 3.9 Balanceo de datos (clases desbalanceadas)

- Hay desbalance cuando una clase domina numéricamente. Los algoritmos minimizan el error global y
  aprenden a predecir la mayoritaria: alta exactitud, falla en la minoritaria.
- Casos: fraude bancario (~0.1 %), enfermedades raras (un falso negativo es grave), deserción
  estudiantil. **Regla práctica:** si la minoritaria es **< 10–15 %** del total, hay que atenderlo.
- 98 % negativa / 2 % positiva → un modelo que siempre dice «negativo» tiene 98 % de exactitud: la
  **exactitud engaña**.

**Métricas correctas:** Recall = TP/(TP+FN); Precision = TP/(TP+FP); F1 (media armónica); ROC-AUC
(independiente del umbral); matriz de confusión. «Nunca solo con accuracy».

**Tres familias de métodos:**

| Familia | Técnicas | Notas |
|---|---|---|
| **Undersampling** (reducir la mayoritaria) | `RandomUnderSampler`, **Tomek Links** (pares fronterizos), **NearMiss** (mayoritarios cercanos a la minoría) | Ideal con dataset muy grande. Pierde información en datasets pequeños. Solo sobre entrenamiento |
| **Oversampling** (aumentar la minoritaria) | `RandomOverSampler` (duplica: riesgo de sobreajuste, sirve de *baseline*), **SMOTE** (interpola entre k vecinos de la minoría), variantes SMOTE-NC (mixtos), ADASYN (zonas difíciles), BorderlineSMOTE | SMOTE puede crear ruido en zonas de solape y con outliers en la minoría |
| **Pesos de clase** | `class_weight='balanced'` | Alternativa sin tocar los datos |

**Protocolo recomendado:** (1) separar el test **antes** de cualquier balanceo; (2) aplicar SMOTE solo a
entrenamiento, dentro de cada fold de validación cruzada; (3) evaluar con F1-macro, ROC-AUC y matriz
de confusión; usar `imblearn.pipeline.Pipeline` y `StratifiedKFold`.

Código de ejemplo (estructura): `make_classification(n_samples=1000, n_features=20, weights=[0.95], ...)`;
diccionario de estrategias `{"Sin balanceo": None, "UnderSampling": ..., "OverSampling": ..., "SMOTE":
SMOTE(k_neighbors=3)}`; `train_test_split(test_size=0.30, stratify=y, random_state=42)`; entrenar
`RandomForestClassifier(class_weight="balanced")` y comparar F1-Macro, F1-Menor, ROC-AUC y Avg-Precision,
con ranking final por ROC-AUC.

### 3.10 Reducción de dimensionalidad

**Definición** («Reducción de dimensionalidad»): n filas y p columnas; reducir = representar los datos
con menos variables o componentes, conservando la información relevante, simplificando el modelo,
reduciendo ruido, acelerando el entrenamiento y facilitando la visualización. **No garantiza mejorar el
rendimiento**: hay que comprobarlo.

**Dos estrategias** («Dos estrategias»):

| | Selección de variables | Extracción de características |
|---|---|---|
| Qué hace | Conserva algunas columnas originales y descarta otras | Transforma las variables para crear nuevas |
| Ejemplo | Conservar cilindrada y consumo | PCA → CP1 y CP2 |
| Interpretación | Las columnas mantienen su significado | Cada componente combina varias variables |

(Ejemplo del dataset de autos de la agencia ambiental de EE. UU.: de `year, desplazamiento, cilindros,
consumo, co2, ...` se pasa a `desplazamiento, consumo` por selección, o a `x_reducida1, x_reducida2` por
reducción.)

**A) Redundancia por correlación** («Identificación de variables redundantes»): variables muy
correlacionadas aportan información repetida, pueden inducir sobreajuste y enlentecer el entrenamiento.
Método: **eliminación manual basada en correlación**, con `|r| > 0.9` como ejemplo de umbral.

```python
corr_matrix = df.corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
threshold = 0.9
to_drop = []
for i in range(len(corr_matrix.columns)):
    for j in range(i):
        if abs(corr_matrix.iloc[i, j]) > threshold:
            to_drop.append(corr_matrix.columns[i])
df_reduced = df.drop(columns=to_drop)
```

La diapo de «Errores frecuentes» matiza: **no eliminar columnas de forma automática solo porque |r|
supere 0,90**, ni interpretar correlación como causalidad.

**B) PCA** («PCA (Análisis de Componentes Principales)»): técnica de extracción **no supervisada**;
convierte variables numéricas en componentes = combinaciones lineales; la 1.ª explica la mayor varianza,
la 2.ª la mayor varianza restante y es **ortogonal** a la primera, etc. Sirve para comprimir, explorar
patrones y visualizar. **Maximiza varianza, no capacidad predictiva ni separación entre clases.**

- «Estandarizar antes de aplicar PCA»: depende de la escala porque usa varianza; si una variable está en
  miles y otra en décimas, la mayor escala domina.

```python
X_scaled = StandardScaler().fit_transform(X)
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
pca.explained_variance_ratio_.round(3)        # varianza por componente
pca.explained_variance_ratio_.sum().round(3)  # varianza acumulada
```

Iris (150 × 4): con 2 componentes `[0.7296, 0.2285]` → **0.958** acumulada; con 3 `[0.7296, 0.2285, 0.0367]`
→ **0.9948**. Se grafica en 2D por clase y en 3D con `Axes3D`.

**C) Selección de características** («Métodos de selección de características»): objetivo, reducir
ruido, redundancia y complejidad; ayuda a controlar sobreajuste. **No garantiza mejorar siempre la
precisión**; se comprueba con datos de validación. Tres métodos:

1. **Univariada** («Método de selección univariada»): puntúa cada variable por separado contra la
   objetivo y conserva las mejores *k*. **Chi²**: asociación entre características **no negativas** y
   objetivo **categórica**; requiere `MinMaxScaler`; puntaje alto = más asociación, **no causalidad**.
   Se ajusta (`fit`) solo con entrenamiento.

   ```python
   selector = SelectKBest(score_func=chi2, k=2)
   X_train_sel = selector.fit_transform(X_train_scaled, y_train)
   X_test_sel  = selector.transform(X_test_scaled)
   selector.get_support()      # True = variable conservada
   ```

   Iris: `petal width` 22.26 y `petal length` 20.01 (seleccionadas), `sepal length` 8.92 y `sepal width`
   3.38; exactitud **0.9556** con Random Forest.

2. **Recursiva, RFE** («RFE Selección recursiva de características»): entrena con todas, mide
   importancia (`coef_` o `feature_importances_`), elimina la menos importante, re-entrena y repite
   hasta el número pedido. Parámetros: `estimator`, `n_features_to_select`, `step`.
   *Entrenar un Random Forest y ordenar importancias **no es lo mismo** que RFE: RFE re-entrena tras
   cada eliminación.*

   | Estimador | ¿Sirve en RFE? | Nota |
   |---|---|---|
   | Regresión lineal | Sí (`coef_`) | Objetivo continuo; evaluar con MAE, RMSE, R² sobre datos no usados en el ajuste |
   | Regresión logística | Sí | Con `StandardScaler` en un `Pipeline` |
   | SVM `kernel="linear"` | Sí (`coef_`) | Con kernel RBF **no** es compatible; sensible a escala |
   | Árbol de decisión | Sí (`feature_importances_`) | No necesita estandarizar |
   | Random Forest | Sí (`feature_importances_`) | No necesita estandarizar |
   | **KNN** | **No** (sin `coef_` ni importancias) | Alternativa: `SequentialFeatureSelector`; sensible a escala |

   Ejemplo Iris con `make_pipeline(StandardScaler(), RFE(LogisticRegression(max_iter=1000),
   n_features_to_select=2))`: seleccionadas `[F, F, T, T]`, ranking `[3 2 1 1]`.

3. **Basada en modelos:** usa importancias o coeficientes estimados por un modelo (Random Forest,
   regresión logística).

   Además, **SFS** (`SequentialFeatureSelector`, `direction='forward'`, `cv=5`) con KNN en Iris: elige
   `petal length` y `petal width`, exactitud **0.9111**.

**Resumen** (diapositiva «Resumen»):

| Técnica | Qué hace | Ventaja | Precaución |
|---|---|---|---|
| Selección | Conserva columnas originales | Interpretación directa | Puede descartar información útil |
| Correlación | Detecta asociaciones lineales | Rápida y fácil de visualizar | No implica causalidad |
| PCA | Combina variables en componentes | Resume variación y ayuda a visualizar | Pierde interpretación directa |

> **Flujo recomendado (literal de la diapo):** explorar datos → separar conjuntos → ajustar
> preprocesamiento con entrenamiento → transformar → evaluar el modelo.

**«Errores frecuentes»:** (1) no usar PCA directo con escalas muy diferentes sin evaluar estandarización;
(2) no ajustar `StandardScaler` ni PCA con **todo** el conjunto antes de separar train y test (fuga de
información); (3) no interpretar correlación como causalidad; (4) no eliminar columnas automáticamente
solo porque |r| > 0,90; (5) PCA requiere variables numéricas y **es sensible a valores atípicos**;
(6) **documentar** qué variables se eliminaron, cuántos componentes se conservaron y por qué.

### 3.11 Integración y fusión de datos

Fusionar fuentes con pandas: `merge()`, `join()`, `concat()`.

| Método | Uso | Detalle |
|---|---|---|
| `merge()` | Por **columnas comunes** (o índices); equivalente a JOIN de SQL | Eliges la columna con `on=` y el tipo con `how=`. Flexible para estructuras distintas |
| `join()` | Por **índice** | Cuando no hay columna común; usa el índice del DataFrame principal; no se elige columna (salvo con índices) |
| `concat()` | Apilar a lo largo de un eje | `axis=0` filas (vertical), `axis=1` columnas (horizontal) |

Valores de `how` («How en merge»):

| `how` | Resultado |
|---|---|
| `inner` | Solo filas con coincidencia en ambos (intersección) |
| `outer` | Todas las filas de ambos, **NaN** donde no hay coincidencia (unión) |
| `left` | Todas las del izquierdo + coincidentes del derecho |
| `right` | Todas las del derecho + coincidentes del izquierdo |

```python
df1 = pd.DataFrame({'ID': [1, 2, 3], 'Nombre': ['Ana', 'Luis', 'Carlos']})
df2 = pd.DataFrame({'ID': [1, 2, 4], 'Edad': [23, 34, 28]})
pd.merge(df1, df2, on='ID', how='inner')          # filas con ID 1 y 2
df1.join(df2, how='inner')                        # por índice (con índices 1,2,3 y 1,2,4)
pd.concat([df1, df2], axis=0)                     # apila; el índice se repite
```

---

## 4. Práctica en clase: «Bike Sharing Demand»

Dataset de Kaggle / UCI (`hour.csv`, Capital Bikeshare, Washington D.C., 2011-2012, registros por hora).
Se carga desde `https://archive.ics.uci.edu/ml/machine-learning-databases/00275/Bike-Sharing-Dataset.zip`
con `urlopen` + `ZipFile` + `BytesIO`.

Variables: `instant`, `dteday`, `season` (1 invierno … 4 otoño), `yr` (0 = 2011, 1 = 2012), `mnth`, `hr`
(0-23), `holiday`, `weekday` (0-6), `workingday`, `weathersit` (1-4), `temp`, `atemp`, `hum`, `windspeed`
(normalizadas), `casual`, `registered`, `cnt` (= casual + registered).

| Etapa | Preguntas |
|---|---|
| 1. Carga | ¿Cuántos registros y variables? ¿Cuáles numéricas y cuáles categóricas? ¿Hay nulos? ¿Qué información da `cnt`? |
| 2. Duplicados | Duplicados exactos; `keep` first/last/False; misma fecha-hora con valores distintos; estrategia apropiada y por qué |
| 3 y 4 | **No aparecen en las fotos.** **[Suposición]** por el orden del temario podrían ser variables temporales y transformaciones |
| 5. Agrupaciones y agregaciones | Demanda promedio por hora; temporada de mayor demanda; laborables vs no laborables; casuales vs registrados por franja horaria |
| 6. Segmentación de la demanda | Clasificar la demanda en **bajo, medio y alto**; cuántos registros por nivel; características de cada segmento; franjas con más demanda alta |

---

## 5. Parte B: aprendizaje no supervisado y clustering

(Otra presentación; ver sección 1.)

- **Definición:** algoritmos que analizan y encuentran patrones en datos **sin etiquetas** (sin variable
  objetivo); buscan estructuras ocultas, relaciones y patrones.
- **Supervisado vs no supervisado:**

| Característica | Supervisado | No supervisado |
|---|---|---|
| Etiquetas | Requiere (Y) | No usa |
| Objetivo | Predecir un resultado | Explorar la estructura de los datos |
| Salida | Valores continuos o categorías | Clusters, patrones, representaciones |
| Algoritmos | Regresión lineal, árboles, redes | K-means, PCA, DBSCAN, Apriori |
| Aplicaciones | Diagnóstico, precios, texto | Segmentación de clientes, anomalías, compresión |
| Evaluación | Accuracy, RMSE, F1 | Subjetiva o interna (silhouette, varianza explicada) |

- **Tipos de tareas:** clustering, reducción de dimensionalidad, detección de anomalías, reglas de asociación.
- **Algoritmos de clustering:** K-Means (hay que fijar K; minimiza distancia dentro del cluster), DBSCAN
  (densidad; ruido; sin K), Jerárquico/aglomerativo (dendrograma; útil si no se conoce el número de grupos).

**K-Means:** minimiza la **inercia** (suma de distancias cuadradas punto-centroide).
Pasos: (1) elegir K centroides, (2) asignar cada punto al más cercano, (3) recalcular centroides como
promedio, (4) repetir 2-3 hasta que no cambien o se alcance el máximo de iteraciones.

**Inicialización:** K-Means tradicional elige centroides al azar (resultados distintos por ejecución);
**k-means++** elige el primero al azar y los siguientes con probabilidad proporcional a la distancia al
centro más cercano (mejor calidad, converge más rápido).

**Elegir K** («Elección del mejor valor de k»):

- **Método del codo:** inercia vs K; el K óptimo es donde la inercia empieza a bajar lentamente.
- **Índice de Silhouette:** oscila entre -1 y 1; cercano a 1 = grupos bien definidos; cercano a 0 =
  superpuestos; cercano a -1 = posibles asignaciones incorrectas. Se busca el K con mayor silhouette promedio.

```python
for k in range(2, 10):
    model = KMeans(n_clusters=k, init='k-means++', random_state=42).fit(X)
    inertias.append(model.inertia_)
    silhouettes.append(silhouette_score(X, model.labels_))
```

Ejemplo con 3 clusters (`make_blobs`): inercia 277.76, silhouette **0.893**.

**Ejercicio:** *Mall Customer Segmentation* (Kaggle): `CustomerID`, `Gender`, `Age`,
`Annual Income (k$)`, `Spending Score (1-100)`; se carga con `pd.read_csv('Mall_Customers.csv')`,
`StandardScaler`, KMeans y silhouette. K-Means exige variables **numéricas**; para categóricas ver 3.6.

---

## 6. Reglas que la profe repite en varias diapositivas

1. **Separar train/test primero**; ajustar (`fit`) escaladores, selectores, PCA, imputadores, SMOTE y
   estadísticas de grupo **solo con entrenamiento**; luego `transform` en prueba. Motivo: fuga de
   información (*data leakage*).
2. **No eliminar un outlier sin entender su origen.** Elegir según sea error, extremo válido o sesgo.
3. **No basta con la exactitud** en datos desbalanceados: F1, recall, ROC-AUC, matriz de confusión.
4. **Correlación no es causalidad**, y una correlación alta no justifica borrar una columna sola.
5. Reducir variables o discretizar **no garantiza mejorar**: comprobar con validación.
6. **Documentar** qué se eliminó/transformó y por qué.
7. Estandarizar cuando las escalas difieren (PCA, KNN, SVM, K-Means); los árboles no lo necesitan.
8. Guardar la versión transformada en **columna nueva** y preservar la original (winsorización).
9. Verificar al terminar (p. ej. «revisar que ya no haya valores nulos», comparar medias con/sin outliers).

---

## 7. Checklist para cruzar con tus apuntes

> **Ya cruzada** con tus dos notebooks de Colab (`a1` y `anal`): ver
> [`comparacion_con_mis_apuntes.md`](comparacion_con_mis_apuntes.md) (27 ✔, 8 ◐, 6 ✘, 4 solo teoría).
> La columna de abajo queda como plantilla en blanco.

Marca `[x]` lo que ya tienes en tus notebooks.

| # | Técnica / concepto | Diapositiva de referencia | En mis apuntes |
|---|---|---|---|
| 1 | Detectar nulos: `isnull().sum()`, %, mapa | «Identificación de valores faltantes», «Ejemplo» | [ ] |
| 2 | Regla de umbrales 5 / 30 / 50 % | «Regla de umbrales» | [ ] |
| 3 | `dropna` filas y columnas | «Métodos para manejar valores faltantes» | [ ] |
| 4 | Imputar media / mediana / moda | «Imputación de valores faltantes» | [ ] |
| 5 | Imputar con "Desconocido" | «Uso de un valor específico para imputar» | [ ] |
| 6 | Interpolación (numérica y temporal) | «Métodos de manejo de datos numéricos / temporales» | [ ] |
| 7 | `KNNImputer` | «Imputación con modelos predictivos» | [ ] |
| 8 | Ejemplo Titanic (drop `deck`, `age` mediana, `embarked` moda) | «Ejemplo: dataset Titanic» | [ ] |
| 9 | Tipos de outlier (univariado, multivariado, puntual, contextual) | «Clasificación de outliers» | [ ] |
| 10 | Boxplot / histograma / scatter / violin | «Métodos visuales», «Scatter plot» | [ ] |
| 11 | Regla IQR (1.5) | «Regla de los cuartiles (IQR)» | [ ] |
| 12 | Regla 3σ | «Desviación estándar» | [ ] |
| 13 | DBSCAN para outliers (label -1) | «Detección de outliers con DBSCAN» | [ ] |
| 14 | LOF | «LOF» | [ ] |
| 15 | Winsorización (`scipy.stats.mstats.winsorize`) | «Winsorización» | [ ] |
| 16 | `log1p` y asimetría (`skew`) antes/después | «Transformación logarítmica», «Resultado» | [ ] |
| 17 | Reemplazo por mediana | «Ejemplo Mediana y Winsorización» | [ ] |
| 18 | Eliminación de outliers por límites IQR | «Eliminación de outliers» | [ ] |
| 19 | Modelos robustos / RANSAC | «Modelos robustos» | [ ] |
| 20 | Tabla comparativa de estrategias y «¿Cuál método utilizar?» | «Comparación de estrategias» | [ ] |
| 21 | Escalado (`StandardScaler`, `MinMaxScaler`) y su `fit` solo en train | PCA, chi², KNN | [ ] |
| 22 | `pd.to_datetime` antes de `.dt` | «Generación de variables basadas en el tiempo» | [ ] |
| 23 | `pd.cut` vs `pd.qcut` | «Creación de variables categóricas a partir de numéricas» | [ ] |
| 24 | `LabelEncoder` / `OrdinalEncoder` / `OneHot` | «Codificación de variables categóricas» (solo imports) | [ ] |
| 25 | Duplicados exactos y `keep` | «Etapas» (práctica) | [ ] |
| 26 | Duplicados por clave con valores distintos | «Etapas» (práctica) | [ ] |
| 27 | Transformaciones (log1p, sqrt, polinomios, interacciones) | «Transformaciones matemáticas y estadísticas» | [ ] |
| 28 | Features temporales (día, mes, fin de semana, festivo, franja) | «Descripción» + ejemplo | [ ] |
| 29 | Lags y `rolling` | «Generación de variables basadas en el tiempo» | [ ] |
| 30 | Codificación cíclica seno/coseno | ídem | [ ] |
| 31 | `groupby` + `agg` + `merge` de vuelta | «Agrupaciones y segmentaciones» | [ ] |
| 32 | Target encoding | ídem | [ ] |
| 33 | Métricas para desbalance (recall, precision, F1, ROC-AUC) | «Impacto del desbalance» | [ ] |
| 34 | Under / over-sampling, SMOTE, Tomek, NearMiss, `class_weight` | «Métodos de balanceo» | [ ] |
| 35 | Protocolo anti-leakage (split antes de balancear) | «SMOTE vs RandomOverSampler» | [ ] |
| 36 | Matriz de correlación y umbral 0.9 | «Identificación de variables redundantes» | [ ] |
| 37 | Selección vs extracción | «Dos estrategias» | [ ] |
| 38 | PCA con estandarización y `explained_variance_ratio_` | «PCA», «Estandarizar antes de aplicar PCA» | [ ] |
| 39 | Selección univariada `SelectKBest(chi2)` | «Método de selección univariada» | [ ] |
| 40 | RFE y compatibilidad de estimadores | «RFE Selección recursiva» y 5 diapos de modelos | [ ] |
| 41 | `SequentialFeatureSelector` (KNN) | «Vecinos más cercanos KNN» | [ ] |
| 42 | `merge` (`on`, `how`), `join`, `concat` | «Fusión», «How en merge», «concat()» | [ ] |
| 43 | K-Means, k-means++, codo, silhouette | Parte B | [ ] |
| 44 | Ejercicio Mall Customers | «Ejercicio» | [ ] |
| 45 | Errores frecuentes (leakage, PCA con escalas distintas, documentar) | «Errores Frecuentes» | [ ] |

---

## 8. Aplicación al proyecto (propuesta mía, para validar)

Contexto del proyecto: el Anuario Estadístico Judicial 2023 de Bolivia convertido en 12 tablas y una
capa analítica (`data/curated/features/dataset_analitico_curado`), con indicadores de congestión por
materia, tipo de proceso y territorio. **No hay variable objetivo** (es descriptivo/EDA), y la mayoría de
los nulos son **estructurales**, no datos perdidos.

> Qué miré: los títulos de los notebooks 01-13, los módulos `notebooks/modulos/nulos.ipynb` y
> `outliers.ipynb`, y qué funciones de pandas/numpy aparecen en cada notebook. **No leí todas las celdas**;
> confirma cada fila de "Ya está" con tu código antes de darla por cierta.

### 8.1 Lo que el proyecto ya hace y coincide con la clase

| Tema de la clase | Dónde está en el proyecto | Coincidencia |
|---|---|---|
| Faltantes: detectar y clasificar | NB 09 y módulo `nulos`: clasifica cada columna por motivo de ausencia (`estructural_materia`, `estructural_geografico`, ...) y calcula % por columna | Cubre "identificar" y justifica **no imputar**. Contrasta con la regla 5/30/50 %: aquí un nulo es "no aplica" y no "dato perdido". Vale decirlo en el informe |
| Outliers: IQR | NB 11 y módulo `outliers`: Tukey **por estrato** (materia homologada × ámbito), con límite severo (3×IQR) y banderas `es_outlier_*` | Aplica la regla de la clase, mejorada con estratos, y **no elimina filas** (regla de oro) |
| Outliers: winsorización y log | Columnas `tasa_congestion_winsorizada`, `duracion_estimada_winsorizada` (p95) y `log_<columna>` con `log1p` | Coincide con los métodos de la clase; NB 11 además comprueba que el orden se conserva (Spearman) |
| Integración | NB 08: uniones N:1 exigiendo que todas encuentren pareja, unión externa 1:1 que conserva no parejas, `concat` para apilar métricas | Coincide con `merge`/`how`/`concat` |
| Conversión de tipos | NB 04 («Conversión de texto a número») y NB 06 (`to_numeric`) | Coincide |
| Duplicados | NB 05 y 08 (`drop_duplicates`, `duplicated`); `auditoria/claves_repetidas_tipo_proceso.csv`, «Juzgados declarados dos veces» | Coincide con las dos preguntas de la práctica (exactos y misma clave con valores distintos) |
| Feature engineering | NB 10: `tasa_congestion`, clearance rate, duración estimada en días, banderas por proceso | Es creación de variables por razones/ratios; la clase lo llama "diferencias e interacciones" |
| Anti-leakage | `diccionario_analitico.csv` ya tiene la columna `riesgo_leakage` | Alineado con la regla 1 |

### 8.2 Lo que la clase enseñó y el proyecto aún no muestra (candidatos)

Ordenados de más a menos natural para este dataset.

| Candidato | Qué haría | Por qué encaja |
|---|---|---|
| **Asimetría antes/después del log** | `skew()` de `atendidas`, `tasa_congestion`, etc., con la tabla de interpretación (2.96 → 1.93 en la clase) | Barato; da el número que respalda `log1p` y winsorización. El proyecto transforma pero no reporta la asimetría |
| **Segmentar la congestión** | `pd.cut` (umbrales de negocio) o `pd.qcut` en niveles bajo / medio / alto; contar y describir cada nivel | Es calcado de la «Etapa 6» de Bike Sharing |
| **Contexto de grupo** | `groupby(...).transform('mean')` por departamento y materia, y devolver al dataframe (`merge` con `suffixes`) | Es «Agrupaciones y segmentaciones» |
| **Variables temporales de la serie histórica** | En `causas_serie_historica` (2007-2023): `shift` (lag), `rolling`, variación interanual | Es «Generación de variables basadas en el tiempo» |
| **Correlación entre indicadores** | Heatmap de correlación de los indicadores numéricos | Ojo: `atendidas = resueltas + pendientes_fin` es una identidad contable (NB 09, 10), así que |r| alto es esperado. Es el caso de la diapo «no eliminar automáticamente solo porque |r| supere 0,90»: se documenta y **no** se elimina |
| **Outliers multivariados** | LOF o DBSCAN sobre indicadores estandarizados (p. ej. congestión, tasa de resolución, duración) | La clase distingue outlier univariado de multivariado; el proyecto solo hace univariado por estrato |
| **Clustering de territorios/materias** | `StandardScaler` + K-Means; elegir K con codo y silhouette; interpretar los clusters | Es la Parte B. Usar columnas **winsorizadas** (K-Means y PCA son sensibles a outliers) y no meter `materia`/`ámbito` como número arbitrario (la diapo «Variable categorica» advierte de ese sesgo y concluye que suele no aportar; alternativas **[mías]**: clusterizar por separado dentro de cada materia, o usar `OneHotEncoder`) |
| **PCA** | PCA de 2 componentes sobre los indicadores estandarizados para visualizar el clustering; reportar varianza acumulada | «Documentar cuántos componentes se conservaron y por qué» |

### 8.3 Lo que probablemente **no** aplica (y por qué)

| Técnica | Motivo |
|---|---|
| SMOTE, under/over-sampling, métricas de desbalance | No hay clasificación ni clase minoritaria |
| `chi²`, RFE, SFS, selección basada en modelos, target encoding | Requieren una variable objetivo. Solo tendrían sentido si defines una (por ejemplo, congestión alta sí/no), lo que ya es otro alcance |
| `KNNImputer` / interpolación | Los nulos son estructurales; imputar inventaría datos. Solo valdría para algún caso puntual, justificado |
| RANSAC / Huber | No se ajusta ningún modelo de regresión |

### 8.4 Detalle práctico

- `requirements.txt` **no incluye `scikit-learn`**. Si se adopta clustering, PCA, LOF o DBSCAN hay que
  añadirlo (el archivo ya fija versiones exactas de pandas, numpy, scipy, matplotlib).
- Winsorizar: el proyecto lo hace a mano (`winsorizar_estratificado`) y no con `scipy.stats.mstats.winsorize`
  como en la clase. Es equivalente en idea; conviene decir en el informe que es la misma técnica.

---

## 9. Lecturas dudosas y huecos

- **Orden de las diapositivas:** deducido por las fotos (inverso) y por el temario. Las etapas 3 y 4 de la
  práctica Bike Sharing no están fotografiadas.
- **Winsorización:** una diapo usa `limits=[0.05, 0.05]` (percentil 5 y 95) y otra explica
  `limits=[0.14, 0.14]` (percentil 14 y 86); en la de Edad usa `[0.1, 0.1]`. Son ejemplos distintos, no un cambio de criterio.
- **DBSCAN:** en una foto la profe tachó con rojo las ventajas «no requiere especificar el número de
  clusters / detecta clusters de cualquier forma / identifica outliers como ruido». No sé si fue para
  enfatizar o para corregir; lo dejo como ventajas porque otra foto de la misma diapo no tiene marca.
- **Valores numéricos leídos de fotos** (inercia 277.76, silhouette 0.893, asimetría 2.96 y 1.93,
  varianzas del PCA, puntajes chi²): se leen con claridad en al menos una foto, pero verifícalos si
  los vas a citar textualmente.
- **Temas 4, 5, 6 y 7:** sin diapositivas dedicadas en las fotos (ver sección 1).
