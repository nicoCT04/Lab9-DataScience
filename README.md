# Laboratorio 9 — Visualización Estática

Infografía de una página que sintetiza el Laboratorio 1 (series de tiempo del ingreso de viajeros a Guatemala, ene-2009 a jun-2026) para un directivo de INGUAT.

**Integrantes:** Nicolás Concuá (23197) · Felipe Aguilar (23195)

**Pregunta guía:** ¿Qué nos enseñan 17 años de datos migratorios sobre el turismo en Guatemala y qué debemos anticipar hacia el futuro?

## Estructura

- `programa/data_prep.py`: carga de la base y construcción de las series con las definiciones del Lab 1 (Total = Turista + Excursionista, Marítima = cruceristas 2009–2022, mercados El Salvador, EE. UU. y Honduras) e indicadores comparativos.
- `programa/style.py`: paleta, tipografía y estilo común de todas las piezas.
- `programa/charts_blocks_1_3.py`: piezas de los bloques 1 a 3.
- `outputs/`: PNG a 300 dpi listos para montar en el lienzo.

## Ejecución

1. Copiar `Base_Migracion_2009-2026jun.xlsx` a `data/raw/` (no se versiona: uso académico).
2. Instalar dependencias y generar las piezas:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python programa/charts_blocks_1_3.py
```

## Paleta

| Rol | Color |
|---|---|
| Serie principal / vías | `#14365D` azul marino |
| Mercados / segunda categoría | `#1F7A7A` verde azulado |
| Contexto | `#A3ADB8` gris |
| Acento (picos, anomalías, pronóstico) | `#E8702A` naranja (`#B8501A` para texto pequeño) |

## Avance

- [x] Documento de explicación de diseño (avance, 15-oct)
- [x] Bloque 1: tarjetas KPI (`b1_kpis.png`)
- [x] Bloque 2: panorama histórico con eventos (`b2_timeline.png`)
- [x] Bloque 3: estacionalidad (`b3_seasonality.png`, `b3_heatmap.png`), cuadrante comparativo (`b3_quadrant.png`) y recuperación por vía y mercado (`b3_recovery.png`)

## Pendiente (Felipe)

- [ ] Bloque 4: tabla/gráfico comparativo de modelos (MAE, RMSE) de la serie Total y proyección del modelo ganador con intervalo de 95 % rotulado «Estimación», usando `style.py`.
- [ ] Bloque 5: 3–5 recomendaciones para INGUAT y ficha técnica (fuente: Base de Migración 2009–2026 INGUAT/IGM, autores).
- [ ] Montaje del lienzo: PNG 1200 × 2400 px y PDF A3 vertical (11 × 17 in).
- [ ] Completar las secciones 5 (bloques 4–5) del documento de explicación.
