"""Datos y cifras del temario de la Temporada 2."""

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from distribuidora_andina import catalogos as cat
from distribuidora_andina.generar import (
    generar_postulaciones,
    generar_todo,
    se_conoce_la_mora_desde,
)

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "datos"
NOTEBOOKS = sorted(RAIZ.glob("temporada-2/*/*.ipynb"))
FUNCIONES = [
    "preparar_despachos",
    "parte_encontrada",
    "encontrados",
    "calendario",
    "tres_pronosticos",
    "probar_en_ventanas",
    "resumen_de_clientes",
    "llamados",
    "mujeres_que_llamaria",
    "categoria_por_palabras",
    "reporte_de_la_manana",
]
PALABRAS_CLAVE = [
    ("Facturación", "factura|boleta|comprobante|ruc|igv|guía"),
    ("Cobranza", "cobr|pag|pague|deud|debo|depósit|deposit|voucher|estado de cuenta"),
    ("Despacho", "pedido|llega|llego|camión|repartidor|despacho|entrega|chofer|mercadería"),
    ("Producto", "vencid|rot|devol|abollad|caja|vino|derram|equivocad"),
]
FRASES_NUEVAS = (
    "movilidad|la unidad|cpe|emitieron el doc|malogrado|humedad|abono|saldo pendiente|"
    "lista de precios|busco proveedor"
)


@pytest.fixture(scope="module")
def ventas():
    return pd.read_csv(DATOS / "ventas.csv", parse_dates=["fecha"])


@pytest.fixture(scope="module")
def despachos():
    return pd.read_csv(DATOS / "despachos.csv", parse_dates=["fecha"])


@pytest.fixture(scope="module")
def tickets():
    return pd.read_csv(DATOS / "tickets.csv", parse_dates=["fecha"])


@pytest.fixture(scope="module")
def postulaciones():
    return pd.read_csv(DATOS / "postulaciones.csv", parse_dates=["fecha"])


def entradas_numericas(df):
    x = pd.get_dummies(df[["ciudad", "tipo", "transportista"]], dtype=int)
    x = x.drop(columns=["ciudad_Lima", "tipo_Bodega", "transportista_Propio"])
    x["mes"] = df["fecha"].dt.month
    x["dia"] = df["fecha"].dt.dayofweek
    return x.join(df[["distancia_km", "lineas", "presentaciones"]])


def entradas_con_categorias(df):
    x = entradas_numericas(df).drop(columns=["mes", "dia"])
    for mes in range(1, 13):
        x[f"mes_{mes}"] = (df["fecha"].dt.month == mes).astype(int)
    for dia in range(7):
        x[f"dia_{dia}"] = (df["fecha"].dt.dayofweek == dia).astype(int)
    return x


def parte_encontrada(df, prob, vigilar=0.10):
    """Tardíos encontrados si cada día solo se vigila esa parte, sin mirar otros días."""
    orden = df[["fecha", "llego_tarde"]].assign(
        prob=prob, azar=np.random.default_rng(0).random(len(df))
    )
    orden = orden.sort_values(["fecha", "prob", "azar"], ascending=[True, False, True])
    puesto = orden.groupby("fecha").cumcount()
    cupo = (orden.groupby("fecha")["fecha"].transform("size") * vigilar).round().clip(lower=1)
    return orden.loc[puesto < cupo, "llego_tarde"].sum() / orden["llego_tarde"].sum()


def test_despachos_coinciden_con_las_ventas(despachos, ventas):
    por_dia = ventas.groupby(["id_cliente", "fecha"]).agg(
        presentaciones=("cantidad", "sum"), lineas=("id_venta", "size")
    )
    propios = despachos.set_index(["id_cliente", "fecha"])[["presentaciones", "lineas"]]
    pd.testing.assert_frame_equal(propios.sort_index(), por_dia.sort_index(), check_dtype=False)


def test_despachos_coinciden_con_los_clientes(despachos):
    clientes = pd.read_csv(DATOS / "clientes.csv").set_index("id_cliente")
    assert (despachos["ciudad"] == despachos["id_cliente"].map(clientes["ciudad"])).all()
    assert (despachos["tipo"] == despachos["id_cliente"].map(clientes["tipo"])).all()


