# Episodio 1.7 · Clasificación: ¿qué crédito revisamos primero?

**Objetivo:** Estimar una probabilidad y usar un umbral para decidir qué revisar.

## Lo que ya sabes en Excel → cómo se hace en Python

| En Excel | En Python |
|---|---|
| Una regla con `=SI()` (`IF`) | `make_pipeline(StandardScaler(), LogisticRegression())` |
| Un puntaje de riesgo | `modelo.predict_proba(x)[:, 1]` |
| `=SI(puntaje>=0.25, ...)` | `probabilidad >= 0.25` |

## Materiales

| Archivo | Para qué sirve | |
|---|---|---|
| `clase.ipynb` | El notebook que vemos en el video | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-1/07-clasificacion-creditos/clase.ipynb) |
| `ejercicio.ipynb` | Practica por tu cuenta | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-1/07-clasificacion-creditos/ejercicio.ipynb) |
| `solucion.ipynb` | Compara tu respuesta | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-1/07-clasificacion-creditos/solucion.ipynb) |

> 🎬 Video próximamente.
