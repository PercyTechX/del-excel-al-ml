import hashlib
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import distribuidora_andina as da
from distribuidora_andina import catalogos as cat
from distribuidora_andina.ensuciar import ensuciar_ventas
from distribuidora_andina.exportar import CODIFICACION, exportar
from distribuidora_andina.generar import (
    SEMILLA,
    generar_todo,
    rng_tabla,
    se_conoce_la_mora_desde,
)

DATOS = Path(__file__).resolve().parents[1] / "datos"
VERSIONES = f"numpy {np.__version__}, pandas {pd.__version__}"
# Huellas de los archivos que usan las temporadas 0 y 1: agregar tablas no debe cambiarlos,
# porque sus notebooks y videos muestran estas cifras.
HUELLAS_TEMPORADA_0 = {
    "creditos.csv": "f22407773a3ce9f8a9f7d7ef545ac50c6a19c0ed345ef50e2f28a4aec75bc6ed",
    "clientes.csv": "e85f1e1259107a94e4cfc0ebfa50ac9f3481d93fe8ed66a0c95ca29098f61b62",
    "empleados.csv": "14330a56774eb324f113fa3ab85148827b9bb71574a5af91feafa853a1252353",
    "productos.csv": "19a0eade7effa28167fc3075126d4557cf7a8248c5f260b79d58a9f0960c956b",
    "ventas_crudo.csv": "cabc5b4e68d08d864637d91a6702bd8710b9ee8b4a7f27563002253b03db9afc",
    "ventas.csv": "1e7e428627d68028e8d4e8def2c9761c606f45a370515a1d66163f6b8415ce10",
    "reporte_ventas_2025.xlsx": "68023383dbbe15a73c1327062d38214ec5731c09caa052474e7d2889102e2fdd",
}


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
    credito = tablas["ventas"][tablas["ventas"]["metodo_pago"] == "Crédito"]
    assert len(tablas["creditos"]) == len(credito[["id_cliente", "fecha"]].drop_duplicates())
    assert len(tablas["despachos"]) == len(
        tablas["ventas"][["id_cliente", "fecha"]].drop_duplicates()
    )
    assert len(tablas["tickets"]) == cat.N_TICKETS
    assert len(tablas["postulaciones"]) == cat.N_POSTULACIONES


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
        ("creditos", "id_credito"),
        ("despachos", "id_despacho"),
        ("tickets", "id_ticket"),
        ("postulaciones", "id_postulacion"),
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


@pytest.mark.parametrize(
    "nombre",
    [
        "productos",
        "empleados",
        "clientes",
        "ventas",
        "creditos",
        "despachos",
        "tickets",
        "postulaciones",
    ],
)
def test_archivos_publicados_coinciden_con_el_generador(tablas, nombre):
    publicado = pd.read_csv(DATOS / f"{nombre}.csv", encoding=CODIFICACION)
    generado = tablas[nombre].copy()
    for col in generado.select_dtypes("datetime").columns:
        generado[col] = generado[col].dt.strftime("%Y-%m-%d")
    for col in generado.select_dtypes("Int64").columns:
        generado[col] = generado[col].astype("float")
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


@pytest.mark.parametrize("archivo", HUELLAS_TEMPORADA_0)
def test_archivos_de_la_temporada_0_no_cambian(archivo):
    huella = hashlib.sha256((DATOS / archivo).read_bytes()).hexdigest()
    assert huella == HUELLAS_TEMPORADA_0[archivo]


def test_creditos_coinciden_con_las_ventas_al_credito(tablas):
    ventas, creditos = tablas["ventas"], tablas["creditos"]
    credito = ventas[ventas["metodo_pago"] == "Crédito"]
    assert creditos["monto"].sum() == pytest.approx(credito["total"].sum(), abs=0.01)


def test_mora_definida_por_los_dias_de_atraso(tablas):
    conocidos = tablas["creditos"].dropna(subset=["moroso"])
    assert ((conocidos["dias_atraso"] > cat.DIAS_MOROSIDAD) == (conocidos["moroso"] == 1)).all()


def test_creditos_sin_madurar_no_tienen_resultado(tablas):
    creditos = tablas["creditos"]
    se_sabe = se_conoce_la_mora_desde(creditos["fecha"], creditos["plazo_dias"])
    pendiente = se_sabe > cat.CORTE_CREDITOS
    assert pendiente.any()
    assert (creditos["moroso"].isna() == pendiente).all()
    assert (creditos["dias_atraso"].isna() == pendiente).all()


