# Datos de Distribuidora Andina S.A.C.

**Distribuidora Andina S.A.C.** es una empresa ficticia peruana de consumo masivo. Vende al por mayor (por caja, fardo o paquete) abarrotes, bebidas, productos de limpieza, de cuidado personal y snacks a bodegas, minimarkets y restaurantes desde 6 sedes: Lima, Arequipa, Trujillo, Chiclayo, Piura y Cusco.

Todos los datos son **sintéticos**: los crea el paquete [`generador/`](../generador/distribuidora_andina) y no pertenecen a ninguna persona ni empresa real. Las marcas y los nombres de negocios son inventados. Puedes usarlos libremente (CC BY 4.0).

## Archivos

| Archivo | Qué contiene | Filas | Se usa en |
|---|---|---|---|
| [`productos.csv`](productos.csv) | Catálogo de productos | 51 | 0.6, 0.7, 0.8, 1.1 |
| [`clientes.csv`](clientes.csv) | Bodegas, minimarkets y restaurantes | 300 | 0.4, 0.6, 0.8, Temporadas 1 y 2 |
| [`empleados.csv`](empleados.csv) | Equipo de ventas | 14 | 0.6, 0.8 |
| [`ventas.csv`](ventas.csv) | Ventas de 2024 y 2025, ya limpias | 50,000 | 0.4 a 0.8, Temporadas 1 y 2 |
| [`ventas_crudo.csv`](ventas_crudo.csv) | Las mismas ventas "como las exporta la oficina", con problemas para limpiar | 50,750 | 0.5, 0.8, 1.9 |
| [`creditos.csv`](creditos.csv) | Compras al crédito y si cayeron en mora | 8,316 | 1.7, 1.8, 2.3 |
| [`despachos.csv`](despachos.csv) | Despachos por cliente y día, y si llegaron tarde | 41,837 | 2.1 a 2.3, 2.10 |
| [`tickets.csv`](tickets.csv) | Mensajes de clientes clasificados a mano | 3,600 | 2.6, 2.10 |
| [`postulaciones.csv`](postulaciones.csv) | Postulaciones y decisión de entrevistar, con un sesgo programado | 3,200 | 2.8, 2.9 |
| [`reporte_ventas_2025.xlsx`](reporte_ventas_2025.xlsx) | Libro de Excel con las hojas *Ventas* (25,667 ventas de 2025), *Productos* y *Clientes* | — | 0.4 |

## Cómo se relacionan

```
productos ──(id_producto)──┐
                           ├──► ventas ◄──(id_cliente)── clientes
empleados ──(id_vendedor)──┘                                │
    ▲                                                       │
    └──────────────────────(id_vendedor)────────────────────┘

creditos ──(id_cliente)──► clientes
despachos ─(id_cliente)──► clientes
tickets ───(id_cliente)──► clientes

postulaciones: no se conecta con los demás archivos
```

Es como tener varias hojas de Excel que se conectan con `=BUSCARV()` (`VLOOKUP`) a través de un código.

## Diccionario de datos

### `productos.csv`

| Columna | Descripción | Ejemplo |
|---|---|---|
| `id_producto` | Código del producto | `P001` |
| `categoria` | Abarrotes, Bebidas, Limpieza, Cuidado personal o Snacks | `Abarrotes` |
| `nombre` | Nombre del producto | `Arroz extra 5 kg` |
| `marca` | Marca (inventada) | `Valle Dorado` |
| `presentacion` | Cómo se vende: caja, fardo o paquete, y cuántas unidades trae | `Fardo x 5` |
| `precio` | Precio mayorista de la presentación, en soles | `99.5` |
| `costo` | Costo de la presentación para la empresa, en soles | `85.21` |

### `clientes.csv`

| Columna | Descripción | Ejemplo |
|---|---|---|
| `id_cliente` | Código del cliente | `C0001` |
| `nombre` | Nombre del negocio | `Bodeguita Don Carlos` |
| `tipo` | Bodega, Minimarket o Restaurante | `Bodega` |
| `ciudad` | Sede que lo atiende | `Arequipa` |
| `fecha_alta` | Fecha en que empezó a comprarnos | `2020-09-27` |
| `limite_credito` | Monto máximo que puede comprar al crédito, en soles | `3000` |
| `id_vendedor` | Vendedor asignado (ver `empleados.csv`) | `E006` |

### `empleados.csv`

| Columna | Descripción | Ejemplo |
|---|---|---|
| `id_empleado` | Código del empleado | `E001` |
| `nombre` | Nombre completo | `María Espinoza Ramos` |
| `sexo` | `F` o `M` | `F` |
| `area` | Área de la empresa | `Ventas` |
| `cargo` | Puesto | `Vendedor` |
| `sede` | Ciudad donde trabaja | `Lima` |
| `fecha_ingreso` | Fecha en que entró a la empresa | `2021-03-30` |

