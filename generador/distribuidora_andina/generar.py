"""Generación de las tablas de Distribuidora Andina S.A.C.

Cada tabla usa su propio generador aleatorio, derivado de la semilla general.
Así, agregar o cambiar una tabla no altera los datos de las demás.
"""

import numpy as np
import pandas as pd

from . import catalogos as cat

SEMILLA = 2024

# Número fijo por tabla para derivar su generador aleatorio.
_FLUJO = {
    "productos": 1,
    "empleados": 2,
    "clientes": 3,
    "ventas": 4,
    "crudo": 5,
    "creditos": 6,
    "despachos": 7,
    "tickets": 8,
    "postulaciones": 9,
}


def rng_tabla(tabla: str, semilla: int = SEMILLA) -> np.random.Generator:
    """Generador aleatorio propio de una tabla."""
    return np.random.default_rng([semilla, _FLUJO[tabla]])


def _fechas_aleatorias(
    rng: np.random.Generator, n: int, desde: pd.Timestamp, hasta: pd.Timestamp
) -> pd.DatetimeIndex:
    dias = (hasta - desde).days + 1
    return desde + pd.to_timedelta(rng.integers(0, dias, n), unit="D")


def generar_productos(semilla: int = SEMILLA) -> pd.DataFrame:
    """Catálogo de productos con su precio mayorista y su costo."""
    rng = rng_tabla("productos", semilla)
    columnas = ["categoria", "nombre", "marca", "presentacion", "precio"]
    df = pd.DataFrame(cat.PRODUCTOS, columns=columnas)
    df["costo"] = (df["precio"] * rng.uniform(*cat.MARGEN_COSTO, len(df))).round(2)
    df.insert(0, "id_producto", [f"P{i:03d}" for i in range(1, len(df) + 1)])
    return df


def generar_empleados(semilla: int = SEMILLA) -> pd.DataFrame:
    """Empleados de la empresa. En la fase 1, solo el equipo de ventas."""
    rng = rng_tabla("empleados", semilla)
    filas, usados = [], set()
    for sede, cantidad in cat.VENDEDORES_POR_SEDE.items():
        for _ in range(cantidad):
            while True:
                sexo = rng.choice(["F", "M"])
                nombres = cat.NOMBRES_MUJER if sexo == "F" else cat.NOMBRES_HOMBRE
                ap1, ap2 = rng.choice(cat.APELLIDOS, 2, replace=False)
                nombre = f"{rng.choice(nombres)} {ap1} {ap2}"
                if nombre not in usados:
                    usados.add(nombre)
                    break
            filas.append(
                {
                    "nombre": nombre,
                    "sexo": sexo,
                    "area": "Ventas",
                    "cargo": "Vendedor",
                    "sede": sede,
                }
            )
    df = pd.DataFrame(filas)
    df["fecha_ingreso"] = _fechas_aleatorias(
        rng, len(df), pd.Timestamp("2015-01-01"), pd.Timestamp("2023-12-31")
    )
    df.insert(0, "id_empleado", [f"E{i:03d}" for i in range(1, len(df) + 1)])
    return df


def _cantidad_por_tipo() -> dict[str, int]:
    tipos = list(cat.TIPOS_CLIENTE)
    cantidades = {t: round(cat.N_CLIENTES * cat.TIPOS_CLIENTE[t]) for t in tipos[:-1]}
    cantidades[tipos[-1]] = cat.N_CLIENTES - sum(cantidades.values())
    return cantidades


def _nombres_de_negocio(rng: np.random.Generator, tipo: str, cantidad: int) -> list[str]:
    opciones = [f"{p} {n}" for p, nombres in cat.NOMBRES_NEGOCIO[tipo].items() for n in nombres]
    assert len(opciones) >= cantidad, (
        f"Hay {len(opciones)} nombres posibles para '{tipo}' y se necesitan {cantidad}. "
        "Agrega más nombres en catalogos.NOMBRES_NEGOCIO."
    )
    return list(rng.choice(opciones, cantidad, replace=False))