def test_el_atraso_no_mira_mas_alla_del_corte(tablas):
    creditos = tablas["creditos"].dropna(subset=["dias_atraso"])
    vence = creditos["fecha"] + pd.to_timedelta(creditos["plazo_dias"], unit="D")
    assert (creditos["dias_atraso"] <= (cat.CORTE_CREDITOS - vence).dt.days).all()


def test_historial_de_creditos_no_usa_el_futuro(tablas):
    """Recalcula el historial compra por compra, con solo lo que se sabía ese día."""
    creditos = tablas["creditos"]
    # El resultado real de todas las compras, antes de ocultar las que no maduraron.
    riesgo_oculto = creditos["moroso"].isna()
    se_sabe = se_conoce_la_mora_desde(creditos["fecha"], creditos["plazo_dias"])
    for _, cliente in creditos.groupby("id_cliente"):
        fechas = cliente["fecha"]
        conocido = se_sabe[cliente.index]
        for fila in cliente.itertuples():
            previas = conocido <= fila.fecha
            assert (fechas[previas] < fila.fecha).all()
            assert fila.casos_previos == previas.sum()
            # Lo que ya se conocía nunca es una compra sin madurar.
            assert not riesgo_oculto[cliente.index][previas].any()
            assert fila.morosos_previos == cliente.loc[previas, "moroso"].sum()


@pytest.fixture(scope="module")
def modelo_de_creditos():
    """La receta del temario de la Temporada 1, con las compras de prueba y sus probabilidades."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    c = pd.read_csv(DATOS / "creditos.csv", parse_dates=["fecha"], encoding=CODIFICACION)
    c["tasa"] = (c["morosos_previos"] / c["casos_previos"]).fillna(0)
    c["sin_historial"] = (c["casos_previos"] == 0).astype(int)
    c["log_monto"] = np.log(c["monto_sobre_limite"])
    corte = pd.Timestamp("2025-07-01")
    se_sabe = se_conoce_la_mora_desde(c["fecha"], c["plazo_dias"])
    entrena = (se_sabe <= corte) & c["moroso"].notna()
    prueba = (c["fecha"] >= corte) & c["moroso"].notna()

    def ajustar(columnas):
        x = pd.get_dummies(c[columnas], columns=["tipo"], dtype=float)
        modelo = make_pipeline(StandardScaler(), LogisticRegression())
        modelo.fit(x[entrena], c.loc[entrena, "moroso"])
        return modelo.predict_proba(x[prueba])[:, 1]

    base = ["log_monto", "antiguedad_anios", "tipo"]
    return (
        c.loc[prueba, "moroso"].astype(int),
        ajustar([*base, "tasa", "sin_historial"]),
        ajustar(base),
        c.loc[prueba, "tasa"],
    )


def test_cifras_del_temario_de_la_temporada_1(modelo_de_creditos):
    from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

    real, con_historial, _, tasa = modelo_de_creditos
    assert len(real) == 1531
    assert real.sum() == 223
    assert 1 - real.mean() == pytest.approx(0.854, abs=0.001)
    assert roc_auc_score(real, con_historial) == pytest.approx(0.71, abs=0.01)

    marcadas = con_historial >= 0.5
    assert (marcadas.sum(), real[marcadas].sum()) == (6, 2)
    assert accuracy_score(real, marcadas) == pytest.approx(0.853, abs=0.001)

    marcadas = con_historial >= 0.25
    assert (marcadas.sum(), real[marcadas].sum()) == (227, 85)
    assert accuracy_score(real, marcadas) == pytest.approx(0.817, abs=0.001)
    assert recall_score(real, marcadas) == pytest.approx(0.38, abs=0.005)
    assert precision_score(real, marcadas) == pytest.approx(0.37, abs=0.005)

    regla = tasa >= 0.3
    assert (regla.sum(), real[regla].sum()) == (271, 89)


def test_el_historial_aporta_al_modelo_de_creditos(modelo_de_creditos):
    from sklearn.metrics import roc_auc_score

    real, con_historial, sin_historial, _ = modelo_de_creditos
    assert roc_auc_score(real, con_historial) > roc_auc_score(real, sin_historial) + 0.03


def test_excel_tiene_las_hojas_esperadas(tablas):
    hojas = pd.read_excel(DATOS / "reporte_ventas_2025.xlsx", sheet_name=None)
    assert list(hojas) == ["Ventas", "Productos", "Clientes"]
    assert (hojas["Ventas"]["fecha"].dt.year == 2025).all()
    assert len(hojas["Productos"]) == len(tablas["productos"])


def test_csv_se_lee_sin_indicar_codificacion():
    df = pd.read_csv(DATOS / "ventas_crudo.csv", sep=";", nrows=5)
    assert "Método de Pago" in df.columns