### `ventas.csv`

Cada fila es la venta de **un producto** a **un cliente** en una fecha.

| Columna | Descripción | Ejemplo |
|---|---|---|
| `id_venta` | Número de venta | `V000001` |
| `fecha` | Fecha de la venta (aaaa-mm-dd) | `2024-01-02` |
| `id_cliente` | Cliente que compró | `C0002` |
| `id_producto` | Producto vendido | `P022` |
| `id_vendedor` | Vendedor que atendió | `E006` |
| `ciudad` | Sede donde se hizo la venta | `Arequipa` |
| `cantidad` | Presentaciones vendidas (cajas, fardos o paquetes) | `3` |
| `precio_unitario` | Precio de cada presentación, en soles | `48.0` |
| `descuento` | Descuento por volumen: 0, 0.05 (desde 10 presentaciones) o 0.10 (desde 20) | `0.0` |
| `total` | `cantidad × precio_unitario × (1 − descuento)`, redondeado a céntimos como `=REDONDEAR()` (`ROUND`) en Excel | `144.0` |
| `metodo_pago` | Efectivo, Billetera digital, Transferencia o Crédito | `Efectivo` |

### `creditos.csv`

Cada fila es una compra al crédito: las ventas con `metodo_pago` igual a `Crédito`, agrupadas por cliente y día. Las columnas `dias_atraso` y `moroso` se conocen después de la venta. No sirven como entradas de un modelo: usarlas sería hacer trampa.

| Columna | Descripción | Ejemplo |
|---|---|---|
| `id_credito` | Código de la compra al crédito | `K00001` |
| `fecha` | Fecha de la compra (aaaa-mm-dd) | `2024-01-02` |
| `id_cliente` | Cliente que compró | `C0024` |
| `tipo` | Bodega, Minimarket o Restaurante | `Minimarket` |
| `monto` | Monto de la compra, en soles | `276.0` |
| `plazo_dias` | Días de plazo para pagar: 15 en bodegas y 30 en los demás | `30` |
| `antiguedad_anios` | Años como cliente el día de la compra | `7.69` |
| `monto_sobre_limite` | `monto` entre `limite_credito` del cliente. Mide una sola compra, no la deuda total | `0.0276` |
| `casos_previos` | Compras del cliente desde enero de 2024 cuyo resultado ya se conocía ese día | `0` |
| `morosos_previos` | De esas compras, cuántas fueron morosas | `0` |
| `dias_atraso` | Días de atraso tras vencer el plazo, observados hasta el 31 de diciembre de 2025. Vacío si aún no se puede saber | `5` |
| `moroso` | `1` si el atraso pasó de 30 días y `0` si no. Vacío si aún no se puede saber | `0` |

Los datos terminan el 31 de diciembre de 2025: 760 compras todavía no tienen resultado, y como el plazo cambia por tipo, las de bodegas maduran antes. No se simula ningún bloqueo de crédito: un cliente con deudas vencidas puede seguir comprando. Y no hay pérdidas: toda compra termina pagándose.

Las relaciones de este archivo están programadas en [`catalogos.py`](../generador/distribuidora_andina/catalogos.py), y cada cliente tiene además un riesgo propio que no se publica. Lo que un modelo encuentre aquí refleja lo programado, no un hallazgo sobre negocios reales.

### `despachos.csv`

Cada fila es un despacho: todas las ventas de un cliente en un día, con la fecha de la venta. `llego_tarde` se conoce después de la salida, así que no sirve como entrada. El resto se conoce al preparar el despacho, no antes de que el cliente haga su pedido.

| Columna | Descripción | Ejemplo |
|---|---|---|
| `id_despacho` | Código del despacho | `D00001` |
| `fecha` | Fecha del despacho (aaaa-mm-dd) | `2024-01-02` |
| `id_cliente` | Cliente | `C0002` |
| `ciudad` | Sede que despacha | `Arequipa` |
| `tipo` | Bodega, Minimarket o Restaurante | `Minimarket` |
| `distancia_km` | Distancia del cliente a su sede, hasta 60 km. Es fija por cliente | `20.5` |
| `lineas` | Líneas de venta del despacho | `1` |
| `presentaciones` | Cajas, fardos o paquetes | `3` |
| `transportista` | `Propio` o `Tercero` | `Tercero` |
| `llego_tarde` | `1` si no llegó en la ventana prometida y `0` si llegó | `0` |

La tardanza está programada en [`catalogos.py`](../generador/distribuidora_andina/catalogos.py) con reglas que actúan en combinación: lluvias en Cusco para clientes lejanos, terceros en sábado y pedidos grandes en campaña. Refleja lo programado, no un hallazgo sobre empresas reales.

### `tickets.csv`

