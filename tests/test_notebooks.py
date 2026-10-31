"""Comprueba que ruff no le quite al ejercicio una librería que el alumno va a necesitar."""

import json
from pathlib import Path

import pytest

EJERCICIOS = sorted(Path(__file__).parent.parent.glob("temporada-0/*/ejercicio.ipynb"))


def celda_inicial(ruta):
    """La celda que importa las librerías y define DATOS, si el notebook la tiene."""
    cuaderno = json.loads(ruta.read_text(encoding="utf-8"))
    celdas = ["".join(c["source"]) for c in cuaderno["cells"] if c["cell_type"] == "code"]
    return next((celda for celda in celdas if "DATOS = " in celda), None)


@pytest.mark.parametrize("ejercicio", EJERCICIOS, ids=lambda ruta: ruta.parent.name)
def test_el_ejercicio_empieza_igual_que_la_solucion(ejercicio):
    assert celda_inicial(ejercicio) == celda_inicial(ejercicio.with_name("solucion.ipynb"))
