# Temporada 2: Más modelos

> Los notebooks están escritos y probados en una réplica de Colab; los videos están por grabarse. Hay que comprobar en Colab y en Excel reales, y las referencias legales del 2.8 y el 2.9 están por verificar.

Ya sabes pronosticar y clasificar, y sabes desconfiar de un buen número. Ahora vas a sumar modelos que siguen reglas, agrupan clientes y leen mensajes, y a preguntarte cuándo un modelo no se debe usar.

| # | Episodio | Pregunta de la empresa | Lo que ya sabes en Excel | Se aprende |
|---|---|---|---|---|
| 2.1 | [Árbol de decisión: tu `=SI()` anidado, pero aprendido](01-arbol-de-decision/) | ¿Qué despachos tienen más riesgo de llegar tarde? | `=SI()` (`IF`) anidado | Árbol pequeño, leer cada hoja como un porcentaje y ordenar por riesgo |
| 2.2 | [Cuando el árbol se aprende todo](02-cuando-el-arbol-se-aprende-todo/) | ¿Qué tan grande dejamos el árbol? | Una regla con mil excepciones | Vigilar el 10 % de cada día, profundidad, sobreajuste y grupo de validación |
| 2.3 | [Random Forest: ¿vale la pena?](03-random-forest/) | ¿Muchos árboles son mejores que uno? | Promediar la opinión de varios colegas | Bosque, qué dice y qué no dice la importancia, y cuándo no compensa |
| 2.4 | [Series de tiempo: día de la semana y feriados](04-series-de-tiempo/) | ¿Cuánto venderemos cada día? | Promedio por día de la semana y el índice del 1.5 | Patrones, una regla con índice como línea base, y una regresión con calendario y tendencia |
| 2.5 | [Una sola prueba puede engañar](05-una-sola-prueba-puede-enganar/) | ¿Ese pronóstico es bueno o tuvo suerte? | Probar la fórmula en varios meses | Validación por ventanas |
| 2.6 | [Modelos que leen: clasificar tickets](06-clasificar-tickets/) | ¿A qué área va cada mensaje? | `=CONTAR.SI()` (`COUNTIF`) con comodines | Contar palabras, clasificar texto, y qué pasa con palabras nuevas |
| 2.7 | [Segmentación de clientes](07-segmentacion-de-clientes/) | ¿Qué grupos de clientes tenemos? | Tabla dinámica con rangos hechos a mano | k-means, escala de las columnas, y por qué los grupos son una decisión |
| 2.8 | [Ética I: auditar una decisión](08-etica-auditar-una-decision/) | ¿Nuestros procesos tratan igual a todos? | Una tabla dinámica por grupo y cargo | Comparar tasas por cargo, indicadores indirectos, y no concluir con pocos casos |
| 2.9 | [Ética II: el modelo que aprendió a discriminar](09-etica-el-modelo-que-discrimina/) | ¿Dejamos que un modelo filtre postulantes? | Lo auditado en el 2.8 | Qué hace un modelo con una etiqueta sesgada, y qué hacer en su lugar |
| 2.10 | [Miniproyecto: el reporte de la mañana](10-miniproyecto-reporte-de-la-manana/) | ¿Qué vigilamos hoy? | El reporte del 1.9 | Reúne pronóstico, despachos y tickets con funciones listas, y lo comprueba en diciembre |

La segmentación va después de los tickets porque no alimenta al hilo de despachos, series y miniproyecto. El aviso del 1.7 ya anunció un episodio de ética.

## Por qué así

### Tres archivos nuevos

- **`despachos.csv`** (41,837 filas): las reglas de tardanza solo actúan en combinación, y esto favorece a un árbol.
- **`tickets.csv`** (3,600 mensajes): el caso de texto.
- **`postulaciones.csv`** (3,200 filas): el caso de ética.

Pruebas con huellas comprueban que no cambia ningún archivo de las temporadas anteriores, incluido `creditos.csv`.

**Cambio frente al plan inicial:** el plan decía "RRHH con rotación", y pasó a postulaciones. Una plantilla creíble para estas ventas da muy pocas renuncias, y postular da miles de casos sin predecir qué hará un empleado concreto. Aun así, 3,200 postulaciones son muchas para esta empresa. El 2.8 lo avisa.

