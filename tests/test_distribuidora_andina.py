from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import distribuidora_andina as da
from distribuidora_andina import catalogos as cat
from distribuidora_andina.ensuciar import ensuciar_ventas
from distribuidora_andina.exportar import CODIFICACION, exportar
from distribuidora_andina.generar import SEMILLA, generar_todo, rng_tabla

DATOS = Path(__file__).resolve().parents[1] / "datos"
VERSIONES = f"numpy {np.__version__}, pandas {pd.__version__}"


@pytest.fixture(scope="module")
def tablas():
    return generar_todo()


@pytest.fixture(scope="module")
def crudo(tablas):
    return ensuciar_ventas(tablas["ventas"], rng_tabla("crudo", SEMILLA))


def test_datos_basicos_de_la_empresa():
    assert da.EMPRESA == "Distribuidora Andina S.A.C."
    assert da.SIMBOLO_MONEDA == "S/"
    assert da.CIUDADES == tuple(cat.SEDES)


def test_es_reproducible(tablas):
    otra_vez = generar_todo()
    for nombre, df in tablas.items():
        pd.testing.assert_frame_equal(df, otra_vez[nombre])


def test_otra_semilla_da_otros_datos(tablas):
    assert not tablas["ventas"].equals(generar_todo(semilla=1)["ventas"])


def test_tamanos(tablas):
    assert len(tablas["productos"]) == len(cat.PRODUCTOS)
    assert len(tablas["empleados"]) == sum(cat.VENDEDORES_POR_SEDE.values())
    assert len(tablas["clientes"]) == cat.N_CLIENTES
    assert len(tablas["ventas"]) == cat.N_VENTAS


@pytest.mark.parametrize(
    "tabla, columna",
    [
        ("productos", "id_producto"),
        ("productos", "nombre"),
        ("empleados", "id_empleado"),
        ("empleados", "nombre"),
        ("clientes", "id_cliente"),
        ("clientes", "nombre"),
        ("ventas", "id_venta"),
    ],
)
def test_identificadores_unicos(tablas, tabla, columna):
    assert tablas[tabla][columna].is_unique


def test_integridad_referencial(tablas):
    v, c = tablas["ventas"], tablas["clientes"]
    assert v["id_cliente"].isin(c["id_cliente"]).all()
    assert v["id_producto"].isin(tablas["productos"]["id_producto"]).all()
    assert v["id_vendedor"].isin(tablas["empleados"]["id_empleado"]).all()
    assert c["id_vendedor"].isin(tablas["empleados"]["id_empleado"]).all()


def test_vendedor_y_cliente_de_la_misma_sede(tablas):
    c = tablas["clientes"].merge(tablas["empleados"], left_on="id_vendedor", right_on="id_empleado")
    assert (c["ciudad"] == c["sede"]).all()


def test_margen_de_distribuidora(tablas):
    p = tablas["productos"]
    margen = 1 - p["costo"] / p["precio"]
    assert margen.between(0.07, 0.16).all()


def test_nadie_compra_antes_de_ser_cliente(tablas):
    v = tablas["ventas"].merge(tablas["clientes"], on="id_cliente", suffixes=("", "_cliente"))
    assert (v["fecha"] >= v["fecha_alta"]).all()
    assert v["fecha"].between(cat.INICIO, cat.FIN).all()


def test_no_hay_ventas_en_feriados(tablas):
    assert not tablas["ventas"]["fecha"].isin(cat.FERIADOS).any()


def test_algunos_clientes_dejan_de_comprar(tablas):
    ultima_compra = tablas["ventas"].groupby("id_cliente")["fecha"].max()
    perdidos = (ultima_compra < pd.Timestamp("2025-10-01")).sum()
    esperados = cat.N_CLIENTES * cat.PROPORCION_CLIENTES_PERDIDOS
    assert 0.8 * esperados <= perdidos <= 1.3 * esperados