def test_cada_cliente_tiene_una_sola_distancia(despachos):
    assert (despachos.groupby("id_cliente")["distancia_km"].nunique() == 1).all()
    assert despachos["distancia_km"].max() <= cat.DISTANCIA_MAXIMA


def test_tickets_con_despacho_vienen_de_una_tardanza(tickets, despachos):
    con_despacho = tickets.dropna(subset=["id_despacho"])
    assert len(con_despacho) == round(cat.N_TICKETS * cat.TICKETS_DE_TARDANZA)
    origen = despachos.set_index("id_despacho").loc[con_despacho["id_despacho"]]
    assert (origen["llego_tarde"] == 1).all()
    assert (con_despacho["id_cliente"].to_numpy() == origen["id_cliente"].to_numpy()).all()
    dias = con_despacho["fecha"].to_numpy() - origen["fecha"].to_numpy()
    assert ((dias >= np.timedelta64(1, "D")) & (dias <= np.timedelta64(3, "D"))).all()


def test_tickets_dentro_del_periodo_y_de_clientes_reales(tickets):
    clientes = pd.read_csv(DATOS / "clientes.csv")
    assert tickets["id_cliente"].isin(clientes["id_cliente"]).all()
    assert tickets["fecha"].between(cat.INICIO, cat.FIN).all()
    assert tickets["categoria"].nunique() == 5


def test_textos_de_tickets_bien_escritos(tickets):
    mensajes = tickets["mensaje"].str.lower()
    assert not mensajes.str.contains(r"\?\.").any()
    assert not mensajes.str.contains("por favor. por favor").any()
    assert not mensajes.str.contains(r"ya pas[oó] \d").any()
    assert mensajes.str.contains("porfa").any()
    fuera_de_temporada = ~tickets["fecha"].dt.month.isin(cat.MESES_PANETON)
    assert not mensajes[fuera_de_temporada].str.contains("panet").any()
    previos = mensajes[tickets["fecha"] < cat.INICIO_FRASES_NUEVAS]
    assert not previos.str.contains(FRASES_NUEVAS).any()


def resultados_de_despachos(despachos):
    previo = despachos[despachos["fecha"] < "2025-07-01"]
    prueba = despachos[despachos["fecha"] >= "2025-07-01"]

    def encontrados(modelo, entradas):
        modelo.fit(entradas(previo), previo["llego_tarde"])
        return parte_encontrada(prueba, modelo.predict_proba(entradas(prueba))[:, 1])

    logistica = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    return {
        "regresion": encontrados(logistica, entradas_con_categorias),
        "arbol_3": encontrados(
            DecisionTreeClassifier(max_depth=3, random_state=0), entradas_numericas
        ),
        "arbol_6": encontrados(
            DecisionTreeClassifier(max_depth=6, random_state=0), entradas_numericas
        ),
    }


def test_cifras_del_arbol_contra_la_regresion(despachos):
    entrena = despachos[despachos["fecha"] < "2025-01-01"]
    valida = despachos[despachos["fecha"].between("2025-01-01", "2025-06-30")]
    por_profundidad = {}
    for profundidad in [2, 3, 4, 5, 6, 8, 10]:
        arbol = DecisionTreeClassifier(max_depth=profundidad, random_state=0)
        arbol.fit(entradas_numericas(entrena), entrena["llego_tarde"])
        prob = arbol.predict_proba(entradas_numericas(valida))[:, 1]
        por_profundidad[profundidad] = parte_encontrada(valida, prob)
    assert max(por_profundidad, key=por_profundidad.get) == 6

    resultados = resultados_de_despachos(despachos)
    assert resultados["regresion"] == pytest.approx(0.23, abs=0.005)
    assert resultados["arbol_3"] == pytest.approx(0.26, abs=0.005)
    assert resultados["arbol_6"] == pytest.approx(0.29, abs=0.005)


