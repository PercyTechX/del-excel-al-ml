"""Generación de las tablas de Distribuidora Andina S.A.C.

Cada tabla usa su propio generador aleatorio, derivado de la semilla general.
Así, agregar o cambiar una tabla no altera los datos de las demás.
"""

import numpy as np
import pandas as pd

from . import catalogos as cat

SEMILLA = 2024

# Número fijo por tabla para derivar su generador aleatorio.
_FLUJO = {"productos": 1, "empleados": 2, "clientes": 3, "ventas": 4, "crudo": 5}


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


def generar_todo(semilla: int = SEMILLA) -> dict[str, pd.DataFrame]:
    """Genera todas las tablas limpias de la empresa."""
    productos = generar_productos(semilla)
    empleados = generar_empleados(semilla)
    clientes = generar_clientes(empleados, semilla)
    ventas = generar_ventas(productos, clientes, semilla)
    return {"productos": productos, "empleados": empleados, "clientes": clientes, "ventas": ventas}
