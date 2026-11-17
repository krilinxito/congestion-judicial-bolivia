# Guion y preguntas probables: presentación de la ampliación

Presentación: `web/presentacion-ampliacion.html` (menú **Presentar → Presentación 2 · Ampliación**), 35 diapositivas en tres partes.
Para estudiar los conceptos desde cero: `web/guia-ampliacion.html`. Para el detalle técnico: `web/ampliacion.html`.

Cada integrante expone una parte. Los textos están escritos para **decirse en voz alta**: frases cortas, sin leerlas de la pantalla. Las cifras que conviene memorizar están al final.

---

## 0. Reparto y tiempos (unos 20 minutos)

| Quién | Diapositivas | Contenido | Tiempo |
|---|---|---|---|
| Presentador 1 | 1 a 11 | Apertura, de dónde partimos y **Parte 1**: corrección y preprocesamiento | 6 min |
| Presentador 2 | 12 a 22 | **Parte 2**: todas las materias y 17 años | 6 min |
| Presentador 3 | 23 a 35 | **Parte 3**: dónde está el problema, y el cierre (tabla de la clase, reglas, qué cambia, límites, resumen) | 7 min |

Si falta tiempo, se pueden decir en una sola frase las diapositivas 9, 10, 14, 18, 22 y 29, y se mantienen completas las demás.

**Regla para todos:** cuando se dice una cifra, se dice también *qué mide*. Y cuando algo no se puede concluir, se dice. La docente ya mencionó que no veía que se pudiera sacar mucho más del dataset; la mejor respuesta es ser exactos con lo que sí hay y claros con lo que no.

---

## 1. Apertura (diapositivas 1 a 3)

**Diapositiva 1 · Portada**
> «Esta es la segunda presentación. La primera mostró cómo se extrajeron los datos del Anuario y qué encontró el análisis exploratorio. Esta cuenta qué hicimos después, cómo lo hicimos y, en cada paso, qué tema de la clase de preprocesamiento aplica.»

**Diapositiva 2 · Agenda**
> «Tres partes. La primera: una corrección y las técnicas de preprocesamiento. La segunda: pasamos de la mitad de la justicia a toda, y de un año a diecisiete. La tercera: dónde está realmente el problema. En cada diapositiva van a ver qué se hizo, cómo y, cuando corresponde, el tema de la clase. Al final hay una tabla que junta los temas.»

**Diapositiva 3 · De dónde partimos**
> «El primer análisis cubría solo el 47,5 % de las causas, porque en los capítulos 5 y 6 las materias penales no publican causas resueltas. Pero el capítulo 9 del Anuario sí resume el movimiento de todas las materias, para 17 años. Con él cubrimos el 100 %: 738.841 causas atendidas en 2023. Se agregaron cinco notebooks nuevos y una corrección al 10. Todo es archivo nuevo: no se modificó ninguna tabla anterior.»

*Pasar a:* «Empecemos por la corrección.»

---

## 2. Parte 1 · Corrección y preprocesamiento (diapositivas 4 a 11)

**Diapositiva 4 · Portada de la parte**
> «Aquí corregimos un error de cálculo y mostramos las técnicas de preprocesamiento sobre los 1.655 procesos no penales.»

**Diapositiva 5 · Se auditó el denominador de civil** *(tema 1: documentar y verificar)*
> «En civil, el Anuario tiene una columna llamada “readecuadas Ley 439”. Nosotros la habíamos sumado como si fueran causas nuevas. Comprobamos por cuatro caminos independientes que en realidad es el **stock con el que empieza el año**: ocupa el lugar de “pendientes de la gestión anterior” en el cuadro, el CEJA define la tasa de resolución sin contar el stock, coincide con el stock inicial del capítulo 9, y en los 1.655 procesos nunca aparecen juntos el stock publicado y las readecuadas: 1.180 publican el stock y 475 lo tienen como readecuadas.»

*Idea para recordar:* es como contar el saldo inicial de una cuenta como si fuera un depósito.

**Diapositiva 6 · Se corrigió el cálculo** *(tema 1: verificar al terminar)*
> «Al corregirlo, la resolución de civil pasa de 0,69 a 1,01, y la de toda la justicia no penal, de 0,83 a 1,01. Los procesos que acumulan mora bajan de 747 a 608. Las demás materias no cambian porque ya publicaban el stock aparte. Para que no vuelva a pasar, el notebook 10 se detiene si la identidad no cierra en los 1.655 procesos.»

