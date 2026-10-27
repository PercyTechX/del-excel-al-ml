"""Versión "cruda" de las ventas: los problemas típicos de un archivo exportado en la oficina.

Se usa en el episodio 0.5 (limpieza de datos). Problemas que incluye:

- Nombres de columna con mayúsculas, espacios y tildes.
- Filas duplicadas (cerca de la original, pero no siempre pegadas).
- Ciudades escritas de distintas formas ("lima ", "LIMA", "Lima").
- Métodos de pago escritos de distintas formas ("efectivo", "Yape" en vez de "Billetera digital").
- Fechas guardadas como texto, casi todas dd/mm/aaaa y unas pocas aaaa-mm-dd.
- Montos guardados como texto con símbolo de moneda y separador de miles ("S/ 1,250.50").
- Descuentos como texto ("5%").
- Celdas vacías en cantidad y método de pago.
- Unas pocas cantidades absurdas por un error de tipeo (dos ceros de más).
"""

import numpy as np
import pandas as pd

PROPORCION_DUPLICADOS = 0.015
PROPORCION_CIUDAD_MAL_ESCRITA = 0.10
PROPORCION_PAGO_MAL_ESCRITO = 0.08
PROPORCION_FECHA_OTRO_FORMATO = 0.01
PROPORCION_VACIOS_PAGO = 0.03
PROPORCION_VACIOS_CANTIDAD = 0.01
N_ERRORES_DE_TIPEO = 5

COLUMNAS = {
    "id_venta": "Nro Venta",
    "fecha": "Fecha",
    "id_cliente": "Cliente",
    "id_producto": "Producto",
    "id_vendedor": "Vendedor",
    "ciudad": "Ciudad",
    "cantidad": "Cantidad",
    "precio_unitario": "Precio Unitario",
    "descuento": "Descuento",
    "total": "Total",
    "metodo_pago": "Método de Pago",
}


def _como_soles(valor: float) -> str:
    return f"S/ {valor:,.2f}"


def _variar_texto(rng: np.random.Generator, textos: np.ndarray) -> list[str]:
    variante = rng.choice(["minusculas", "mayusculas", "espacio"], len(textos))
    return [
        t.lower() if v == "minusculas" else t.upper() if v == "mayusculas" else f"{t} "
        for t, v in zip(textos, variante, strict=True)
    ]


def ensuciar_ventas(ventas: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Devuelve una copia de `ventas` con los problemas descritos en el módulo."""
    df = ventas.copy()
    n = len(df)

    mal = rng.random(n) < PROPORCION_CIUDAD_MAL_ESCRITA
    df.loc[mal, "ciudad"] = _variar_texto(rng, df.loc[mal, "ciudad"].to_numpy())

    mal = rng.random(n) < PROPORCION_PAGO_MAL_ESCRITO
    pagos = df.loc[mal, "metodo_pago"].to_numpy()
    billetera = rng.choice(["Yape", "Plin", "yape"], len(pagos))
    variados = _variar_texto(rng, pagos)
    df.loc[mal, "metodo_pago"] = np.where(pagos == "Billetera digital", billetera, variados)

    df["cantidad"] = df["cantidad"].astype("Int64")
    tipeo = rng.choice(n, N_ERRORES_DE_TIPEO, replace=False)
    df.loc[tipeo, "cantidad"] = df.loc[tipeo, "cantidad"] * 100
    df.loc[rng.random(n) < PROPORCION_VACIOS_CANTIDAD, "cantidad"] = pd.NA
    df.loc[rng.random(n) < PROPORCION_VACIOS_PAGO, "metodo_pago"] = None

    otro_formato = rng.random(n) < PROPORCION_FECHA_OTRO_FORMATO
    df["fecha"] = np.where(
        otro_formato, df["fecha"].dt.strftime("%Y-%m-%d"), df["fecha"].dt.strftime("%d/%m/%Y")
    )
    df["precio_unitario"] = df["precio_unitario"].map(_como_soles)
    df["total"] = df["total"].map(_como_soles)
    df["descuento"] = (df["descuento"] * 100).round().astype(int).astype(str) + "%"

    # Cada duplicado aparece unas filas después de su original.
    duplicados = df.sample(frac=PROPORCION_DUPLICADOS, random_state=rng)
    orden = np.concatenate(
        [
            np.arange(n, dtype=float),
            duplicados.index.to_numpy() + rng.integers(1, 30, len(duplicados)) + 0.5,
        ]
    )
    df = pd.concat([df, duplicados], ignore_index=True)
    df = df.iloc[np.argsort(orden, kind="stable")].reset_index(drop=True)

    return df.rename(columns=COLUMNAS)