### El árbol gana aquí, pero poco, y no siempre

**Medida nueva, que se presenta como tal en el 2.2:** si cada día solo se pueden vigilar 10 de cada 100 despachos, ¿qué parte de los tardíos se encuentra? Se decide día por día con los pedidos de ese día, sin mirar el futuro. Los empates se resuelven al azar, con semilla fija.

**Separación:** se entrena con 2024, se elige la profundidad con el primer semestre de 2025, se entrena de nuevo con todo eso, y se prueba con el segundo semestre, una sola vez. Así, la campaña de julio y la de diciembre están en la prueba, y la de 2024 en el entrenamiento.

| Vigilando el 10 % de cada día | Tardíos encontrados, jul-dic 2025 | Con 6 semillas más |
|---|---|---|
| Al azar | 10 % | |
| Regresión, con mes y día como categorías, como enseñó el 1.5 | 23 % | 20 % a 23 % |
| Árbol de profundidad 3, el que se puede leer | 26 % | 24 % a 27 % |
| Árbol de profundidad 6, la elegida con validación | 29 % | 27 % a 30 % |
| Árbol sin límite (99.6 % de aciertos en entrenamiento) | 20 % | |
| Bosque de 200 árboles, con al menos 20 casos por hoja, un valor fijo sin ajustar | 29 % | 26 % a 30 % |
| Regresión a la que se le dan a mano las tres reglas | 30 % | 28 % a 32 % |

Lo que se puede afirmar:

- **El árbol de profundidad 6 le gana a la regresión por 4 a 9 puntos** en las 7 semillas, porque se programaron reglas combinadas. No hay mucho más: conociendo las probabilidades reales del generador, se llega a unos 32 %.
- **La regresión con las reglas escritas a mano alcanza al árbol.** Requiere conocerlas. Lo que el árbol ahorra es tener que adivinarlas.
- **El árbol que se lee (8 hojas) se queda cerca del grande.** Por eso el 2.1 usa este.
- **Cada hoja responde "a tiempo"**, porque en ninguna pasa del 50 %. La hoja de terceros en sábado llega a 48 % de tardíos y la más común a 4 %. El 2.1 enseña a leer el porcentaje de cada hoja como orden de prioridad, no el sí o no.
- **La profundidad elegida es casi un empate:** cambia entre 5 y 8 según la semilla.
- **Bosque y árbol empatan en la práctica,** y el bosque no se puede leer.
- **La importancia no dice cómo actúa una variable.** El bosque da cerca de 0.3 a `dia`, 0.2 a `transportista_Tercero`, y unos 0.15 a `mes` y a `distancia_km`. El `dia` solo importa con terceros y la distancia casi solo con lluvia en Cusco. Eso no aparece en esa lista.
- **El 91 % de aciertos vuelve a no decir nada:** es lo que se logra diciendo que nada llega tarde. Se recuerda en el 2.2.

**En créditos no hay ventaja.** Con la receta y las fechas del 1.7, vigilando el 10 % de cada mes:

| | Compras morosas encontradas |
|---|---|
| Regresión logística | 30 % |
| Árbol de profundidad 3 | 26 % |
| Bosque | 28 % |
| Árbol sin límite | 13 % |

Entre los tres primeros hay un empate: la diferencia es de unos 8 morosos de 223, y cambia con la semilla. Lo firme es que árbol y bosque no le sacan ventaja real a la regresión, y que el árbol sin límite siempre es el peor. La mora se programó sumando efectos. Es el ejercicio del 2.3: más complejo no significa mejor.

### Series: el calendario ayuda, y una regla de Excel queda a la par

Para cada mes de julio a diciembre de 2025, se usa solo lo anterior a ese mes y se pronostican sus días. La venta media es de S/ 20,573 por día. La medida es venta en soles. **Todos los métodos ponen los feriados en cero**, porque ese día no se vende, y la regresión se entrena sin feriados.

