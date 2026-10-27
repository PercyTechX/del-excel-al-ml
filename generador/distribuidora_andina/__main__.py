"""Genera los datos de Distribuidora Andina.

Uso:
    python -m distribuidora_andina                 # escribe en la carpeta datos/ del repositorio
    python -m distribuidora_andina --salida ruta   # escribe en otra carpeta
"""

import argparse
from pathlib import Path

from .exportar import exportar
from .generar import SEMILLA

DATOS_DEL_REPO = Path(__file__).resolve().parents[2] / "datos"


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera los datos de Distribuidora Andina.")
    parser.add_argument("--salida", type=Path, default=DATOS_DEL_REPO, help="carpeta de destino")
    parser.add_argument("--semilla", type=int, default=SEMILLA, help="semilla aleatoria")
    args = parser.parse_args()
    for ruta in exportar(args.salida, args.semilla):
        print(f"✓ {ruta}")


if __name__ == "__main__":
    main()