def test_el_bosque_empata_y_sin_limite_empeora(despachos):
    previo = despachos[despachos["fecha"] < "2025-07-01"]
    prueba = despachos[despachos["fecha"] >= "2025-07-01"]

    def encontrados(modelo):
        modelo.fit(entradas_numericas(previo), previo["llego_tarde"])
        return parte_encontrada(prueba, modelo.predict_proba(entradas_numericas(prueba))[:, 1])

    bosque = RandomForestClassifier(200, min_samples_leaf=20, random_state=0, n_jobs=-1)
    assert encontrados(bosque) == pytest.approx(0.29, abs=0.005)
    assert encontrados(DecisionTreeClassifier(random_state=0)) == pytest.approx(0.20, abs=0.01)


@pytest.mark.parametrize("semilla", [1, 2, 3])
def test_el_arbol_gana_a_la_regresion_con_otras_semillas(semilla):
    tablas = generar_todo(semilla)
    resultados = resultados_de_despachos(tablas["despachos"])
    assert resultados["regresion"] < resultados["arbol_3"] < resultados["arbol_6"] + 0.01
    assert resultados["arbol_6"] - resultados["regresion"] > 0.03


def test_la_tardanza_responde_a_las_reglas_programadas(despachos):
    mes = despachos["fecha"].dt.month
    lluvia = (despachos["ciudad"] == "Cusco") & mes.isin(cat.LLUVIA_MESES)
    lluvia &= despachos["distancia_km"] >= cat.LLUVIA_KM
    sabado = (despachos["transportista"] == "Tercero") & (despachos["fecha"].dt.dayofweek == 5)
    campana = mes.isin(cat.CAMPANA_MESES) & (despachos["presentaciones"] >= cat.CAMPANA_BULTOS)
    ninguna = ~(lluvia | sabado | campana)
    base = despachos.loc[ninguna, "llego_tarde"].mean()
    assert base < 0.06
    for regla in (lluvia, sabado, campana):
        assert despachos.loc[regla, "llego_tarde"].mean() > 0.3


def test_en_creditos_sin_limite_es_el_peor():
    creditos = pd.read_csv(DATOS / "creditos.csv", parse_dates=["fecha"])
    se_sabe = se_conoce_la_mora_desde(creditos["fecha"], creditos["plazo_dias"])
    entrena = creditos[se_sabe <= "2025-07-01"]
    prueba = creditos[(creditos["fecha"] >= "2025-07-01") & creditos["moroso"].notna()]

    def entradas(df):
        previos = df["casos_previos"].replace(0, np.nan)
        return pd.DataFrame(
            {
                "monto": np.log(df["monto_sobre_limite"]),
                "antiguedad": df["antiguedad_anios"],
                "tasa": (df["morosos_previos"] / previos).fillna(0),
                "sin_historial": (df["casos_previos"] == 0).astype(int),
                "bodega": (df["tipo"] == "Bodega").astype(int),
                "minimarket": (df["tipo"] == "Minimarket").astype(int),
            }
        )

    def encontrados(modelo):
        modelo.fit(entradas(entrena), entrena["moroso"].astype(int))
        orden = prueba.assign(
            prob=modelo.predict_proba(entradas(prueba))[:, 1],
            azar=np.random.default_rng(0).random(len(prueba)),
            mes=prueba["fecha"].dt.to_period("M"),
            real=prueba["moroso"].astype(int),
        ).sort_values(["mes", "prob", "azar"], ascending=[True, False, True])
        puesto = orden.groupby("mes").cumcount()
        cupo = (orden.groupby("mes")["mes"].transform("size") * 0.10).round()
        return orden.loc[puesto < cupo, "real"].sum() / orden["real"].sum()

    logistica = encontrados(make_pipeline(StandardScaler(), LogisticRegression()))
    arbol = encontrados(DecisionTreeClassifier(max_depth=3, random_state=0))
    sin_limite = encontrados(DecisionTreeClassifier(random_state=0))
    assert logistica == pytest.approx(0.30, abs=0.005)
    assert arbol == pytest.approx(0.26, abs=0.005)
    # Sin límite, el resultado cambia con el orden de las columnas.
    assert sin_limite == pytest.approx(0.13, abs=0.015)
    assert sin_limite < min(logistica, arbol)