| Método | Error por día | Error por mes | Error por día, mediana de 30 semillas más |
|---|---|---|---|
| Promedio por día de las últimas 8 semanas | 4,331 | 116,639 | 4,674 |
| Mismo día del año pasado (364 días antes) | 3,918 | 25,443 | 4,174 |
| Promedio de 8 semanas × índice del mes de 2024 | 2,935 | 35,970 | 2,954 |
| Regresión con día de la semana y mes | 2,848 | 25,078 | 3,300 |
| Regresión con día de la semana, mes y tendencia | 2,875 | 28,280 | 2,912 |

- **Lo estable es el calendario:** el promedio de 8 semanas pierde contra la regla con índice y contra la regresión en las 30 semillas.
- **Entre la regla con índice y la regresión con tendencia hay un empate por día:** la regla gana en 18 de 30 semillas, por poco. Una fórmula de Excel queda a la par. Es el mismo mensaje del 1.5.
- **La tendencia decide por mes.** Sin ella, la regresión subestima a una empresa que crece, y la regla le gana en 29 de 30 semillas. Con ella, la regresión gana a la regla en 24 de 30. Son solo 6 meses, y la semilla publicada es una excepción, porque ahí la tendencia no ayuda. Por eso el 2.4 usa la regresión con tendencia.
- **Sin bosque y sin `statsmodels`,** para que quepa y no haya otra versión que comprobar en Colab.

**Por qué el 2.5:** con ventanas mensuales de marzo a diciembre de 2025, la regla yerra de S/ 2,027 a S/ 3,710 por día según el mes, y la regresión con tendencia de S/ 1,812 a S/ 3,486. Por día, la regresión gana 7 meses y la regla 3. Por mes, en agosto gana la regresión (1,147 contra 20,964), y en septiembre la regla (7,206 contra 24,396). Mirando un solo mes, se concluye cualquier cosa.

### Texto: el 83 % y lo que hay debajo

Entrenamiento hasta junio de 2025 y prueba con 967 mensajes posteriores:

| Método | Exactitud |
|---|---|
| Decir siempre la categoría más común de entrenamiento | 22 % |
| Palabras clave, una lista hecha a mano en `tests/test_temporada_2.py` | 67 % |
| Regresión logística sobre conteo de palabras | 83 % (de 83 % a 86 % en otras semillas) |

| Dentro de ese 83 % | Mensajes | Exactitud |
|---|---|---|
| Con frases que no había al entrenar | 135 | 47 % (de 50 % a 59 % en otras semillas) |
| Con dos temas | 72 | 46 % |
| Con ambas cosas | 44 | 50 % |
| El resto | 716 | 96 % |

- **El 96 % no es mérito del modelo:** es casi el techo, porque el 4 % está mal etiquetado a propósito y los mensajes salen de 60 frases. Con mensajes reales se espera menos.
- **El modelo no conoce palabras nuevas.** Desde julio de 2025, cerca del 15 % de las frases es de una lista nueva.
- **Reentrenar se nota, con reservas.** Mes a mes de agosto a diciembre, el modelo fijo da 84 % y el que se reentrena cada mes da 90 %, con 84 % a 87 % y 90 % a 92 % en otras semillas. Las frases nuevas son solo 10 y se repiten, así que el reentrenamiento las memoriza. El 2.10 lo trata.
- **Los mensajes con dos temas** llevan la etiqueta del primero, algo que el conteo de palabras no puede ver.
- **La lista de palabras clave no es un límite:** cambia de 60 % a 69 % según el orden. Se muestra para ver qué tiene de bueno una regla.
- **Sin TF-IDF ni modelos de lenguaje como ChatGPT en el video.** Se menciona en un minuto que existen, y por qué sigue valiendo entender el conteo.

### Segmentación: los grupos son una decisión

Con tres columnas (días sin comprar, pedidos por mes activo y compra por mes activo) y k = 4:

| | Grupos | Qué pasa |
|---|---|---|
| Sin escalar | 126, 120, 41 y 13 clientes | Decide la compra en soles. Los perdidos quedan repartidos |
| Escalados | 181, 82, 12 y 25 clientes | Sale un grupo de 25 perdidos, de 393 días sin comprar de media |

