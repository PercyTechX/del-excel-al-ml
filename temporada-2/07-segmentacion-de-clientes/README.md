# Episodio 2.7 · Segmentación de clientes

**Objetivo:** Agrupar clientes con k-means, escalar las columnas y entender que los grupos son una decisión.

## Lo que ya sabes en Excel → cómo se hace en Python

| En Excel | En Python |
|---|---|
| Rangos a mano | `KMeans(n_clusters=4, n_init=10, random_state=0)` |
| Misma escala | `StandardScaler().fit_transform(tabla)` |
| Tabla dinámica por grupo | `tabla.groupby(grupos).mean()` |

## Materiales

| Archivo | Para qué sirve | |
|---|---|---|
| `clase.ipynb` | El notebook que vemos en el video | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-2/07-segmentacion-de-clientes/clase.ipynb) |
| `ejercicio.ipynb` | Practica por tu cuenta | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-2/07-segmentacion-de-clientes/ejercicio.ipynb) |
| `solucion.ipynb` | Compara tu respuesta | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-2/07-segmentacion-de-clientes/solucion.ipynb) |

> 🎬 Video próximamente.