**Diapositiva 7 · No se imputó ningún vacío** *(tema 2: datos faltantes)*
> «La clase enseña a imputar: rellenar con la media, la mediana o con KNN. Aquí no lo hicimos, y lo decidimos a propósito: la mayoría de los vacíos significan “esto no aplica”, no “se perdió el dato”. Por ejemplo, si un proceso no tuvo ingresos, la tasa queda vacía en vez de dividir por cero. La duración solo existe en los 1.122 procesos de 1.655 que resolvieron algo. El año 2023 del CEJA se muestra “sin dato”. Y la columna de 2019 de la tabla 9.1.10 no coincide con las otras dos, hasta 34.671 causas, así que se registra y no se usa.»

**Diapositiva 8 · Asimetría y log1p** *(tema 3: valores atípicos y transformaciones)*
> «Medimos la asimetría, es decir, qué tan larga es la cola de cada distribución. Menos de 0,5 es casi simétrica; más de 1 es fuerte. Con `log1p`, las causas atendidas pasan de 6,5 a 0,54: funciona. Pero en la duración pasa de 16,6 a −1,13: se corrige de más. Es justo lo que dice la clase: transformar no garantiza mejorar, hay que medirlo.»

**Diapositiva 9 · cut y qcut** *(tema 6: discretización)*
> «Usamos las dos formas de cortar en categorías. `cut` con las bandas del CEJA, que son umbrales fijados por una fuente externa. `qcut` en terciles de duración, que reparte la misma cantidad de procesos en cada grupo. Cada celda es el índice contra la base: 1,0 es lo esperado si la materia no importara. Civil aparece de más en la banda crítica, 1,15, aunque su tasa total es 1,01. Coactivo y trabajo se concentran en la duración larga.»

**Diapositiva 10 · Contexto de grupo** *(tema 8: creación de variables)*
> «Un proceso que tarda 300 días no es lento si toda su materia tarda 300. Calculamos la mediana de cada materia y ámbito con `groupby().transform` y comparamos cada proceso con la suya. 198 de 1.122 tardan más del triple; entre los grandes, con 100 o más causas, son 53 de 360.»

**Diapositiva 11 · Mahalanobis** *(tema 3: valores atípicos)*
> «Hasta aquí los extremos eran de una sola variable. Buscamos también combinaciones raras con la distancia de Mahalanobis. Salieron 20 de 1.082 procesos; 14 no tenían ninguna bandera anterior. LOF y DBSCAN, que enseñó la clase, necesitan `scikit-learn`, que el proyecto no usa. Son filas pequeñas: se marcan, no se eliminan. Y decimos con claridad que Mahalanobis supone normalidad, que estos datos no cumplen, así que es una marca para revisar.»

*Pasar a:* «Hasta aquí fue limpiar y preparar. Ahora, ampliar la cobertura.»

### Preguntas probables · Parte 1

**P: ¿Eso no invalida el primer análisis?**
R: Corrigió un número, no el método. El error estaba en cómo se clasificaba una columna de civil. Lo encontramos nosotros al verificar con el PDF, el capítulo 9 y la definición del CEJA, y está documentado con el efecto exacto (civil de 0,69 a 1,01). Las demás materias no cambian. Es la regla del proyecto: si hay dos formas de calcular algo, se hacen las dos.

**P: ¿Cómo saben que las readecuadas son stock y no ingreso? ¿No será una interpretación?**
R: Son cuatro pruebas independientes. Dos son del documento (la posición en el cuadro y el capítulo 9, donde el valor es igual al stock inicial), una es la definición del CEJA, y la cuarta es una propiedad de los datos: en los 1.655 procesos nunca coexisten el stock publicado y las readecuadas. Si fueran ingresos habría procesos con las dos cosas.

**P: ¿Por qué no imputaron los vacíos si lo vimos en clase?**
R: Porque la clase dice que imputar se decide según el motivo de la ausencia, y aquí los vacíos son estructurales: una forma de resolución penal no existe en una causa civil. Rellenarlos con la media inventaría datos y cambiaría las tasas. Cada caso quedó clasificado y registrado, y la duración se calcula solo donde hay resueltas.

**P: ¿Por qué `log1p` y no `log`?**
R: Porque muchas cantidades valen cero y `log(0)` no existe. `log1p(x)` calcula `log(1 + x)`, que sí está definido en cero.

