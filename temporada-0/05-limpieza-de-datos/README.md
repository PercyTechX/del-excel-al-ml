# Episodio 0.5 · Limpieza de datos: vacíos, duplicados, textos y fechas

**Objetivo:** Dejar listos los datos reales: celdas vacías, filas repetidas, textos inconsistentes, fechas y montos guardados como texto.

## Lo que ya sabes en Excel → cómo se hace en Python

| En Excel | En Python |
|---|---|
| Quitar duplicados | `ventas.drop_duplicates()` |
| `=ESPACIOS()` (`TRIM`), `=NOMPROPIO()` (`PROPER`), aproximadamente | `.str.strip()`, `.str.capitalize()` |
| Llenar vacíos | `.fillna("Sin dato")` |
| `=VALOR()` (`VALUE`) | `.astype(float)` |
| Convertir texto en fecha, `=AÑO()` (`YEAR`), `=MES()` (`MONTH`) | `pd.to_datetime()`, `.dt.year`, `.dt.month` |

## Materiales

| Archivo | Para qué sirve | |
|---|---|---|
| `clase.ipynb` | El notebook que vemos en el video | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-0/05-limpieza-de-datos/clase.ipynb) |
| `ejercicio.ipynb` | Practica por tu cuenta | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-0/05-limpieza-de-datos/ejercicio.ipynb) |
| `solucion.ipynb` | Compara tu respuesta | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-0/05-limpieza-de-datos/solucion.ipynb) |

> 🎬 Video próximamente.