- **El 4 es una elección.** No se presenta como un número descubierto, y no se usa una medida de separación en el video.
- **Los 25 perdidos son parte de los 30 que encuentra la regla del 1.9.** Una regla ya los encuentra. Y queda uno fuera con buena historia: entre las "12 grandes" está C0105, con 508 días sin comprar y S/ 8,659 por mes. Es un gran cliente perdido que el promedio del grupo esconde. Sirve de gancho.
- **Los grupos se parecen a `tipo`, pero no son lo mismo:** en el grupo de 181 hay 134 bodegas. Se compara con una tabla dinámica, y cambia con la semilla.
- **Son una decisión de negocio:** se pregunta qué haría la empresa distinto con cada grupo.

### Ética: dos episodios, porque en uno no cabe

El sesgo está programado y se dice desde el inicio. Por construcción, el puntaje de la prueba se sortea igual para todos (61.5 en mujeres y 62.3 en hombres). Eso no se puede suponer de una prueba real.

**2.8: se audita la decisión humana, por cargo.** De 2022 a 2025, entre quienes sacaron 75 o más, la parte llamada a entrevista:

| Cargo | Mujeres llamadas | Hombres llamados |
|---|---|---|
| Vendedor | 17 de 87 (20 %) | 51 de 95 (54 %) |
| Almacenero | 10 de 46 (22 %) | 77 de 137 (56 %) |
| Repartidor | 3 de 18 (17 %) | 70 de 132 (53 %) |
| Asistente administrativo | 22 de 57 (39 %) | 22 de 34 (65 %) |

- **Asistente es la mejor demostración:** ahí no se programó sesgo directo, y las mujeres quedan abajo igual en las 30 semillas revisadas. El tamaño de esta brecha es alto por azar: lo esperado son unos 16 puntos, no 26. Ocurre porque el reclutador castiga los meses sin empleo y premia poder viajar. Esas columnas difieren entre grupos: 13.5 meses en mujeres y 4.0 en hombres; poder viajar, 36 % y 71 %. Son valores programados, no miden capacidad, y este archivo no puede decir por qué ocurren ni si predicen desempeño.
- **Se pregunta si cada requisito hace falta.** Poder viajar puede ser un requisito real de un repartidor o un vendedor. No se borra sin analizarlo.
- **Pocos casos engañan.** Repartidor son 3 de 18 mujeres, y sirve de ejemplo en el episodio. En 2025 fueron 35 llamadas entre 271 mujeres en total. Incluso eligiendo solo por puntaje, algún cargo sale con brecha casi siempre. El 2.8 enseña a mirar conteos y a acumular años antes de concluir.

**2.9: un modelo que imita esa decisión.** En 2025 se llama a tantas personas por cargo como se llamó ese año: 215 de 783. Si se sorteara dentro de cada cargo, serían unas 72 mujeres.

| Quién elige | Mujeres llamadas, 2025 | Frente al sorteo, con 30 semillas más: mínimo, mediana y máximo |
|---|---|---|
| Reclutador, decisión histórica | 35 | 0.45, 0.58, 0.70 |
| Modelo con experiencia, prueba, cargo, indicadores y `sexo`, llamando a los de mayor probabilidad | 26 | 0.14, 0.29, 0.42 |
| Lo mismo sin `sexo` | 41 | 0.37, 0.53, 0.68 |
| Lo mismo sin `sexo` ni los dos indicadores | 72 | 0.86, 0.99, 1.15 |

Lo que se puede afirmar, y es estable:

- **Automatizar con un corte aplica el sesgo sin excepciones.** El modelo con `sexo` queda por debajo del reclutador en las 30 semillas. Lo causa el corte, no un defecto de cálculo.
- **Quitar `sexo` no alcanza:** en las 30 semillas se queda por debajo del sorteo. Aquí, 41 sale mejor que el reclutador por azar; lo normal, en 23 de 30, es que quede igual o peor.
- **Quitar los dos indicadores empareja, y eso no se traslada a un caso real.** Aquí solo se programaron dos, y se sabe cuáles son. En datos reales hay muchos, y borrar columnas no es una receta. El episodio tiene que decirlo con claridad.