**P: ¿Por qué la duración queda con −1,13 de asimetría? ¿Entonces no sirve el logaritmo?**
R: Sirve para las cantidades (atendidas, resueltas, pendientes), donde baja de fuerte a moderada. En la duración corrige de más porque hay muchos valores muy chicos. Por eso lo medimos y lo decimos: no se transforma a ciegas.

**P: ¿Qué es el índice contra la base?**
R: La participación de una materia en una categoría dividida por la participación de toda la base. Si el 38 % de los procesos son críticos y en civil el 43 %, el índice es 1,15. Un 1,0 es “lo esperado si la materia no importara”.

**P: ¿Por qué terciles en la duración y no umbrales fijos?**
R: Porque para la duración no hay un umbral oficial como el del CEJA para la tasa. Los terciles reparten por igual y permiten comparar materias.

**P: ¿Mahalanobis no supone normalidad? ¿Entonces es inválido?**
R: Lo decimos en la diapositiva. Por eso lo usamos solo como marca para revisar, no como conclusión. La alternativa de la clase (LOF) necesita `scikit-learn`, y preferimos no agregar una dependencia solo para eso. Los 14 casos nuevos son filas pequeñas, no errores.

**P: ¿Por qué no usaron `scikit-learn`?**
R: Para mantener el proyecto reproducible con pocas dependencias (`pandas`, `numpy`, `scipy`, `matplotlib`). El K-Means, el silhouette y el PCA están implementados con `scipy` y `numpy` y verificados (por ejemplo, la varianza del PCA suma 100 % y los componentes son ortogonales). Si se necesitara LOF o DBSCAN, se agregaría.

**P: ¿Qué es “mora” en “procesos que acumulan mora”?**
R: Procesos con tasa de resolución menor que 1: entra más de lo que sale.

---

## 3. Parte 2 · Todas las materias y 17 años (diapositivas 12 a 22)

**Diapositiva 12 · Portada de la parte**
> «Ahora usamos el capítulo 9, el resumen de todo el sistema, y construimos la serie desde 2007.»

**Diapositiva 13 · Integración del capítulo 9** *(tema 11: integración y fusión)*
> «Calculamos los indicadores del CEJA para 13 materias y 9 departamentos. Antes de interpretar, verificamos cada cuadro con otro camino. Las dos identidades de cada fila cierran en 68 de 72; las 4 restantes difieren en una causa y ya estaban registradas. Capital más provincia da el nacional con cero diferencias, en 15 materias y 5 columnas. Y el total del cuadro 9.1.9 es igual al de la serie 9.1.12.»

**Diapositiva 14 · Doble conteo de lo penal** *(tema 7: duplicados)*
> «Tres cuidados con lo penal. Uno: el Anuario intercambia los rótulos de anticorrupción y violencia contra la mujer entre cuadros; como no se puede saber cuál es cuál, los sumamos en pares y el resultado no depende de la etiqueta. Dos: ejecución penal, que según el propio Anuario, en la página 673, “no resuelve”, se muestra aparte y no entra en los rankings. Tres: instrucción, sentencia y tribunales son etapas distintas; una misma causa puede aparecer en más de una.»

**Diapositiva 15 · Resultado por materia**
> «Con tasa óptima solo están coactivo fiscal, familia y civil. Ojo con coactivo: resuelve más de lo que recibe, pero su stock es tan grande que tardaría 1.446 días en vaciarse. El flujo y el stock miden cosas distintas. Y los tribunales de sentencia penal tardarían 1.953 días, más de cinco años: la mayor duración entre las materias comparables.»

**Diapositiva 16 · El stock en 2023**
> «Dentro de 2023, el stock subió 19.114 causas, según las tablas. La justicia no penal lo redujo en 1.379; el aumento está en lo penal, 13.134, y en ejecución penal, 7.359. Aclaro de una vez que esta es una variación *dentro del año*; en un minuto muestro por qué no se debe leer como un atraso neto del sistema.»

**Diapositiva 17 · Por departamento**
> «Solo Potosí tiene resolución óptima, 1,02. Beni es el único en nivel crítico, 0,85, y su stock creció 18,9 %. Santa Cruz suma 7.627 causas dentro del año, el mayor aumento absoluto, y concentra el 33 % del stock nacional.»

**Diapositiva 18 · Brecha de capacidad** *(tema 8: creación de variables)*
> «Es aritmética, no un modelo. Para que el stock deje de crecer harían falta 19.115 resoluciones más al año, un 5 % más que hoy. Para vaciarlo en tres años, 137.951 más, un 36 %. Es un orden de magnitud, no una proyección.»

