import distribuidora_andina as da


def test_datos_basicos_de_la_empresa():
    assert da.EMPRESA == "Distribuidora Andina S.A.C."
    assert da.SIMBOLO_MONEDA == "S/"
    assert "Lima" in da.CIUDADES
