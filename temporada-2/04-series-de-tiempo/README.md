# Episodio 2.4 · Series de tiempo: día de la semana y feriados

**Objetivo:** Pronosticar cada día con una regla con índice y con una regresión con calendario.

## Lo que ya sabes en Excel → cómo se hace en Python

| En Excel | En Python |
|---|---|
| Una fila por día | `.groupby("fecha")["total"].sum().asfreq("D", fill_value=0)` |
| `=PROMEDIO.SI()` (`AVERAGEIF`) por día | `serie.groupby(serie.index.dayofweek).mean()` |
| Regla con índice | `tres_pronosticos(serie, FERIADOS, mes)` |

## Materiales

| Archivo | Para qué sirve | |
|---|---|---|
| `clase.ipynb` | El notebook que vemos en el video | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-2/04-series-de-tiempo/clase.ipynb) |
| `ejercicio.ipynb` | Practica por tu cuenta | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-2/04-series-de-tiempo/ejercicio.ipynb) |
| `solucion.ipynb` | Compara tu respuesta | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-2/04-series-de-tiempo/solucion.ipynb) |

> 🎬 Video próximamente.