def categoria_por_palabras(mensaje):
    mensaje = mensaje.lower()
    for categoria, palabras in PALABRAS_CLAVE:
        if re.search(palabras, mensaje):
            return categoria
    return "Consulta comercial"


def test_cifras_de_tickets(tickets):
    entrena = tickets[tickets["fecha"] < "2025-07-01"]
    prueba = tickets[tickets["fecha"] >= "2025-07-01"]
    conteo = CountVectorizer()
    modelo = LogisticRegression(max_iter=2000).fit(
        conteo.fit_transform(entrena["mensaje"]), entrena["categoria"]
    )
    predicho = pd.Series(modelo.predict(conteo.transform(prueba["mensaje"])), prueba.index)
    acierta = predicho == prueba["categoria"]
    nuevas = prueba["mensaje"].str.lower().str.contains(FRASES_NUEVAS)
    mixtos = prueba["mensaje"].str.contains("demás,")

    assert len(prueba) == 967
    assert acierta.mean() == pytest.approx(0.83, abs=0.005)
    assert (nuevas & ~mixtos).sum() == 135 and (mixtos & ~nuevas).sum() == 72
    assert (mixtos & nuevas).sum() == 44 and (~mixtos & ~nuevas).sum() == 716
    assert acierta[nuevas & ~mixtos].mean() == pytest.approx(0.47, abs=0.005)
    assert acierta[mixtos & ~nuevas].mean() == pytest.approx(0.46, abs=0.005)
    assert acierta[~nuevas & ~mixtos].mean() == pytest.approx(0.96, abs=0.005)
    comun = (prueba["categoria"] == entrena["categoria"].mode()[0]).mean()
    assert comun == pytest.approx(0.22, abs=0.005)
    reglas = prueba["mensaje"].map(categoria_por_palabras) == prueba["categoria"]
    assert reglas.mean() == pytest.approx(0.67, abs=0.005)


def mujeres_llamadas(postulaciones):
    """Mujeres llamadas en 2025 por cada quien elige, con tantos llamados por cargo como hubo."""
    entrena = postulaciones[postulaciones["fecha"] < "2025-01-01"]
    prueba = postulaciones[postulaciones["fecha"] >= "2025-01-01"]

    def elegir(puntajes):
        elegidos = pd.Series(False, prueba.index)
        for _, grupo in prueba.groupby("cargo"):
            orden = puntajes[grupo.index].sort_values(ascending=False, kind="stable").index
            elegidos[orden[: int(grupo["entrevistado"].sum())]] = True
        return int(elegidos[prueba["sexo"] == "F"].sum())

    def imitando(columnas):
        xa = pd.get_dummies(entrena[columnas], dtype=int)
        xb = pd.get_dummies(prueba[columnas], dtype=int).reindex(columns=xa.columns, fill_value=0)
        modelo = make_pipeline(StandardScaler(), LogisticRegression())
        modelo.fit(xa, entrena["entrevistado"])
        return elegir(pd.Series(modelo.predict_proba(xb)[:, 1], prueba.index))

    base = ["cargo", "anios_experiencia", "puntaje_prueba"]
    indicadores = ["meses_sin_empleo", "puede_viajar"]
    sorteo = sum(
        grupo["entrevistado"].sum() * (grupo["sexo"] == "F").mean()
        for _, grupo in prueba.groupby("cargo")
    )
    return {
        "sorteo": sorteo,
        "reclutador": int(prueba.loc[prueba["sexo"] == "F", "entrevistado"].sum()),
        "con_sexo": imitando(base + indicadores + ["sexo"]),
        "sin_sexo": imitando(base + indicadores),
        "sin_indicadores": imitando(base),
    }


def test_cifras_de_etica(postulaciones):
    llamadas = mujeres_llamadas(postulaciones)
    assert llamadas["sorteo"] == pytest.approx(72, abs=0.5)
    assert llamadas["reclutador"] == 35
    assert llamadas["con_sexo"] == 26
    assert llamadas["sin_sexo"] == 41
    assert llamadas["sin_indicadores"] == 72