**Diapositiva 19 · La serie 2007-2023** *(tema 8: variables temporales)*
> «Armamos la serie con tres ámbitos y calculamos con `pct_change` la variación interanual, con `shift` el rezago y con `rolling(3)` la media móvil. La resolución pasa de 0,74 en 2007 a alrededor de 1 desde 2015, y 0,95 en 2023. Las ingresadas saltan más de 15 % en 2013, 2016, 2020 y 2021; 2020 y 2021 son la pandemia y el rebote. Desde 2015 la resolución no tiene memoria entre años: oscila alrededor de 1.»

**Diapositiva 20 · El stock no se conserva** *(tema 1: documentar sin corregir)*
> «Este es el hallazgo sobre la fuente. Si hablamos de una cuenta, el saldo final de diciembre debería ser el saldo inicial de enero. En el Anuario no lo es: la apertura es menor que el cierre previo en 15 de 16 transiciones. Por ejemplo, el cierre de 2022 fue 364.680 y la apertura de 2023, 337.394: faltan 27.286 causas. No sabemos por qué; depuración, archivo o cambios de registro son solo hipótesis. No lo corregimos ni lo interpolamos. Consecuencia: el stock no se puede reconstruir sumando flujos, y por eso los 19.114 de hace un momento son una variación dentro del año.»

**Diapositiva 21 · Comparación con el CEJA**
> «Calculamos las tasas con las fórmulas del CEJA y las comparamos con las que ellos publican para 2018-2022. De 2019 a 2022 casi coinciden, con diferencias máximas de 0,02 en resolución y 0,10 en congestión. Es como comparar nuestra calculadora con la de un laboratorio. 2018 difiere mucho y no lo podemos explicar con estos datos. Y 2023, que el CEJA no tiene, ahora tiene cifra: resolución 0,95, congestión 1,93.»

**Diapositiva 22 · Resueltas por materia**
> «Las cinco materias no penales resuelven más en 2023 que en 2021, desde +5 % en familia hasta +39 % en trabajo. La excepción son los tribunales de sentencia penal: de 3.110 resueltas en 2020 a 1.811 en 2023, −33 % desde 2021. No usamos 2019 porque esa columna no cierra entre cuadros.»

*Pasar a:* «Con todo esto en mano, la pregunta es: ¿dónde está el problema?»

### Preguntas probables · Parte 2

**P: Si el Anuario no cierra consigo mismo, ¿por qué confían en el capítulo 9?**
R: Porque no confiamos a ciegas: lo verificamos. Las identidades de cada fila cierran en 68 de 72 y las 4 restantes difieren en una causa; capital + provincia = nacional con cero diferencias; y el mismo total sale de otro cuadro. Donde no cierra, lo registramos (son 117 discrepancias en total, todas listadas con página) y no lo corregimos.

**P: El Anuario dice que se resolvió el 52,5 % de lo atendido. ¿Por qué ustedes dicen 0,95?**
R: Son dos medidas distintas. El 52,5 % del Anuario (p. 673) es resueltas ÷ atendidas. Nuestro 0,95 es la tasa de resolución del CEJA: resueltas ÷ ingresadas del año. Con nuestros datos, resueltas ÷ atendidas da 51,7 %: la misma idea, a menos de un punto del Anuario. No sabemos exactamente a qué se debe esa diferencia y no la forzamos.

**P: ¿Por qué ejecución penal “no resuelve” si aparece con 9.068 resueltas?**
R: El Anuario publica números en esa fila pero aclara en la página 673 que los juzgados de ejecución penal no resuelven. Por prudencia la mostramos aparte y no la incluimos en rankings ni en comparaciones de duración. Qué cuenta exactamente esa cifra, no lo sabemos con seguridad, y preferimos decirlo.

**P: ¿Por qué suman anticorrupción y violencia? ¿No pierden información?**
R: Pierden la distinción entre las dos, pero es la única decisión honesta: el Anuario intercambia los rótulos entre cuadros y no hay forma de saber cuál es cuál. La suma por pares da el mismo resultado sin importar cuál es cuál. La auditoría de materias lo explica.

**P: ¿Los 19.114 son un atraso real del sistema?**
R: No exactamente. Son la diferencia entre los saldos de cierre e inicio del mismo año en el cuadro 9.1.9. Entre los cierres de 2022 y 2023 el stock publicado bajó de 364.680 a 356.508. Por eso lo presentamos como “variación dentro del año, según las tablas” y mostramos aparte que el stock no se conserva entre años.