def generar_clientes(empleados: pd.DataFrame, semilla: int = SEMILLA) -> pd.DataFrame:
    """Clientes (bodegas, minimarkets y restaurantes), cada uno con un vendedor de su sede."""
    rng = rng_tabla("clientes", semilla)
    cantidades = _cantidad_por_tipo()
    tipos = rng.permutation([t for t, n in cantidades.items() for _ in range(n)])
    nombres = {t: iter(_nombres_de_negocio(rng, t, n)) for t, n in cantidades.items()}

    df = pd.DataFrame({"nombre": [next(nombres[t]) for t in tipos], "tipo": tipos})
    df["ciudad"] = rng.choice(list(cat.SEDES), len(df), p=list(cat.SEDES.values()))

    nuevo = rng.random(len(df)) < cat.PROPORCION_CLIENTES_NUEVOS
    df["fecha_alta"] = _fechas_aleatorias(
        rng, len(df), pd.Timestamp("2016-01-01"), pd.Timestamp("2023-12-31")
    )
    df.loc[nuevo, "fecha_alta"] = _fechas_aleatorias(
        rng, nuevo.sum(), cat.INICIO, pd.Timestamp("2025-09-30")
    )
    df["limite_credito"] = [int(rng.choice(cat.LIMITES_CREDITO[t])) for t in df["tipo"]]
    df["id_vendedor"] = [
        rng.choice(empleados.loc[empleados["sede"] == c, "id_empleado"].to_numpy())
        for c in df["ciudad"]
    ]
    df.insert(0, "id_cliente", [f"C{i:04d}" for i in range(1, len(df) + 1)])
    return df


def _fechas_de_baja(clientes: pd.DataFrame, rng: np.random.Generator) -> pd.Series:
    """Fecha en que cada cliente deja de comprar (NaT si sigue activo).

    No se publica: es el patrón oculto que se descubrirá al analizar la recencia de compra.
    """
    baja = pd.Series(pd.NaT, index=clientes.index, dtype="datetime64[ns]")
    candidatos = clientes.index[clientes["fecha_alta"] < pd.Timestamp("2025-01-01")]
    n = round(len(clientes) * cat.PROPORCION_CLIENTES_PERDIDOS)
    perdidos = rng.choice(candidatos, n, replace=False)
    desde = clientes.loc[perdidos, "fecha_alta"].clip(lower=cat.INICIO) + pd.Timedelta(days=90)
    hasta = pd.Timestamp("2025-09-30")
    dias = ((hasta - desde).dt.days * rng.random(n)).astype(int)
    baja[perdidos] = desde + pd.to_timedelta(dias, unit="D")
    return baja


def _pesos_por_dia(dias: pd.DatetimeIndex) -> np.ndarray:
    peso = (
        dias.month.map(cat.ESTACIONALIDAD_MES).to_numpy()
        * dias.day_of_week.map(cat.ESTACIONALIDAD_DIA).to_numpy()
        * np.where(dias.year > cat.INICIO.year, cat.CRECIMIENTO_ANUAL, 1.0)
    )
    peso[dias.isin(cat.FERIADOS)] = 0.0
    return peso


def _pesos_producto_por_mes(productos: pd.DataFrame, rng: np.random.Generator) -> np.ndarray:
    """Matriz (mes 1–12 × producto) con la popularidad base y la estacionalidad."""
    popularidad = rng.lognormal(0, 0.6, len(productos))
    matriz = np.tile(popularidad, (12, 1))
    for categoria, por_mes in cat.ESTACIONALIDAD_CATEGORIA.items():
        columnas = (productos["categoria"] == categoria).to_numpy()
        matriz[:, columnas] *= np.array([por_mes[m] for m in range(1, 13)])[:, None]
    for nombre, por_mes in cat.ESTACIONALIDAD_PRODUCTO.items():
        columnas = (productos["nombre"] == nombre).to_numpy()
        matriz[:, columnas] *= np.array([por_mes[m] for m in range(1, 13)])[:, None]
    return matriz