def test_el_puntaje_es_igual_y_aun_asi_hay_brecha(postulaciones):
    medias = postulaciones.groupby("sexo")["puntaje_prueba"].mean()
    assert abs(medias["F"] - medias["M"]) < 1
    altos = postulaciones[postulaciones["puntaje_prueba"] >= 75]
    tasas = altos.pivot_table(index="cargo", columns="sexo", values="entrevistado")
    assert tasas.loc["Asistente administrativo", "F"] == pytest.approx(0.39, abs=0.01)
    assert tasas.loc["Asistente administrativo", "M"] == pytest.approx(0.65, abs=0.01)
    assert (tasas["F"] < tasas["M"]).all()
    # En Asistente no hay sesgo directo programado: la brecha llega por los dos indicadores.
    assert "Asistente administrativo" not in cat.CARGOS_CON_SESGO
    medias = postulaciones.groupby("sexo")[["meses_sin_empleo", "puede_viajar"]].mean()
    assert medias.loc["F", "meses_sin_empleo"] > 2 * medias.loc["M", "meses_sin_empleo"]
    assert medias.loc["F", "puede_viajar"] < medias.loc["M", "puede_viajar"]


def test_afirmaciones_de_etica_con_30_semillas():
    razones = pd.DataFrame(
        [mujeres_llamadas(generar_postulaciones(semilla)) for semilla in range(1, 31)]
    )
    assert (razones["con_sexo"] < razones["reclutador"]).all()
    assert (razones["sin_sexo"] < razones["sorteo"]).all()
    assert (razones["sin_sexo"] <= razones["reclutador"]).sum() == 23
    frente_al_sorteo = razones["sin_indicadores"] / razones["sorteo"]
    assert frente_al_sorteo.between(0.85, 1.16).all()


def test_en_asistente_la_direccion_de_la_brecha_es_estable():
    for semilla in range(1, 31):
        postulaciones = generar_postulaciones(semilla)
        altos = postulaciones[
            (postulaciones["puntaje_prueba"] >= 75)
            & (postulaciones["cargo"] == "Asistente administrativo")
        ]
        tasas = altos.groupby("sexo")["entrevistado"].mean()
        assert tasas["F"] < tasas["M"]


def errores_de_series(ventas):
    serie = ventas.groupby("fecha")["total"].sum().asfreq("D", fill_value=0)

    def es_feriado(indice):
        return indice.isin(cat.FERIADOS)

    def calendario(indice):
        x = pd.DataFrame(index=indice)
        for dia in range(7):
            x[f"dia_{dia}"] = (indice.dayofweek == dia).astype(int)
        for mes in range(1, 13):
            x[f"mes_{mes}"] = (indice.month == mes).astype(int)
        x["tendencia"] = (indice - cat.INICIO).days
        return x

    def sin_feriados(tramo):
        return tramo[~es_feriado(tramo.index)]

    errores = []
    for mes in pd.period_range("2025-07", "2025-12", freq="M"):
        inicio = mes.start_time
        dias = serie[inicio : mes.end_time.normalize()]
        previo = serie[: inicio - pd.Timedelta(days=1)]
        entrena = sin_feriados(previo)
        modelo = LinearRegression().fit(calendario(entrena.index), entrena)
        regresion = pd.Series(modelo.predict(calendario(dias.index)), dias.index)
        regresion = regresion.where(~es_feriado(dias.index), 0)

        ultimas = sin_feriados(previo[previo.index >= inicio - pd.Timedelta(days=56)])
        por_dia = ultimas.groupby(ultimas.index.dayofweek).mean()
        ocho = pd.Series(dias.index.dayofweek.map(por_dia), dias.index).where(
            ~es_feriado(dias.index), 0
        )
        hace_un_anio = inicio - pd.Timedelta(days=364)
        tramo = serie[hace_un_anio - pd.Timedelta(days=56) : hace_un_anio - pd.Timedelta(days=1)]
        mismo_mes = serie[(serie.index.year == 2024) & (serie.index.month == mes.month)]
        indice = sin_feriados(mismo_mes).mean() / sin_feriados(tramo).mean()
        regla = ocho * indice
        errores.append(
            {
                "regresion": (dias - regresion).abs().mean(),
                "regla": (dias - regla).abs().mean(),
                "ocho_semanas": (dias - ocho).abs().mean(),
                "regresion_mes": abs(dias.sum() - regresion.sum()),
                "regla_mes": abs(dias.sum() - regla.sum()),
            }
        )
    return pd.DataFrame(errores).mean()