def test_totales_redondeados_como_excel(tablas):
    v = tablas["ventas"].sample(2000, random_state=0)
    for fila in v.itertuples():
        bruto = (
            Decimal(int(fila.cantidad))
            * Decimal(str(fila.precio_unitario))
            * (1 - Decimal(str(fila.descuento)))
        )
        esperado = float(bruto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        assert fila.total == esperado, fila


def test_descuentos_por_volumen(tablas):
    v = tablas["ventas"]
    assert (v.loc[v["cantidad"] >= 20, "descuento"] == 0.10).all()
    assert (v.loc[v["cantidad"].between(10, 19), "descuento"] == 0.05).all()
    assert (v.loc[v["cantidad"] < 10, "descuento"] == 0.0).all()


def test_estacionalidad(tablas):
    v = tablas["ventas"].merge(tablas["productos"], on="id_producto")
    mes = v["fecha"].dt.month
    por_mes = v.groupby(mes)["total"].sum()
    assert por_mes[12] > por_mes[7] > por_mes[2]

    por_anio = v.groupby(v["fecha"].dt.year)["total"].sum()
    assert por_anio[2025] > por_anio[2024]

    bebidas = v["categoria"] == "Bebidas"
    assert bebidas[mes == 2].mean() > bebidas[mes == 8].mean()  # más bebidas en verano

    paneton = v["nombre"] == "Panetón 900 g"
    assert paneton[mes.isin([11, 12])].sum() > 0.85 * paneton.sum()


def test_version_cruda_tiene_los_problemas_esperados(crudo):
    assert crudo.duplicated().sum() > 0
    assert crudo["Cantidad"].isna().sum() > 0
    assert crudo["Cantidad"].max() >= 100  # errores de tipeo
    assert crudo["Método de Pago"].isna().sum() > 0
    assert {"Yape", "efectivo"} <= set(crudo["Método de Pago"].dropna())
    assert crudo["Total"].str.startswith("S/ ").all()
    assert crudo["Total"].str.contains(",").any()  # hay montos con separador de miles
    fechas = crudo["Fecha"]
    assert fechas.str.match(r"\d{2}/\d{2}/\d{4}$").mean() > 0.95
    assert fechas.str.match(r"\d{4}-\d{2}-\d{2}$").any()
    assert {"lima", "LIMA", "Lima "} <= set(crudo["Ciudad"])


def test_duplicados_no_siempre_pegados(crudo):
    dup = crudo.duplicated(keep="first")
    pegados = dup & crudo.eq(crudo.shift()).all(axis=1)
    assert pegados.sum() < dup.sum()


@pytest.mark.parametrize("nombre", ["productos", "empleados", "clientes", "ventas"])
def test_archivos_publicados_coinciden_con_el_generador(tablas, nombre):
    publicado = pd.read_csv(DATOS / f"{nombre}.csv", encoding=CODIFICACION)
    generado = tablas[nombre].copy()
    for col in generado.select_dtypes("datetime").columns:
        generado[col] = generado[col].dt.strftime("%Y-%m-%d")
    try:
        pd.testing.assert_frame_equal(publicado, generado, check_dtype=False)
    except AssertionError as error:
        raise AssertionError(
            f"datos/{nombre}.csv no coincide con el generador ({VERSIONES}). "
            "Si cambiaste el generador, ejecuta `python -m distribuidora_andina`."
        ) from error


def test_archivos_crudo_y_excel_coinciden_con_el_generador(tmp_path):
    exportar(tmp_path)
    for archivo in ["ventas_crudo.csv", "reporte_ventas_2025.xlsx"]:
        assert (tmp_path / archivo).read_bytes() == (DATOS / archivo).read_bytes(), (
            f"datos/{archivo} no coincide con el generador ({VERSIONES}). "
            "Si cambiaste el generador, ejecuta `python -m distribuidora_andina`."
        )


def test_excel_tiene_las_hojas_esperadas(tablas):
    hojas = pd.read_excel(DATOS / "reporte_ventas_2025.xlsx", sheet_name=None)
    assert list(hojas) == ["Ventas", "Productos", "Clientes"]
    assert (hojas["Ventas"]["fecha"].dt.year == 2025).all()
    assert len(hojas["Productos"]) == len(tablas["productos"])


def test_csv_se_lee_sin_indicar_codificacion():
    df = pd.read_csv(DATOS / "ventas_crudo.csv", sep=";", nrows=5)
    assert "Método de Pago" in df.columns
