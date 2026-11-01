# Episodio 2.6 · Modelos que leen: clasificar tickets

**Objetivo:** Clasificar mensajes contando palabras, y ver dónde falla.

## Lo que ya sabes en Excel → cómo se hace en Python

| En Excel | En Python |
|---|---|
| `=CONTAR.SI()` (`COUNTIF`) por palabra | `CountVectorizer().fit_transform(textos)` |
| Clasificar el mensaje | `modelo.predict(...)` |
| Aciertos por grupo | `acierta[filtro].mean()` |

## Materiales

| Archivo | Para qué sirve | |
|---|---|---|
| `clase.ipynb` | El notebook que vemos en el video | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-2/06-clasificar-tickets/clase.ipynb) |
| `ejercicio.ipynb` | Practica por tu cuenta | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-2/06-clasificar-tickets/ejercicio.ipynb) |
| `solucion.ipynb` | Compara tu respuesta | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-2/06-clasificar-tickets/solucion.ipynb) |

> 🎬 Video próximamente.