def test_cifras_de_series(ventas):
    medias = errores_de_series(ventas)
    assert medias["ocho_semanas"] == pytest.approx(4331, abs=5)
    assert medias["regla"] == pytest.approx(2935, abs=5)
    assert medias["regresion"] == pytest.approx(2875, abs=5)
    assert medias["regla_mes"] == pytest.approx(35970, abs=50)
    assert medias["regresion_mes"] == pytest.approx(28280, abs=50)


@pytest.mark.parametrize("semilla", [1, 2, 3])
def test_el_calendario_ayuda_con_otras_semillas(semilla):
    medias = errores_de_series(generar_todo(semilla)["ventas"])
    assert medias["ocho_semanas"] > max(medias["regla"], medias["regresion"])


def test_cifras_de_segmentacion(ventas):
    g = ventas.groupby("id_cliente").agg(
        ultima=("fecha", "max"),
        primera=("fecha", "min"),
        pedidos=("fecha", "nunique"),
        total=("total", "sum"),
    )
    meses = ((g["ultima"] - g["primera"]).dt.days / 30.44).clip(lower=1)
    x = pd.DataFrame(
        {
            "dias_sin_comprar": (cat.FIN - g["ultima"]).dt.days,
            "pedidos_mes": g["pedidos"] / meses,
            "compra_mes": g["total"] / meses,
        }
    )
    sin_escalar = KMeans(4, n_init=10, random_state=0).fit_predict(x)
    assert sorted(np.bincount(sin_escalar)) == [13, 41, 120, 126]
    escalados = KMeans(4, n_init=10, random_state=0).fit_predict(StandardScaler().fit_transform(x))
    assert sorted(np.bincount(escalados)) == [12, 25, 82, 181]
    dias = x["dias_sin_comprar"].groupby(escalados).mean()
    perdidos = x.index[escalados == dias.idxmax()]
    regla = g.index[g["ultima"] < "2025-10-01"]
    assert len(perdidos) == 25 and len(regla) == 30 and perdidos.isin(regla).all()


def funcion(ruta, nombre):
    """El código de la función `nombre` en un notebook, si la tiene."""
    celdas = json.loads(ruta.read_text(encoding="utf-8"))["cells"]
    for celda in celdas:
        hallada = re.search(rf"^def {nombre}\(.*?(?=^\S|\Z)", "".join(celda["source"]), re.M | re.S)
        if celda["cell_type"] == "code" and hallada:
            return hallada.group().rstrip()
    return None


@pytest.mark.parametrize("nombre", FUNCIONES)
def test_las_funciones_copiadas_son_iguales(nombre):
    copias = {funcion(ruta, nombre) for ruta in NOTEBOOKS} - {None}
    assert len(copias) == 1


@pytest.mark.parametrize(
    "carpeta, cifras",
    [
        ("02-cuando-el-arbol-se-aprende-todo", ["0.291", "0.228", "0.752", "0.223"]),
        ("03-random-forest", ["0.294", "0.296", "0.26", "0.278"]),
        ("04-series-de-tiempo", ["7388", "4787", "3035", "3128"]),
        ("05-una-sola-prueba-puede-enganar", ["2814.0", "2900.0", "26344.0", "35578.0"]),
        ("06-clasificar-tickets", ["0.832", "0.674"]),
        ("08-etica-auditar-una-decision", ["0.39", "0.65"]),
        ("09-etica-el-modelo-que-discrimina", ["72", "35", "26", "41"]),
        ("10-miniproyecto-reporte-de-la-manana", ["3524.0", "3486.0", "0.395", "0.909"]),
    ],
)
def test_las_salidas_guardadas_muestran_las_cifras_del_texto(carpeta, cifras):
    clase = json.loads((RAIZ / "temporada-2" / carpeta / "clase.ipynb").read_text(encoding="utf-8"))
    salidas = json.dumps([celda.get("outputs", []) for celda in clase["cells"]])
    for cifra in cifras:
        assert cifra in salidas, cifra