**P: ¿Por qué no corrigen o explican la diferencia de 27.286 causas?**
R: Porque no hay base para hacerlo. No sabemos si fueron depuraciones, archivos o cambios de registro, y corregir sería inventar. Lo documentamos como límite.

**P: ¿Cómo se calcula la duración? ¿Es un tiempo real?**
R: No es un tiempo medido: no hay fechas por causa. Es pendientes al cierre ÷ resueltas × 365: los días que tardaría en vaciarse el stock si se resolviera al ritmo actual y no entrara nada. El CEJA no publica este indicador; es un estimador propio.

**P: Los tribunales de sentencia penal son pocas causas, ¿no distorsiona?**
R: Sí, es una base pequeña: 2.083 ingresadas y 1.811 resueltas, con 9.688 pendientes. Además cuentan etapas, no expedientes. Lo señalamos y lo presentamos como el cuello de botella más claro, no como una conclusión definitiva.

**P: ¿Por qué 2018 no coincide con el CEJA?**
R: No lo sabemos. Puede ser otra fuente o una revisión posterior; con estos datos no se puede explicar, así que lo decimos y no lo forzamos. Desde 2019 coinciden.

**P: ¿La brecha de capacidad es una recomendación?**
R: No, es aritmética: `max(0, ingresadas − resueltas)` más stock ÷ 3. Es un orden de magnitud y está limitada por la no conservación del stock.

**P: ¿Qué es `pct_change`, `shift`, `rolling`?**
R: `pct_change` calcula el cambio porcentual respecto al año anterior; `shift` mueve la serie un año para comparar con el anterior; `rolling(3)` hace un promedio móvil de tres años que suaviza los saltos.

**P: ¿Por qué no se usa seno/coseno si es una serie de tiempo?**
R: Esa codificación sirve para variables cíclicas como hora, día o mes. Nuestra serie es anual, no hay ciclo dentro del dato.

**P: ¿Las resueltas por materia de 2019 por qué no?**
R: Porque la columna de 2019 de la tabla 9.1.10 no coincide con la suma de las otras dos (hasta 34.671 causas de diferencia por materia), mientras que 2020 a 2023 cierran con diferencia máxima de 9. Se registra en un CSV y no se usa.

---

## 4. Parte 3 · Dónde está el problema (diapositivas 23 a 30)

**Diapositiva 23 · Portada de la parte**
> «Hasta aquí vimos cuánto. Ahora vemos dónde.»

**Diapositiva 24 · Concentración del rezago** *(tema 3: extremos válidos)*
> «Ordenamos los 1.655 procesos de más a menos pendientes y acumulamos. El 6 % de los procesos, 100 de 1.655, reúne el 73 % del rezago. Hay 566 procesos que no tienen causas pendientes. Diez tipos de proceso, de 87, reúnen el 65,7 %: asistencia familiar, ordinario e infracción a leyes sociales. Y La Paz y Santa Cruz concentran el 66,6 %. Estos extremos son válidos, no errores: no se eliminan.»

**Diapositiva 25 · Qué explica la duración** *(tema 6: codificación de categóricas)*
> «Medimos qué parte de las diferencias de duración explica cada factor, con el R² ajustado. Las categorías entran como indicadoras, *one-hot* hecho a mano, no como números del 1 al 87, que es el error que advierte la clase. Resultado: ser capital o provincia explica menos del 1 %. El departamento, entre 10 y 14 %. La materia, entre 5 y 39 % según el peso. Y lo que más explica es el tipo de proceso: 21 % sin pesos y hasta 57 % ponderado. Es descripción, no causalidad.»

**Diapositiva 26 · K-Means** *(parte B: clustering; tema 4: estandarización)*
> «Probamos si los procesos forman grupos naturales. Estandarizamos cuatro variables, usamos K-Means con *k-means++* de 2 a 7 grupos y medimos el silhouette: cerca de 0,5 o más hay grupos claros. El mejor fue 0,425, con tres grupos: una masa normal y dos minorías extremas. No lo adoptamos como resultado, porque no hay grupos naturales. Mostrar lo que no funcionó también es un resultado.»

**Diapositiva 27 · Carga por personal** *(tema 11: integración y fusión)*
> «Cruzamos los puestos de personal y los órganos de cada departamento con el movimiento de causas. Un ítem es un puesto presupuestado, y medimos por puesto ocupado, sin vacantes. La carga varía 2,6 veces: de 33 causas nuevas por puesto en Pando a 85 en Santa Cruz. El personal sigue a la demanda: los departamentos con más causas tienen más puestos.»