def _redondear_a_centimos(cantidad, precio, descuento_pct) -> np.ndarray:
    """Total redondeado a céntimos "hacia arriba desde 0.5", igual que REDONDEAR() en Excel."""
    precio_cent = np.round(np.asarray(precio) * 100).astype(np.int64)
    bruto = np.asarray(cantidad, dtype=np.int64) * precio_cent * (100 - descuento_pct)
    return ((bruto + 50) // 100) / 100


def generar_ventas(
    productos: pd.DataFrame, clientes: pd.DataFrame, semilla: int = SEMILLA
) -> pd.DataFrame:
    """Ventas diarias de 2024 y 2025. Cada fila es un producto vendido a un cliente."""
    rng = rng_tabla("ventas", semilla)
    dias = pd.date_range(cat.INICIO, cat.FIN, freq="D")
    peso_dia = _pesos_por_dia(dias)
    peso_producto = _pesos_producto_por_mes(productos, rng)
    baja = _fechas_de_baja(clientes, rng)

    # Cuántas ventas tiene cada cliente: según su tipo, un factor propio y el peso de los días
    # en que estuvo activo (así el crecimiento y la estacionalidad afectan al total).
    hasta = baja.fillna(cat.FIN)
    activo = (dias.to_numpy() >= clientes["fecha_alta"].to_numpy()[:, None]) & (
        dias.to_numpy() <= hasta.to_numpy()[:, None]
    )
    actividad = clientes["tipo"].map(cat.ACTIVIDAD_POR_TIPO) * rng.lognormal(0, 0.5, len(clientes))
    actividad *= (activo * peso_dia).sum(axis=1) / peso_dia.sum()
    n_por_cliente = rng.multinomial(cat.N_VENTAS, actividad / actividad.sum())

    ids_producto = productos["id_producto"].to_numpy()
    precios = productos["precio"].to_numpy()
    partes = []
    for i, cliente in enumerate(clientes.itertuples()):
        n = n_por_cliente[i]
        if n == 0:
            continue
        p_dia = peso_dia * activo[i]
        fechas = pd.DatetimeIndex(rng.choice(dias, n, p=p_dia / p_dia.sum()))

        preferencia = productos["categoria"].map(cat.PREFERENCIA_CATEGORIA[cliente.tipo])
        pesos = peso_producto * preferencia.fillna(1.0).to_numpy()
        idx = np.empty(n, dtype=int)
        for mes in np.unique(fechas.month):
            en_mes = fechas.month == mes
            p = pesos[mes - 1]
            idx[en_mes] = rng.choice(len(productos), en_mes.sum(), p=p / p.sum())

        media = cat.CANTIDAD_MEDIA[cliente.tipo]
        k = cat.DISPERSION_CANTIDAD
        partes.append(
            pd.DataFrame(
                {
                    "fecha": fechas,
                    "id_cliente": cliente.id_cliente,
                    "id_producto": ids_producto[idx],
                    "id_vendedor": cliente.id_vendedor,
                    "ciudad": cliente.ciudad,
                    "cantidad": rng.negative_binomial(k, k / (k + media), n) + 1,
                    "precio_unitario": precios[idx],
                    "metodo_pago": rng.choice(
                        cat.METODOS_PAGO, n, p=cat.PROBABILIDAD_PAGO[cliente.tipo]
                    ),
                }
            )
        )

    df = pd.concat(partes, ignore_index=True)
    condiciones = [df["cantidad"] >= desde_n for desde_n, _ in cat.DESCUENTOS]
    descuento_pct = np.select(condiciones, [pct for _, pct in cat.DESCUENTOS], 0)
    df["descuento"] = descuento_pct / 100
    df["total"] = _redondear_a_centimos(df["cantidad"], df["precio_unitario"], descuento_pct)

    df = df.sort_values(["fecha", "id_cliente", "id_producto"], kind="stable", ignore_index=True)
    df.insert(0, "id_venta", [f"V{i:06d}" for i in range(1, len(df) + 1)])
    columnas = [
        "id_venta",
        "fecha",
        "id_cliente",
        "id_producto",
        "id_vendedor",
        "ciudad",
        "cantidad",
        "precio_unitario",
        "descuento",
        "total",
        "metodo_pago",
    ]
    return df[columnas]


def se_conoce_la_mora_desde(fecha: pd.Series, plazo_dias: pd.Series) -> pd.Series:
    """Primer día en que ya se sabe si una compra al crédito fue morosa."""
    return fecha + pd.to_timedelta(plazo_dias + cat.DIAS_MOROSIDAD + 1, unit="D")


def generar_creditos(
    ventas: pd.DataFrame, clientes: pd.DataFrame, semilla: int = SEMILLA
) -> pd.DataFrame:
    """Compras al crédito: una fila por cliente y día, con lo que se sabía al vender y su pago.

    `moroso` y `dias_atraso` quedan vacíos si, a la fecha de corte, aún no se puede saber.
    El historial solo cuenta compras cuya mora ya se conocía el día de la venta. No se simula
    ningún bloqueo: un cliente puede seguir comprando al crédito aunque tenga deudas vencidas.
    """
    rng = rng_tabla("creditos", semilla)
    datos = clientes.set_index("id_cliente")
    riesgo = pd.Series(rng.normal(0, cat.MORA_DISPERSION_CLIENTE, len(datos)), index=datos.index)

    df = (
        ventas[ventas["metodo_pago"] == "Crédito"]
        .groupby(["id_cliente", "fecha"], as_index=False)["total"]
        .sum()
        .rename(columns={"total": "monto"})
        .sort_values(["fecha", "id_cliente"], kind="stable", ignore_index=True)
    )
    df["monto"] = df["monto"].round(2)
    df["tipo"] = df["id_cliente"].map(datos["tipo"])
    df["plazo_dias"] = df["tipo"].map(cat.PLAZO_CREDITO)
    df["antiguedad_anios"] = (
        (df["fecha"] - df["id_cliente"].map(datos["fecha_alta"])).dt.days / 365.25
    ).round(2)
    df["monto_sobre_limite"] = (df["monto"] / df["id_cliente"].map(datos["limite_credito"])).round(
        4
    )

    logit = (
        cat.MORA_BASE
        + cat.MORA_POR_MONTO * np.log(df["monto_sobre_limite"])
        + cat.MORA_POR_ANIO * df["antiguedad_anios"]
        + df["tipo"].map(cat.MORA_POR_TIPO)
        + df["id_cliente"].map(riesgo)
    )
    moroso = rng.random(len(df)) < 1 / (1 + np.exp(-logit.to_numpy()))
    # Atraso de quien no cae en mora: la mitad paga a tiempo y el resto se demora algo.
    leve = np.where(rng.random(len(df)) < 0.5, 0, rng.integers(1, cat.DIAS_MOROSIDAD + 1, len(df)))
    grave = cat.DIAS_MOROSIDAD + rng.geometric(1 / 30, len(df))
    atraso = np.where(moroso, grave, leve)

    se_sabe = se_conoce_la_mora_desde(df["fecha"], df["plazo_dias"])
    df["casos_previos"] = 0
    df["morosos_previos"] = 0
    for _, compras in df.groupby("id_cliente"):
        filas = compras.index.to_numpy()
        # El plazo es fijo por cliente: lo conocido crece con la fecha y se puede buscar en orden.
        conocidos = np.searchsorted(se_sabe[filas], compras["fecha"], side="right")
        acumulado = np.concatenate([[0], moroso[filas].cumsum()])
        df.loc[filas, "casos_previos"] = conocidos
        df.loc[filas, "morosos_previos"] = acumulado[conocidos]

    # El atraso solo se observa hasta el corte: una deuda aún impaga muestra lo que lleva.
    vence = df["fecha"] + pd.to_timedelta(df["plazo_dias"], unit="D")
    atraso = np.minimum(atraso, (cat.CORTE_CREDITOS - vence).dt.days.clip(lower=0))
    maduro = se_sabe <= cat.CORTE_CREDITOS
    df["dias_atraso"] = pd.Series(atraso, index=df.index, dtype="Int64").where(maduro)
    df["moroso"] = pd.Series(moroso.astype(int), index=df.index, dtype="Int64").where(maduro)
    df.insert(0, "id_credito", [f"K{i:05d}" for i in range(1, len(df) + 1)])
    return df[
        [
            "id_credito",
            "fecha",
            "id_cliente",
            "tipo",
            "monto",
            "plazo_dias",
            "antiguedad_anios",
            "monto_sobre_limite",
            "casos_previos",
            "morosos_previos",
            "dias_atraso",
            "moroso",
        ]
    ]


def generar_despachos(
    ventas: pd.DataFrame, clientes: pd.DataFrame, semilla: int = SEMILLA
) -> pd.DataFrame:
    """Despachos: una fila por cliente y día, con lo que se sabía al salir y si llegó tarde."""
    rng = rng_tabla("despachos", semilla)
    datos = clientes.set_index("id_cliente")
    mediana = datos["ciudad"].map(cat.DISTANCIA_MEDIANA)
    distancia = mediana * rng.lognormal(0, cat.DISTANCIA_DISPERSION, len(datos))
    distancia = distancia.clip(upper=cat.DISTANCIA_MAXIMA).round(1)

    df = (
        ventas.groupby(["id_cliente", "fecha"], as_index=False)
        .agg(lineas=("id_venta", "size"), presentaciones=("cantidad", "sum"))
        .sort_values(["fecha", "id_cliente"], kind="stable", ignore_index=True)
    )
    df["ciudad"] = df["id_cliente"].map(datos["ciudad"])
    df["tipo"] = df["id_cliente"].map(datos["tipo"])
    df["distancia_km"] = df["id_cliente"].map(distancia)
    prob_tercero = (cat.TERCERO_BASE + cat.TERCERO_POR_KM * df["distancia_km"]).clip(
        upper=cat.TERCERO_MAXIMO
    )
    tercero = rng.random(len(df)) < prob_tercero
    df["transportista"] = np.where(tercero, "Tercero", "Propio")

    mes = df["fecha"].dt.month
    lluvia = (df["ciudad"] == "Cusco") & mes.isin(cat.LLUVIA_MESES)
    lluvia &= df["distancia_km"] >= cat.LLUVIA_KM
    sabado_tercero = tercero & (df["fecha"].dt.dayofweek == 5)
    campana = mes.isin(cat.CAMPANA_MESES) & (df["presentaciones"] >= cat.CAMPANA_BULTOS)
    logit = (
        cat.TARDE_BASE
        + cat.TARDE_POR_KM * df["distancia_km"]
        + cat.TARDE_LLUVIA_CUSCO * lluvia
        + cat.TARDE_TERCERO_SABADO * sabado_tercero
        + cat.TARDE_CAMPANA_CARGA * campana
    )
    df["llego_tarde"] = (rng.random(len(df)) < 1 / (1 + np.exp(-logit.to_numpy()))).astype(int)
    df.insert(0, "id_despacho", [f"D{i:05d}" for i in range(1, len(df) + 1)])
    return df[
        [
            "id_despacho",
            "fecha",
            "id_cliente",
            "ciudad",
            "tipo",
            "distancia_km",
            "lineas",
            "presentaciones",
            "transportista",
            "llego_tarde",
        ]
    ]


def _referencia_de_dia(fecha_despacho: pd.Timestamp, fecha_ticket: pd.Timestamp) -> str:
    """Cómo nombra el cliente el día del despacho, según cuándo escribe."""
    if (fecha_ticket - fecha_despacho).days == 1:
        return "ayer"
    return cat.DIAS_SEMANA_TICKET[fecha_despacho.dayofweek]


def _texto_ticket(
    rng: np.random.Generator,
    categoria: str,
    otra: str | None,
    canal: str,
    fecha: pd.Timestamp,
    dia: str,
    tiempo: str,
) -> str:
    """Redacta un mensaje de cliente, a veces con dos temas y con escritura de WhatsApp."""

    def frase(tema: str) -> str:
        frases = cat.FRASES_TICKET[tema]
        if fecha.month not in cat.MESES_PANETON:
            frases = [f for f in frases if "panet" not in f.lower()]
        hay_nuevas = fecha >= cat.INICIO_FRASES_NUEVAS
        if hay_nuevas and rng.random() < cat.PROPORCION_FRASES_NUEVAS:
            frases = cat.FRASES_NUEVAS_TICKET[tema]
        return str(rng.choice(frases)).format(dia=dia, tiempo=tiempo, n=int(rng.integers(2, 9)))

    def unir(primera: str, segunda: str) -> str:
        return primera + (" " if primera.endswith("?") else ". ") + segunda

    def con_mayuscula(frase_inicial: str) -> str:
        pos = 1 if frase_inicial.startswith("¿") else 0
        return frase_inicial[:pos] + frase_inicial[pos].upper() + frase_inicial[pos + 1 :]

    texto = frase(categoria)
    if otra is not None:
        texto = unir(texto, "Además, " + frase(otra))
    saludo, cierre = rng.choice(cat.SALUDOS_TICKET), rng.choice(cat.CIERRES_TICKET)
    if not saludo:
        texto = con_mayuscula(texto)
    texto = saludo + texto
    if cierre:
        texto = unir(texto, cierre)
    elif canal != "WhatsApp" and not texto.endswith("?"):
        texto += "."
    if canal == "WhatsApp" and rng.random() < 0.5:
        texto = f" {texto.lower()} "
        for largo, corto in cat.ABREVIATURAS_TICKET.items():
            texto = texto.replace(largo, corto)
    return texto.strip()


def generar_tickets(despachos: pd.DataFrame, semilla: int = SEMILLA) -> pd.DataFrame:
    """Mensajes de clientes a Atención al Cliente, clasificados a mano en cinco categorías.

    Solo los tickets que nacen de una entrega tardía llevan `id_despacho`.
    """
    rng = rng_tabla("tickets", semilla)
    # Un ticket se escribe hasta 3 días después del despacho, sin pasar de la fecha de corte.
    candidatos = despachos[despachos["fecha"] <= cat.FIN - pd.Timedelta(days=3)]
    tardios = candidatos[candidatos["llego_tarde"] == 1]
    n_tarde = round(cat.N_TICKETS * cat.TICKETS_DE_TARDANZA)
    n_otros = cat.N_TICKETS - n_tarde
    base = pd.concat(
        [
            tardios.iloc[rng.choice(len(tardios), n_tarde, replace=False)],
            candidatos.iloc[rng.choice(len(candidatos), n_otros, replace=False)],
        ],
        ignore_index=True,
    )
    otras = list(cat.PESO_CATEGORIA_TICKET)
    categorias = ["Despacho"] * n_tarde + list(
        rng.choice(otras, n_otros, p=list(cat.PESO_CATEGORIA_TICKET.values()))
    )
    todas = ["Despacho", *otras]
    canales = rng.choice(
        list(cat.CANALES_TICKET), cat.N_TICKETS, p=list(cat.CANALES_TICKET.values())
    )
    fechas = base["fecha"] + pd.to_timedelta(rng.integers(1, 4, cat.N_TICKETS), unit="D")

    textos, etiquetas = [], []
    for fila, categoria, canal, fecha in zip(
        base["fecha"], categorias, canales, fechas, strict=True
    ):
        otra = None
        if rng.random() < cat.TICKETS_MIXTOS:
            otra = rng.choice([c for c in todas if c != categoria])
        dia = _referencia_de_dia(fila, fecha)
        pasados = (fecha - fila).days
        tiempo = "pasó un día" if pasados == 1 else f"pasaron {pasados} días"
        textos.append(_texto_ticket(rng, categoria, otra, canal, fecha, dia, tiempo))
        mal = rng.random() < cat.TICKETS_MAL_ETIQUETADOS
        etiquetas.append(rng.choice([c for c in todas if c != categoria]) if mal else categoria)

    df = pd.DataFrame(
        {
            "fecha": fechas,
            "id_cliente": base["id_cliente"],
            "id_despacho": base["id_despacho"].where(base.index < n_tarde),
            "canal": canales,
            "mensaje": textos,
            "categoria": etiquetas,
        }
    )
    df = df.sort_values("fecha", kind="stable", ignore_index=True)
    df.insert(0, "id_ticket", [f"T{i:05d}" for i in range(1, len(df) + 1)])
    return df


def generar_postulaciones(semilla: int = SEMILLA) -> pd.DataFrame:
    """Postulaciones a la empresa y si se llamó a entrevista, con un sesgo programado a propósito.

    El puntaje de la prueba se sortea igual para hombres y mujeres. La diferencia en las
    entrevistas viene de los coeficientes de `catalogos.py`: no describe a ninguna empresa real.
    """
    rng = rng_tabla("postulaciones", semilla)
    n = cat.N_POSTULACIONES
    cargos = rng.choice(list(cat.CARGOS_POSTULACION), n, p=list(cat.CARGOS_POSTULACION.values()))
    prob_mujer = pd.Series(cargos).map(cat.PROPORCION_MUJERES_POSTULACION).to_numpy()
    sexo = np.where(rng.random(n) < prob_mujer, "F", "M")
    sedes = rng.choice(list(cat.SEDES), n, p=list(cat.SEDES.values()))
    experiencia = rng.gamma(2.0, 2.0, n).round(1)
    puntaje = rng.normal(62, 14, n).clip(0, 100).round(0).astype(int)
    pausa = rng.exponential(pd.Series(sexo).map(cat.PAUSA_MEDIA_MESES).to_numpy()).round(0)
    viajar = rng.random(n) < pd.Series(sexo).map(cat.PROBABILIDAD_VIAJAR).to_numpy()

    sesgo = (sexo == "F") & np.isin(cargos, cat.CARGOS_CON_SESGO)
    logit = (
        cat.ENTREVISTA_BASE
        + cat.ENTREVISTA_POR_PUNTAJE * (puntaje - 60)
        + cat.ENTREVISTA_POR_ANIO * experiencia
        + cat.ENTREVISTA_POR_MES_PAUSA * pausa
        + cat.ENTREVISTA_POR_VIAJAR * viajar
        + cat.ENTREVISTA_SESGO_MUJER * sesgo
    )
    entrevistado = rng.random(n) < 1 / (1 + np.exp(-logit))
    df = pd.DataFrame(
        {
            "fecha": _fechas_aleatorias(
                rng, n, pd.Timestamp("2022-01-01"), pd.Timestamp("2025-12-31")
            ),
            "cargo": cargos,
            "sede": sedes,
            "sexo": sexo,
            "anios_experiencia": experiencia,
            "meses_sin_empleo": pausa.astype(int),
            "puede_viajar": viajar.astype(int),
            "puntaje_prueba": puntaje,
            "entrevistado": entrevistado.astype(int),
        }
    )
    df = df.sort_values("fecha", kind="stable", ignore_index=True)
    df.insert(0, "id_postulacion", [f"A{i:05d}" for i in range(1, n + 1)])
    return df


def generar_todo(semilla: int = SEMILLA) -> dict[str, pd.DataFrame]:
    """Genera todas las tablas limpias de la empresa."""
    productos = generar_productos(semilla)
    empleados = generar_empleados(semilla)
    clientes = generar_clientes(empleados, semilla)
    ventas = generar_ventas(productos, clientes, semilla)
    creditos = generar_creditos(ventas, clientes, semilla)
    despachos = generar_despachos(ventas, clientes, semilla)
    tickets = generar_tickets(despachos, semilla)
    postulaciones = generar_postulaciones(semilla)
    return {
        "productos": productos,
        "empleados": empleados,
        "clientes": clientes,
        "ventas": ventas,
        "creditos": creditos,
        "despachos": despachos,
        "tickets": tickets,
        "postulaciones": postulaciones,
    }
