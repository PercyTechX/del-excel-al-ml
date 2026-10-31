# Temporada 1: Fundamentos de Machine Learning

> **Temario aprobado; los notebooks están por hacerse.** Las cifras de pronóstico se apoyan en un solo julio y un solo diciembre.

Ya sabes limpiar, cruzar y graficar datos en Python. Ahora la computadora va a aprender de esos datos para responder preguntas sobre lo que todavía no ha pasado.

| # | Episodio | Pregunta de la empresa | Lo que ya sabes en Excel | Se aprende |
|---|---|---|---|---|
| 1.1 | ¿Qué es Machine Learning? | El `total` tiene una fórmula exacta. ¿Y cuánto comprará un cliente? | Una regla con `=SI()` (`IF`) | Reglas contra ejemplos, variables de entrada y objetivo, entrenar y predecir |
| 1.2 | Tu primer modelo: la recta | ¿Cómo se asocian las líneas de pedido del mes con el monto de la compra? | Gráfico de dispersión, línea de tendencia, `=PENDIENTE()` (`SLOPE`), `=INTERSECCION.EJE()` (`INTERCEPT`), `=PRONOSTICO.LINEAL()` (`FORECAST.LINEAR`), `=COEFICIENTE.R2()` (`RSQ`) | Dispersión, regresión lineal con `.fit()` y `.predict()`, R² y los límites de una recta |
| 1.3 | ¿Funciona con datos nuevos? | ¿Podemos confiar en ese número? | Comparar lo proyectado con lo real, con `=ABS()` y `=PROMEDIO()` (`AVERAGE`) | Entrenamiento y prueba, error en soles (MAE) y línea base |
| 1.4 | Pronostica sin hacer trampa | ¿Cuánto comprará cada cliente el próximo mes? | Promedio de los últimos meses | Fuga de datos, separar por fechas y reglas simples como línea base |
| 1.5 | Más variables y la temporada | ¿Ayudan el mes, el tipo de cliente y la ciudad? | Índice del mes con una tabla dinámica | Varias variables, textos a números y estacionalidad |
| 1.6 | Cuando el modelo se aprende las respuestas | ¿Por qué un modelo mejor en entrenamiento falla en prueba? | Una fórmula hecha a la medida de un solo mes | Sobreajuste y por qué se separan los datos |
| 1.7 | Clasificación: ¿qué crédito revisamos primero? | ¿Qué ventas al crédito conviene revisar o cobrar antes? | `=SI()` (`IF`) con un umbral | Regresión logística, probabilidad y umbral |
| 1.8 | Cuando el 85 % de aciertos no sirve | ¿El modelo sirve, o solo parece bueno? | Una tabla dinámica de real contra predicho | Exactitud, matriz de confusión, precisión, exhaustividad y umbral según el costo en soles |
| 1.9 | Miniproyecto: el pronóstico de la cartera | ¿Cuánto se venderá en diciembre, por cartera? | El reporte del episodio 0.8 | Del archivo crudo al modelo y a un Excel, comprobando contra lo que realmente pasó |

## Por qué así

### Primero una recta que falla

Tomando solo los meses en que cada cliente compró, hay 6,459 filas. La recta entre líneas de pedido y monto da un R² de 0.76, con la fórmula `total = -417 + 325.5 × líneas`. Sus defectos enseñan:

- Para una sola línea predice una compra **negativa**: S/ -91.5.
- Un solo valor por línea promedia clientes muy distintos: con rectas separadas, S/ 207 por línea en bodegas y S/ 369 en minimarkets.
- Las líneas del mes no se conocen antes de que termine el mes. Sirve para aprender la recta, pero no para pronosticar: es el gancho del 1.4.

### Una comparación honesta en el 1.4 y el 1.5

Error medio en soles:

