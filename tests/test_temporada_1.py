"""Comprueba que las funciones de los notebooks y las cifras del temario sigan vigentes."""

import json
import re
from pathlib import Path

import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "datos"
NOTEBOOKS = sorted(RAIZ.glob("temporada-1/*/*.ipynb"))
FUNCIONES = [
    "por_cliente_y_mes",
    "tabla_de_pronostico",
    "preparar_x",
    "preparar_creditos",
    "costo_total",
    "pronosticar_cartera",
    "limpiar_ventas",
]


def funcion(ruta, nombre):
    """El código de la función `nombre` en un notebook, si la tiene."""
    celdas = json.loads(ruta.read_text(encoding="utf-8"))["cells"]
    for celda in celdas:
        texto = "".join(celda["source"])
        hallada = re.search(rf"^def {nombre}\(.*?(?=^\S|\Z)", texto, re.M | re.S)
        if celda["cell_type"] == "code" and hallada:
            return hallada.group().rstrip()
    return None


@pytest.mark.parametrize("nombre", FUNCIONES)
def test_las_funciones_copiadas_son_iguales(nombre):
    copias = {funcion(ruta, nombre) for ruta in NOTEBOOKS} - {None}
    assert len(copias) == 1


@pytest.fixture(scope="module")
def tablas():
    espacio = {"pd": pd}
    primero = NOTEBOOKS[0].parents[1] / "05-mas-variables-y-la-temporada" / "clase.ipynb"
    for nombre in ["tabla_de_pronostico", "preparar_x"]:
        exec(funcion(primero, nombre), espacio)
    ventas = pd.read_csv(DATOS / "ventas.csv")
    clientes = pd.read_csv(DATOS / "clientes.csv")
    tabla = espacio["tabla_de_pronostico"](ventas, clientes)
    del_2024 = ventas[ventas["fecha"].str[:4] == "2024"]
    por_mes = del_2024.groupby(del_2024["fecha"].str[5:7].astype(int))["total"].sum()
    return ventas, tabla, por_mes / por_mes.mean(), espacio["preparar_x"]


def predecir(tabla, indice, preparar_x, hasta, desde):
    entreno, prueba = tabla[tabla["mes"] < hasta], tabla[desde(tabla)]
    numeros, textos = ["mes_anterior", "promedio_3"], ["tipo", "ciudad", "numero_mes"]
    x_entreno = preparar_x(entreno, numeros, textos)
    x_prueba = preparar_x(prueba, numeros, textos, x_entreno.columns)
    modelo = LinearRegression().fit(x_entreno, entreno["total"])
    return prueba.assign(
        regresion=modelo.predict(x_prueba),
        regla_indice=prueba["promedio_6"] * prueba["numero_mes"].map(indice),
    )


def test_la_recta_del_episodio_1_2(tablas):
    ventas = tablas[0]
    mensual = ventas.groupby(["id_cliente", ventas["fecha"].str[:7]]).agg(
        lineas=("total", "size"), total=("total", "sum")
    )
    modelo = LinearRegression().fit(mensual[["lineas"]], mensual["total"])
    assert len(mensual) == 6459
    assert modelo.coef_[0] == pytest.approx(325.5, abs=0.1)
    assert modelo.intercept_ == pytest.approx(-417.1, abs=0.1)
    assert modelo.score(mensual[["lineas"]], mensual["total"]) == pytest.approx(0.76, abs=0.01)


def test_comparacion_de_julio_a_diciembre(tablas):
    _, tabla, indice, preparar_x = tablas
    prueba = predecir(tabla, indice, preparar_x, "2025-07", lambda t: t["mes"] >= "2025-07")
    errores = {
        columna: round(mean_absolute_error(prueba["total"], prueba[columna]))
        for columna in ["promedio_3", "promedio_6", "regla_indice", "regresion"]
    }
    assert errores == {"promedio_3": 889, "promedio_6": 855, "regla_indice": 827, "regresion": 921}

    cartera = prueba.groupby(["id_vendedor", "mes"])[
        ["total", "promedio_6", "regla_indice", "regresion"]
    ].sum()
    assert round(mean_absolute_error(cartera["total"], cartera["promedio_6"])) == 7704
    assert round(mean_absolute_error(cartera["total"], cartera["regla_indice"])) == 4963
    assert round(mean_absolute_error(cartera["total"], cartera["regresion"])) == 4819


def test_pronostico_de_diciembre_del_miniproyecto(tablas):
    _, tabla, indice, preparar_x = tablas
    prueba = predecir(tabla, indice, preparar_x, "2025-12", lambda t: t["mes"] == "2025-12")
    cartera = prueba.groupby("id_vendedor")[
        ["total", "promedio_6", "regla_indice", "regresion"]
    ].sum()
    assert round(mean_absolute_error(cartera["total"], cartera["promedio_6"])) == 14256
    assert round(mean_absolute_error(cartera["total"], cartera["regla_indice"])) == 7316
    assert round(mean_absolute_error(cartera["total"], cartera["regresion"])) == 6090


def test_sobreajuste_del_episodio_1_6(tablas):
    _, tabla, _, preparar_x = tablas
    tabla = tabla.assign(
        cliente_trimestre=tabla["id_cliente"]
        + "-"
        + ((tabla["numero_mes"] - 1) // 3 + 1).astype(str)
    )
    entreno, prueba = tabla[tabla["mes"] < "2025-07"], tabla[tabla["mes"] >= "2025-07"]
    numeros = ["mes_anterior", "promedio_3"]
    textos = ["tipo", "ciudad", "numero_mes", "cliente_trimestre"]
    x_entreno = preparar_x(entreno, numeros, textos)
    x_prueba = preparar_x(prueba, numeros, textos, x_entreno.columns)
    modelo = LinearRegression().fit(x_entreno, entreno["total"])

    assert x_entreno.shape[1] == 1188
    assert round(mean_absolute_error(entreno["total"], modelo.predict(x_entreno))) == 570
    assert round(mean_absolute_error(prueba["total"], modelo.predict(x_prueba))) == 1346