Mensajes de clientes a Atención al Cliente; los del canal Teléfono los transcribe un operador. Se redactan combinando frases de `catalogos.py`, por lo que su vocabulario es mucho más pequeño que el de un negocio real. El 12 % mezcla dos temas y su categoría es la del primero. El 4 % está mal clasificado a propósito. Desde julio de 2025, cerca del 15 % de las frases es de una lista nueva. `id_despacho` delata la categoría, así que no sirve como entrada de un modelo.

| Columna | Descripción | Ejemplo |
|---|---|---|
| `id_ticket` | Código del ticket | `T00001` |
| `fecha` | Fecha del mensaje (aaaa-mm-dd) | `2024-01-03` |
| `id_cliente` | Cliente que escribe | `C0283` |
| `id_despacho` | Despacho tardío que originó el mensaje. Vacío en los demás | `D00123` |
| `canal` | WhatsApp, Teléfono o Correo | `WhatsApp` |
| `mensaje` | Lo que escribió o dijo el cliente | `Buenas, el arroz vino con gorgojos. Es urgente.` |
| `categoria` | Despacho, Facturación, Producto, Cobranza o Consulta comercial, asignada a mano | `Producto` |

### `postulaciones.csv`

Postulaciones de 2022 a 2025 y la decisión histórica de llamar o no a entrevista. **El sesgo contra las mujeres está programado a propósito para enseñar a detectarlo:** no describe a ninguna empresa ni a ninguna persona real. Es directo en Vendedor, Almacenero y Repartidor, y en todos los cargos llega también por dos columnas: `meses_sin_empleo` y `puede_viajar`. Sus diferencias entre grupos están programadas y no miden capacidad. El puntaje de la prueba se sortea igual para todos, algo que no se puede suponer de una prueba real. `sexo` usa solo `F` y `M`, una simplificación de estos datos. Son muchas postulaciones para esta empresa; `empleados.csv` solo cubre ventas.

| Columna | Descripción | Ejemplo |
|---|---|---|
| `id_postulacion` | Código de la postulación | `A00001` |
| `fecha` | Fecha de la postulación (aaaa-mm-dd) | `2022-01-01` |
| `cargo` | Vendedor, Almacenero, Repartidor o Asistente administrativo | `Almacenero` |
| `sede` | Ciudad del puesto | `Lima` |
| `sexo` | `F` o `M` | `M` |
| `anios_experiencia` | Años de experiencia | `2.6` |
| `meses_sin_empleo` | Meses sin empleo formal antes de postular | `3` |
| `puede_viajar` | `1` si declara poder viajar por trabajo | `1` |
| `puntaje_prueba` | Puntaje de la prueba de la empresa, de 0 a 100 | `63` |
| `entrevistado` | `1` si se le llamó a entrevista y `0` si no | `0` |

### `ventas_crudo.csv`

Las mismas ventas, pero con los problemas de un archivo real exportado en la oficina. Es la materia prima del episodio 0.5:

- Separado por punto y coma (`;`), como lo exportan muchos sistemas.
- Nombres de columna con mayúsculas, espacios y tildes (`Método de Pago`).
- Filas duplicadas.
- Ciudades escritas de distintas formas: `Lima`, `lima`, `LIMA`, `Lima ` (con espacio al final).
- Métodos de pago escritos de distintas formas: `efectivo`, `EFECTIVO`, y `Yape` o `Plin` en lugar de `Billetera digital`.
- Fechas como texto, casi todas en formato `dd/mm/aaaa` y unas pocas en `aaaa-mm-dd`.
- Montos como texto con símbolo de moneda y separador de miles: `S/ 1,250.50`.
- Descuentos como texto: `5%`.
- Celdas vacías en `Cantidad` y `Método de Pago`.
- Unas pocas cantidades absurdas por errores de tipeo.

## Lo que esconden los datos

Los datos no son aleatorios: tienen patrones como los de una empresa real, que iremos descubriendo durante la serie.

- Las ventas suben en **julio** (Fiestas Patrias) y en **diciembre** (Navidad), y bajan en enero y febrero.
- En **verano** (diciembre a marzo) se venden más bebidas y snacks.
- El **panetón** se vende casi solo en noviembre y diciembre.
- **2025 vende más que 2024.**
- No hay despachos los **feriados nacionales**, y los **domingos** las ventas bajan mucho.
- Cada tipo de cliente compra distinto: los restaurantes compran sobre todo abarrotes.
- Algunos clientes **dejaron de comprarnos**... ¿podrás encontrarlos?

## Volver a generar los datos

```bash
pip install -e .
python -m distribuidora_andina
```

El generador usa una semilla fija, así que siempre produce exactamente los mismos datos. Las pruebas comprueban que los archivos de esta carpeta coinciden con lo que genera el código.