| Método | Por cliente y mes, jul-dic 2025 | Por cartera y mes, jul-dic 2025 | Por cliente y mes, oct-dic 2025 | Por cartera y mes, oct-dic 2025 |
|---|---|---|---|---|
| Promedio de sus últimos 3 meses | 889 | 8,386 | | 8,514 |
| Promedio de sus últimos 6 meses | 855 | 7,704 | 864 | 7,385 |
| Promedio de 6 meses × índice del mes de 2024 | 827 | 4,963 | 863 | 4,681 |
| Regresión con varias variables | 921 | 4,819 | 965 | 4,412 |

Lo que se puede afirmar:

- **La estacionalidad baja el error por cartera en un 36 %**, frente al promedio de 6 meses. Casi toda la mejora viene de julio y diciembre.
- **Entre la regresión y la regla con índice hay un empate por cartera.** La regla se puede hacer en Excel.
- **Cliente por cliente, la regla con índice le gana a esta regresión** en julio a diciembre. Por eso se compara siempre con una línea base. Si la regresión les asigna 0 a los clientes sin compras en 3 meses, baja de 921 a 861, y la ventaja de la regla se achica.

**Definición exacta:** una fila por cliente y mes, con cero en los meses sin compra. Los promedios cuentan como cero los meses anteriores al alta. Se evalúa desde el mes en que el primer día ya es posterior o igual al alta. La regresión usa la compra del mes anterior, el promedio de 3 meses, el tipo, la ciudad y el mes, y se entrena con julio de 2024 a junio de 2025. El índice es la venta de ese mes en 2024 entre el promedio mensual de 2024.

### Sobreajuste con una demostración clara

Agregar una variable por cada cliente y trimestre pasa de 23 a 1,188 variables. El error en entrenamiento baja de 878 a 570, y en prueba sube de 921 a 1,346. La recta del 1.3 no sirve para mostrarlo, porque casi no cambia entre entrenamiento y prueba.

### Clasificación con créditos

Se descartaron dos casos:

- **Clientes que dejan de comprar:** en estos datos, la baja se sortea y corta la compra de golpe, sin señal previa, y hay muy pocos casos para evaluar. Encontrarlos ya es fácil con una regla: 30 clientes no compraron de octubre a diciembre de 2025. Queda como ejercicio del 1.9.
- **Renuncias de personal:** una plantilla creíble para estas ventas da muy pocos casos, y predecir quién renunciará es delicado.

El caso elegido es **`creditos.csv`**, con 8,316 compras al crédito: las 8,674 líneas de `ventas.csv` agrupadas por cliente y día. Reglas de diseño:

- **Etiqueta:** tiene `plazo_dias` y `dias_atraso`, y moroso significa más de 30 días de atraso tras vencer el plazo. `dias_atraso` solo sirve para crear la etiqueta: usarlo como entrada sería fuga.
- **Fecha de corte:** una venta cuyo plazo aún no ha madurado no se usa, ni en entrenamiento ni en prueba. La partición se escribe por fechas.
- **Señal:** riesgo propio de cada cliente, que no se publica, más el monto frente al límite de crédito, la antigüedad y el tipo. El historial de morosidad solo cuenta compras cuya mora ya se conocía ese día, desde enero de 2024.
- **Coeficientes publicados** en `generador/distribuidora_andina/catalogos.py`, y ajustados con otras semillas, no con la oficial. Son datos sintéticos, y el 1.7 debe decirlo. Con 298 clientes y su riesgo propio, un modelo recupera bien el efecto del monto, pero no separa con claridad el del tipo ni el de la antigüedad: esa también es una lección.

**Receta:** logaritmo de `monto_sobre_limite`, `antiguedad_anios`, `tipo`, tasa de morosidad previa (0 si no hay historial) y una columna que marca a quienes no tienen historial. Entrena con lo que ya se conocía el 1 de julio de 2025 y prueba con 1,531 compras posteriores, de las que 223 resultaron morosas:

| | Decir que ninguna cae en mora | Regla: tasa previa de 30 % o más | Modelo, umbral 0.5 | Modelo, umbral 0.25 |
|---|---|---|---|---|
| Compras marcadas | 0 | 271 | 6 | 227 |
| Exactitud | 85.4 % | 79.4 % | 85.3 % | 81.7 % |
| Precisión | | 33 % | no aplica (6 marcadas) | 37 % |
| Exhaustividad | 0 % | 40 % | 1 % | 38 % |

Con umbral 0.5, el modelo casi no marca a nadie. Al bajarlo pierde exactitud, pero encuentra a más de un tercio de los morosos. Ese es el corazón del 1.8. Y hay dos avisos honestos:

- **La regla simple casi empata con el modelo:** el AUC es 0.70 para la regla y 0.71 para el modelo. El historial sí aporta, porque sin él baja a 0.64. Pero aquí una columna hace casi todo el trabajo, como pasa con el pronóstico.
- **Cuántas marca con 0.5 depende mucho de la semilla:** con otras semillas va de 3 a 54 compras. El episodio no debe presentar esa fila como una cifra estable.

Los datos no incluyen pérdidas ni costos, porque toda compra termina pagándose. El 1.8 declara sus supuestos de costo en soles, y muestra cómo cambia el umbral con ellos. Tampoco se puede evaluar a clientes nuevos: en la prueba casi todos tienen historial.

**Avisos de un minuto en el 1.7 y el 1.8:** sirve para ordenar qué revisar, no para negar crédito automáticamente. Una persona decide. Y el modelo solo ve a quienes ya recibieron crédito, lo que es un sesgo. La ética completa va en la Temporada 2.

### Un miniproyecto que se puede comprobar

Fijamos "hoy" en el 30 de noviembre de 2025 y pronosticamos diciembre, para compararlo con lo que pasó:

| Método | Error por cartera, diciembre de 2025 |
|---|---|
| Promedio de 6 meses | S/ 14,256 |
| Promedio de 6 meses × índice | S/ 7,316 |
| Regresión | S/ 6,090 (cerca del 11 %) |

- **La diferencia entre las dos últimas es un empate:** en simulaciones con otras semillas del generador, la regla gana a menudo. Se muestran las tres, sin declarar ganador.
- **No pronosticamos enero de 2026**, porque no se puede verificar.
- **Es un pronóstico de cartera, no una meta.** El error va del 1 % al 40 % según la cartera, así que no sirve para evaluar ni pagar a un vendedor.
- **No dice qué producto ofrecer:** el generador elige los productos por tipo de cliente y mes, sin preferencias propias de cada cliente.
- **Ejercicio:** encontrar a los clientes perdidos con una regla simple. Responde el "¿podrás encontrarlos?" de `datos/README.md`.

## Para que quepa en 10 a 12 minutos

- La tabla por cliente y mes, con sus promedios, se entrega como función lista, igual que `limpiar_ventas` en el 0.8. Lo mismo el Excel del 1.9.
- `preparar_X()` convierte textos en números y usa las columnas de entrenamiento. `make_pipeline(StandardScaler(), LogisticRegression())` se da como receta en el 1.7.
- `shift`, `rolling` y `get_dummies` no se enseñan a fondo: se explica qué hacen, y cada notebook los deja listos.
- Ninguna duración está medida. Hay que ajustar estos episodios con lo que salga al grabar el 0.1 y el 0.2.

## Datos y herramientas

- **Datos:** `creditos.csv` va en su propio flujo aleatorio, y una prueba con huellas comprueba que no cambia ningún archivo de la Temporada 0. RRHH y los tickets quedan para la Temporada 2.
- **Herramientas:** se agrega **scikit-learn** 1.6.1, la versión de Colab.
- **Pruebas:** al escribir los notebooks, las cifras de esta página se convertirán en pruebas, y otra prueba mantendrá iguales las funciones copiadas entre ellos.