Lo que **no** se puede afirmar:

- **Esta medida no dice si se eligió bien.** No sabemos cómo habría trabajado quien no fue llamado. La etiqueta es la decisión sesgada, y un modelo que la imita bien se ve bien en sus métricas. Es el mismo sesgo de selección que avisó el 1.7 con los créditos: el modelo solo ve a quienes ya recibieron crédito.
- **El umbral de 0.8, si se menciona, es una regla práctica de otro país:** no un criterio de justicia ni una norma peruana.

**Conclusión del episodio:** este modelo no se debe usar para filtrar, porque aprende de una etiqueta sesgada y no hay datos de desempeño. El 1.7 decía "una persona decide", y sigue siendo cierto. Pero no basta, porque esa persona es de donde salió el sesgo. Hace falta definir criterios antes de ver a los postulantes, revisar las tasas por cargo cada cierto tiempo, y nombrar a un responsable.

**Cuidado con el notebook:** su única función devuelve un conteo, sin probabilidades ni una lista de personas.

**Por verificar antes de grabar:** la lista de feriados de `catalogos.py`, que parece omitir el 7 de junio, el 23 de julio y el 6 de agosto, y las referencias legales en Perú, sobre ofertas de empleo sin discriminación y datos personales. Auditar por grupo exige tener el dato de sexo, y esa tensión debe entrar en la verificación. Debe salir de la fuente oficial, y el video no es asesoría legal.

### Un miniproyecto que no hace trampa

"Hoy" avanza cada día de diciembre de 2025. Cada mañana solo se usa lo que ya existe: los pedidos tomados para hoy y los mensajes de ayer. Los modelos se entrenan hasta el 30 de noviembre, con el bucle y las funciones ya listas.

| Parte del reporte | Resultado en diciembre | Línea base |
|---|---|---|
| Venta por día, venta media de S/ 25,630 | Regresión con tendencia: yerra S/ 3,486 por día | Regla con índice: S/ 3,524 |
| Vigilar el 10 % de cada día: 2,187 despachos, con 294 tardíos | Árbol de profundidad 6: encuentra 40 % | Al azar: 10 % |
| Tickets por área, 187 mensajes | 91 % de exactitud | Modelo de junio: 85 % |

Es un solo mes, ya visto al elegir estos métodos, y con campaña y lluvia: el 40 % no se traslada al año. Entre la regla y la regresión, el orden cambia con la semilla. El episodio no declara ganador. El reporte funciona los 31 días, incluidos los feriados, y supone que los pedidos del día se cerraron antes de armarlo.

## Para que quepa en 10 a 12 minutos

- **Se recorta:** el 2.1 solo enseña un árbol pequeño y su lectura; el 2.2 introduce el 10 % diario; el 2.4 compara dos reglas con la regresión con tendencia, solo por día; el 2.5 solo trata ventanas; el 2.6 deja el reentrenamiento para el 2.10; el 2.9 solo muestra cuatro conteos; el 2.10 usa un bucle ya entregado.
- **Se da como receta:** las entradas de cada modelo, `CountVectorizer`, `KMeans` y el bucle de ventanas del 2.5, sin explicar su matemática.
- **Ninguna duración está medida,** y esta temporada tampoco se ajustó con lo que salga al grabar el 0.1 y el 0.2. Los revisores estiman de 8 a 13 minutos, y de 12 a 14 en el 2.10, que es el de mayor riesgo. Conviene pasar sin narrar las celdas de funciones.

## Datos y herramientas

- **Datos:** cada archivo nuevo usa su propio flujo aleatorio, y los coeficientes se publican en `catalogos.py`.
- **Herramientas:** no se agrega ninguna librería.
- **Pruebas:** `tests/test_temporada_2.py` comprueba las cifras centrales de árbol, créditos, series, texto, segmentación y ética, y que las salidas guardadas de los notebooks muestren las cifras clave. Las afirmaciones de ética se comprueban con 30 semillas, y las de árbol y series con 3. Otras cifras de este temario no tienen una prueba propia, como los rangos por semilla y el reentrenamiento mes a mes.