**Diapositiva 28 · Dos clases de problema**
> «Hay dos tipos de problema. Saturación en Santa Cruz: la mayor carga por puesto, la remuneración por causa resuelta más baja del país y 422 días para vaciar su stock. Y bajo rendimiento con carga ligera en Beni: recibe 38 causas por puesto, resuelve 33 y es el único con tasa crítica, 0,85. No son el mismo problema ni se arreglan igual. Y el límite, en voz alta: de 15 relaciones probadas entre recursos y resultados, ninguna es significativa. Con 9 departamentos y un año, eso describe, no prueba.»

**Diapositiva 29 · Correlación** *(tema 10)*
> «Calculamos la correlación entre ocho indicadores. 7 de 28 pares pasan de 0,90, y 4 de esos son identidades contables, como atendidas igual a resueltas más pendientes: es esperable. Los otros tres, congestión, duración y pendencia, se construyen con fórmulas emparentadas. La clase dice que una correlación alta no es motivo para borrar una columna, y no borramos ninguna: la capa curada sigue con sus 118.»

**Diapositiva 30 · PCA** *(tema 10 con tema 4)*
> «Con PCA sobre variables estandarizadas, dos componentes explican el 79,6 % y tres el 97,8 %. Al dibujar los procesos en los dos primeros se ve una nube continua, sin grupos separados, que coincide con el silhouette bajo.»

*Pasar a:* «Cerramos juntando todo.»

### Preguntas probables · Parte 3

**P: ¿Qué aporta este trabajo, si no se puede sacar mucho más del dataset?** *(la pregunta más importante)*
R: Aporta cuatro cosas. Cobertura: de 47,5 % al 100 % de las causas y de un año a 17. Rigor: un error corregido, documentado y con su efecto. Un hallazgo sobre la fuente: el stock publicado no se conserva entre años, 15 de 16 transiciones. Y hallazgos acotados: el rezago está concentrado (6 % de los procesos reúne el 73 %), lo que más explica la duración es el tipo de proceso y no ser capital o provincia, los tribunales de sentencia penal son el cuello de botella más claro y hay dos clases de problema distintas entre departamentos. Y decimos con claridad dónde termina lo que los datos permiten: un año, sin fechas por causa, sin población.

**P: ¿Por qué el tipo de proceso explica tanto? Con 85 categorías, ¿no es sobreajuste?**
R: Es una buena objeción. Por eso usamos el R² *ajustado*, que descuenta el número de categorías. Aun así, con categorías pequeñas conviene leerlo como descripción, no como un modelo para predecir. En la lectura ponderada por volumen, donde pesan los procesos grandes, sigue siendo el factor que más explica.

**P: ¿Por qué hay 1.122 procesos en la descomposición y 1.082 en el K-Means y en PCA?**
R: La duración existe solo en los procesos que resolvieron algo (1.122 de 1.655). Para el agrupamiento, el PCA y Mahalanobis se necesitan además todas las demás variables sin vacío, y quedan 1.082.

**P: ¿Por qué el K-Means no sirvió y aun así lo muestran?**
R: Porque la ruta del proyecto lo sugería y era razonable probarlo. El silhouette de 0,425 está por debajo de 0,5, así que no hay grupos claros. Mostrar el resultado negativo evita que alguien lo proponga después como pendiente.

**P: ¿Qué es el silhouette?**
R: Va de −1 a 1 y mide qué tan bien separados están los grupos: cuánto se parece cada punto a los de su grupo frente a los del grupo más cercano. Cerca de 0,5 o más indica grupos claros.

**P: ¿Por qué no hicieron un modelo predictivo?**
R: No hay variable objetivo que justifique uno, y hay 47 columnas marcadas con riesgo de *leakage* en el diccionario analítico. Este proyecto es descriptivo.

**P: ¿Más personal significa más resoluciones?**
R: No lo podemos afirmar. Probamos 15 relaciones con Spearman y ninguna es significativa. Con solo 9 departamentos eso no prueba que no haya relación, solo que estos datos no la detectan.

**P: ¿Por qué Beni resuelve menos con menos carga? ¿Cuál es la causa?**
R: No lo sabemos. Los datos muestran que no es un problema de volumen ni de vacantes (solo 2,4 % de vacantes). Podría ser la mezcla de materias, la geografía o la organización, pero eso no se puede decir con este dataset.

