# Del Excel al Machine Learning

[![CI](https://github.com/PercyTechX/del-excel-al-ml/actions/workflows/ci.yml/badge.svg)](https://github.com/PercyTechX/del-excel-al-ml/actions/workflows/ci.yml)
[![Código: MIT](https://img.shields.io/badge/c%C3%B3digo-MIT-blue.svg)](LICENSE)
[![Contenido: CC BY 4.0](https://img.shields.io/badge/contenido-CC%20BY%204.0-lightgrey.svg)](LICENSE-CONTENT.md)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)

**Aprende Machine Learning desde cero, partiendo de lo que ya sabes hacer en Excel.**

Una serie de videos con notebooks listos para usar, pensada para personas que trabajan en oficina y quieren entrar al mundo de los datos y la inteligencia artificial. Sin instalar nada, sin matemáticas complicadas y con ejemplos de una empresa como la tuya.

> 🇬🇧 **In English:** *From Excel to Machine Learning* is a free, Spanish-language video series and notebook collection that teaches Python and Machine Learning to office workers, using familiar Excel concepts as the starting point. All examples are based on a fictional Peruvian company with synthetic data. The repository follows ML engineering practices: CI that lints the code and executes every notebook, with a pinned environment and a tested synthetic-data generator in progress.
>
> **Status:** work in progress. Season 0 is being produced.

---

## ¿Para quién es?

- Trabajas con Excel todos los días: reportes, tablas dinámicas, `BUSCARV`.
- Escuchas hablar de *Machine Learning* e *inteligencia artificial* y quieres entender de qué se trata.
- Nunca has programado, o lo intentaste y te frustraste.

Si te identificas con alguno de estos puntos, esta serie es para ti.

## ¿Cómo funciona?

1. **Mira el video** del episodio.
2. **Abre el notebook en Google Colab** con el botón <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Abrir en Colab" height="18"/>. Solo necesitas una cuenta de Google.
3. **Practica** con el ejercicio y compara con la solución.

## La empresa del curso: Distribuidora Andina S.A.C.

Todos los ejemplos ocurren en **Distribuidora Andina S.A.C.**, una empresa ficticia peruana con sedes en Lima, Arequipa, Trujillo, Cusco, Piura y Chiclayo. Sus áreas de Ventas, Recursos Humanos, Finanzas y Atención al Cliente nos plantean problemas reales que resolveremos con Python y Machine Learning.

Los datos son **sintéticos** (generados por código) y están disponibles en [`datos/`](datos/).

## Temario

### Temporada 0: Python para gente de Excel

| # | Episodio | Video | Notebook |
|---|---|---|---|
| 0.1 | [Google Colab, tu nueva hoja de cálculo](temporada-0/01-google-colab/) | 🔜 | [![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PercyTechX/del-excel-al-ml/blob/main/temporada-0/01-google-colab/clase.ipynb) |
| 0.2 | [Python como calculadora](temporada-0/02-python-calculadora/) | 🔜 | 🔜 |
| 0.3 | [Decisiones, repeticiones y funciones](temporada-0/03-decisiones-y-funciones/) | 🔜 | 🔜 |
| 0.4 | [pandas I: abre tu Excel en Python](temporada-0/04-pandas-abre-tu-excel/) | 🔜 | 🔜 |
| 0.5 | [Limpieza de datos: vacíos, duplicados, textos y fechas](temporada-0/05-limpieza-de-datos/) | 🔜 | 🔜 |
| 0.6 | [pandas II: tablas dinámicas, BUSCARV y estadística básica](temporada-0/06-tablas-dinamicas-y-buscarv/) | 🔜 | 🔜 |
| 0.7 | [Gráficos](temporada-0/07-graficos/) | 🔜 | 🔜 |
| 0.8 | [Miniproyecto: automatiza tu reporte mensual](temporada-0/08-mini-proyecto-reporte-mensual/) | 🔜 | 🔜 |

### Próximas temporadas

- **Temporada 1: Fundamentos de Machine Learning.** Qué es ML, regresión, clasificación y cómo evaluar un modelo.
- **Temporada 2: Más modelos.** Árboles de decisión, Random Forest, segmentación de clientes, pronósticos, texto y ética.
- **Temporada 3: Proyecto final.** Un caso completo con datos de Kaggle, desde el análisis hasta poner el modelo en producción.

## Estructura del repositorio

```
del-excel-al-ml/
├── temporada-0/          Episodios: clase, ejercicio y solución
├── datos/                Datos sintéticos de Distribuidora Andina
├── generador/            Paquete Python que genera los datos
├── tests/                Pruebas del generador
└── recursos/             Plantilla de notebook, guías rápidas y material de apoyo
```

## Para usuarios avanzados: trabajar en tu computadora

Colab es suficiente para toda la serie. Si prefieres trabajar localmente:

```bash
git clone https://github.com/PercyTechX/del-excel-al-ml.git
cd del-excel-al-ml
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt -e ".[dev]"
pytest                           # ejecuta las pruebas y todos los notebooks
```

## Autor

Creado por **Percy Nazario** ([@PercyTechX](https://github.com/PercyTechX)).

- GitHub: [@PercyTechX](https://github.com/PercyTechX)
- LinkedIn: [Percy Nazario](https://www.linkedin.com/in/percy-nazario/)
- YouTube: *próximamente*

Si esta serie te ayuda, dale una ⭐ al repositorio y compártelo con alguien que esté dando el salto del Excel a los datos.

## Licencia

- **Código** (celdas de código de los notebooks, generador y pruebas): [MIT](LICENSE).
- **Contenido didáctico** (texto explicativo de los notebooks, diapositivas, guías y datos): [CC BY 4.0](LICENSE-CONTENT.md).
