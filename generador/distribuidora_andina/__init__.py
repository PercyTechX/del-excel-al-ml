"""Datos sintéticos de Distribuidora Andina S.A.C., la empresa ficticia de la serie.

Uso:
    python -m distribuidora_andina   # genera los archivos en la carpeta datos/
"""

from importlib.metadata import PackageNotFoundError, version

from . import generar
from .catalogos import SEDES
from .generar import generar_todo

try:
    __version__ = version("distribuidora-andina")
except PackageNotFoundError:  # se usa sin instalar
    __version__ = "desconocida"

EMPRESA = "Distribuidora Andina S.A.C."
MONEDA = "PEN"
SIMBOLO_MONEDA = "S/"
CIUDADES = tuple(SEDES)

__all__ = ["CIUDADES", "EMPRESA", "MONEDA", "SIMBOLO_MONEDA", "generar", "generar_todo"]