**P: ¿Qué es un ítem?**
R: Un puesto de trabajo presupuestado, no una persona. Incluye personal administrativo y de apoyo, y no se sabe cuántos son jueces. Por eso medimos por puesto ocupado, sin vacantes.

**P: ¿Por qué no usaron población para tasas por habitante?**
R: Porque falta la tabla oficial completa del Censo 2024 del INE. En la prensa hay cifras para 6 de los 9 departamentos y son preliminares, así que no las usamos. Es el siguiente paso.

**P: La remuneración, ¿en qué moneda y de qué período?**
R: El Anuario publica la remuneración mensual del personal y solo del personal, no el presupuesto total. Por eso la usamos como índice contra el promedio nacional (1,0), sin anualizar ni asignar moneda.

**P: ¿Por qué 7 de 28 correlaciones altas no les preocupan?**
R: Porque 4 son identidades contables, esperables, y los otros 3 miden lo mismo con fórmulas parecidas. La clase dice que una correlación alta no justifica borrar una columna, y que correlación no es causalidad.

**P: ¿Qué significan los componentes del PCA?**
R: PC1 contrapone duración y pendencia a la tasa de resolución; PC2 es sobre todo volumen. Dos componentes conservan casi el 80 % de la información de las cuatro variables.

---

## 5. Cierre (diapositivas 31 a 35)

**Diapositiva 31 · Dónde se aplicó cada tema de la clase**
> «Esta tabla junta todo. De los once temas más el clustering, ocho se aplicaron, tres en parte y uno no aplica. En parte: estandarización, porque no hay train/test al no haber modelo predictivo; conversión de tipos, que se heredó de los notebooks 04 y 06; y duplicados, cuya depuración se hizo en la Fase 2. No aplica el balanceo de clases, porque no hay clasificación. Y chi², RFE y SFS necesitan una variable objetivo: este proyecto es descriptivo.»

**Diapositiva 32 · Reglas de la profe**
> «Y las reglas que se repiten en clase: ninguna fila eliminada, ninguna correlación alta usada para borrar, transformaciones medidas antes de adoptarlas, todo en archivos nuevos preservando los originales, y el notebook 13 con 12 bloques de verificación.»

**Diapositiva 33 · Qué cambia**
> «Qué cambia respecto al primer análisis: civil resuelve 1,01, no 0,69; cubrimos el 100 % de las causas; con lo penal, los tribunales de sentencia tardarían 1.953 días contra 1.446 de coactivo; la justicia no penal bajó su stock y el aumento dentro del año está en lo penal; la geografía que importa es el departamento, no capital contra provincia; y Bolivia 2023 ya tiene cifra con las fórmulas del CEJA.»

**Diapositiva 34 · Límites**
> «Lo que no podemos decir. Los indicadores penales son de flujo y cuentan etapas. El stock no se conserva entre años. Con 9 departamentos y un año, las relaciones con recursos no son concluyentes. Y medimos celeridad, no calidad. Lo que sigue: la población del INE, indicadores propios para penal, y averiguar por qué el stock no se conserva.»

**Diapositiva 35 · Resumen**
> «Resumen: más cobertura, un error corregido y el problema mejor ubicado. Gracias; quedamos atentos a las preguntas.»

### Preguntas generales

**P: ¿Cómo se pueden reproducir los resultados?**
R: Los notebooks se ejecutan en orden (`01 … 18`, luego `13`), están en el repositorio y en la página “Cómo reproducir” de la web. Desde el notebook 08 no hace falta el PDF. El notebook 13 verifica 12 bloques con `assert`: si algo no se cumple, se detiene.

**P: ¿Dónde está documentado todo?**
R: En la web del proyecto: la guía de la ampliación (paso a paso, sin tecnicismos), la página técnica de la ampliación y las páginas de decisiones, límites y validación.

**P: ¿Por qué algunas técnicas de la clase no se usaron (SMOTE, chi², RFE, SFS, train/test)?**
R: Todas necesitan una variable objetivo y este proyecto es descriptivo. Lo que sí tomamos de la clase es el criterio: no alterar el dato original sin entender su origen, no imputar lo que no existe, preservar la columna original y documentar cada decisión.

**P: ¿Qué harían con más tiempo?**
R: Tres cosas. La población oficial del INE para medir por 100.000 habitantes. Indicadores propios para las materias penales, con sobreseimientos y salidas alternativas. Y rastrear por qué el stock publicado no se conserva entre años.

