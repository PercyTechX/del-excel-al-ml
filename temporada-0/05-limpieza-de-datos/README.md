# Episodio 0.5 · Limpieza de datos: vacíos, duplicados, textos y fechas

**Objetivo:** Dejar listos los datos reales: celdas vacías, filas repetidas, textos inconsistentes, fechas y montos guardados como texto.

## Lo que ya sabes en Excel → cómo se hace en Python

| En Excel | En Python |
|---|---|
| Quitar duplicados | `df.drop_duplicates()` |
| `=ESPACIOS()` (`TRIM`), `=MAYUSC()` (`UPPER`) | `.str.strip()`, `.str.upper()` |
| `=MES()` (`MONTH`), `=DIAS()` (`DAYS`) | `.dt.month`, resta de fechas |

## Materiales

| Archivo | Para qué sirve |
|---|---|
| `clase.ipynb` | El notebook que vemos en el video |
| `ejercicio.ipynb` | Practica por tu cuenta |
| `solucion.ipynb` | Compara tu respuesta |

> En construcción: video y notebooks próximamente.