**P: ¿Cuál es el hallazgo más importante?**
R: Si tuviera que elegir uno: el rezago está concentrado y lo explica el tipo de proceso, no ser capital o provincia. Y como hallazgo sobre la fuente: el stock publicado no se conserva entre años. El primero orienta dónde mirar; el segundo, cuánto confiar en las series.

---

## 6. Frases que conviene evitar

| No decir | Decir en su lugar |
|---|---|
| «La justicia penal funciona peor» | «Los tribunales de sentencia penal tardarían 1.953 días; cuentan etapas y es una base pequeña» |
| «El stock subió 19.114 causas» (a secas) | «Según las tablas, el stock subió 19.114 dentro de 2023; entre cierres el stock publicado no se conserva» |
| «Más personal resuelve más» | «No se puede afirmar: 15 relaciones probadas, ninguna significativa, con 9 departamentos» |
| «El tipo de proceso causa la demora» | «El tipo de proceso es lo que más explica las diferencias; es descripción, no causalidad» |
| «Beni es peor» | «Beni resuelve menos de lo que ingresa con carga ligera por puesto; no sabemos la causa» |
| «Tuvimos un error en los datos del Anuario» (sobre readecuadas) | «Teníamos mal clasificada una columna de civil; se corrigió y el efecto está documentado» |
| «Los datos del Anuario están mal» | «El Anuario no cierra consigo mismo en 117 casos y el stock no se conserva entre años; lo registramos sin corregirlo» |

---

## 7. Cifras para memorizar

| Dato | Valor |
|---|---|
| Cobertura | 47,5 % → 100 % (738.841 causas atendidas en 2023), 17 años |
| Civil, tasa de resolución | 0,69 → **1,01** |
| Total no penal | 0,83 → **1,01**; mora 747 → 608 |
| Readecuadas | 1.180 procesos con stock publicado, 475 con readecuadas, 1.655 en total |
| Bolivia 2023 (fórmulas del CEJA) | resolución **0,95**, congestión **1,93** |
| Comparación con el CEJA | 2019-2022: diferencia máxima 0,02 y 0,10; 2018 difiere (0,80 contra 1,00) |
| Stock dentro de 2023 | +19.114 (no penal −1.379, penal +13.134, ejecución +7.359) |
| Stock entre años | apertura < cierre previo en **15 de 16**; 2022→2023: −27.286; suma 2008-2023: −546.074 |
| Tribunales de sentencia penal | 1.953 días; resueltas 3.110 (2020) → 1.811 (2023) |
| Coactivo / civil, días | 1.446 / 162 |
| Concentración | 6 % de los procesos = 73 % del rezago; 566 de 1.655 sin pendientes; 10 de 87 tipos = 65,7 % |
| Qué explica la duración | ámbito < 1 %; departamento 10-14 %; materia 5-39 %; **tipo de proceso 21-57 %** |
| K-Means | mejor silhouette 0,425 (k = 3): se descarta |
| Asimetría | atendidas 6,5 → 0,54; duración 16,6 → −1,13 |
| Contexto de grupo | 198 de 1.122 procesos > 3 × mediana; 53 de 360 entre los grandes |
| Mahalanobis | 20 de 1.082 (1,8 %); 6 con bandera previa, 14 solo en conjunto |
| Correlación / PCA | 7 de 28 pares > 0,90 (4 contables); PCA 79,6 % (2) y 97,8 % (3) |
| Personal | 6.766 ítems (316 vacantes); carga 33 (Pando) a 85 (Santa Cruz) = 2,6 veces; 0 de 15 relaciones significativas |
| Verificación | notebook 13: 12 bloques; 117 discrepancias del Anuario registradas |
| Clase | 11 temas + clustering: 8 aplicados, 3 en parte, 1 no aplica |

## 8. Dónde mirar si preguntan algo que no está aquí

- Conceptos jurídicos y las cinco cantidades: `web/conceptos.html`
- Por qué y cómo se corrigieron las readecuadas: `web/decisiones.html#las-readecuadas`
- Discrepancias del Anuario: `web/validacion.html`
- Auditorías (rótulos intercambiados, doble conteo): `web/auditorias.html`
- Límites: `web/limites.html`
- Todas las preguntas frecuentes con respuesta: `web/preguntas.html`
- Los archivos de cada cifra: `data/curated/eda/` (el nombre del archivo está en `web/ampliacion.html`, sección «Archivos nuevos»)
