# Laboratorio 9 — Visualización Estática

Infografía de una página que sintetiza el Laboratorio 1 (series de tiempo del ingreso de viajeros a Guatemala, ene-2009 a jun-2026) para un directivo de INGUAT.

**Integrantes:** Nicolás Concuá (23197) · Felipe Aguilar (23195)

**Pregunta guía:** ¿Qué nos enseñan 17 años de datos migratorios sobre el turismo en Guatemala y qué debemos anticipar hacia el futuro?

## Estructura

- `programa/data_prep.py`: carga de la base y construcción de las series con las definiciones del Lab 1 (Total = Turista + Excursionista, Marítima = cruceristas 2009–2022, mercados El Salvador, EE. UU. y Honduras) e indicadores comparativos.
- `programa/style.py`: paleta, tipografía y estilo común de todas las piezas.
- `programa/charts_blocks_1_3.py`: piezas de los bloques 1 a 3.
- `programa/forecast.py`: reproducción del ARIMA ganador y cálculo del intervalo predictivo del 95 %.
- `programa/infografia.py`: bloque 4, recomendaciones y montaje final de los cinco bloques.
- `programa/documento.py`: exportación de la explicación editable a PDF.
- `data/processed/modelos_total_lab1.csv`: métricas de los siete modelos de Total, tomadas del Lab 1.
- `docs/Explicacion_Diseno_Lab9.md`: fuente editable del documento de explicación.
- `outputs/`: PNG a 300 dpi listos para montar en el lienzo.

## Ejecución

1. Copiar `Base_Migracion_2009-2026jun.xlsx` a `data/raw/` (no se versiona: uso académico).
2. Instalar dependencias y generar las piezas:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python programa/charts_blocks_1_3.py
python programa/infografia.py
python programa/documento.py
```

Entorno verificado: Python 3.11.2. Las versiones de `requirements.txt` corresponden a la ejecución validada. Para la infografía final bastan los dos últimos scripts; el primero regenera las piezas del avance. El Excel permanece ignorado por Git. Arial debe estar instalada; Matplotlib usará una fuente alternativa si no está disponible.

## Entregables

- [Infografía digital, 1200 × 2400 px](outputs/Infografia_Lab9.png).
- [Infografía para impresión, una página de 11 × 17 pulgadas](outputs/Infografia_Lab9.pdf).
- [Explicación de decisiones de diseño, PDF](docs/Explicacion_Diseno_Lab9.pdf) y [fuente editable](docs/Explicacion_Diseno_Lab9.md).
- [Fuente editable de la infografía](programa/infografia.py), [comparación de modelos](outputs/b4_modelos.png) y [pronóstico con intervalo](outputs/b4_pronostico.png).
- [Pronóstico mensual verificable](outputs/b4_pronostico.csv) y [registro de validación](outputs/b4_validacion.json).
- Repositorio de trabajo: https://github.com/nicoCT04/Lab9-DataScience. Compartir el enlace y los archivos mediante el canal académico autorizado, con acceso para docente y auxiliares.

**Formato:** el enunciado llama «A3» a 11 × 17 pulgadas. No son equivalentes: A3 ISO es 297 × 420 mm. Se sigue la medida explícita de 11 × 17 pulgadas. El PNG respeta 1200 × 2400 sin recorte; el PDF se vuelve a componer para su proporción y conserva texto/gráficos vectoriales.

## Procedencia de modelos y límites

Las métricas no se inventan ni se recalculan con otra partición: el CSV transcribe la salida de la sección 21 de `Lab1DataScience/notebooks/Lab1_Series_Tiempo.ipynb`, serie Total, guardada en el repositorio del Lab 1 (commit `055ec66fa7609da4efb162cce67a0a447ab1205e`). La tabla contiene MAE y RMSE en viajeros, con dos decimales; el lienzo redondea al entero. SARIMA fijo = (1,1,1)(0,1,1)12; automático = (2,1,2)(2,0,0)12. Se incluyen también Prophet, Holt-Winters, suavizamiento simple y naive estacional. No hace falta instalar Prophet ni pmdarima para visualizar sus resultados guardados.

Se reproduce ARIMA(1,1,1) sobre `log(Total)` con 147 meses de entrenamiento (ene 2009–mar 2021) y 63 de prueba (abr 2021–jun 2026). La línea usa `exp(predicted_mean)`, igual que el Lab 1; no aplica corrección de media lognormal. `forecast.py` exige convergencia y verifica MAE/RMSE contra el Lab 1 con tolerancia máxima de un viajero por diferencias numéricas entre versiones.

El intervalo predictivo puntual del 95 % se calcula con `get_forecast().conf_int(alpha=0.05)` y se invierte con `exp`, sin ajustar sobre prueba. Es muy amplio, por lo que se muestra completo en **escala logarítmica explícita**. Es condicional al modelo, no garantiza cobertura simultánea ni incorpora cambios estructurales. Es una estimación retrospectiva sobre prueba, **no una proyección posterior a junio de 2026**.

En el 70/30 gana ARIMA (MAE 154,494.17; RMSE 169,119.58). En la evaluación complementaria del Lab 1 sobre los últimos 24 meses gana Holt-Winters (MAE 17,581.15; RMSE 20,776.87). No se comparan directamente los errores de horizontes distintos para afirmar una mejora.

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

## Trabajo completado (Felipe)

- [x] Bloque 4: tabla MAE/RMSE de Total y predicción sobre prueba del ganador con intervalo del 95 % rotulado «Estimación», usando `style.py`.
- [x] Bloque 5: cuatro recomendaciones para INGUAT y ficha técnica con fuente/autores.
- [x] Montaje del lienzo: PNG 1200 × 2400 y PDF vertical de una página, 11 × 17 pulgadas.
- [x] Completar la sección 5 del documento (bloques 4–5), con fuente editable y PDF actualizado.

## Revisión de rúbrica y entrega

| Criterio | Evidencia |
|---|---|
| Documento (45 puntos): coherencia, color, gráficos y orden | Explicación, secciones 1–7; actualización de 5.4–5.5 |
| Integridad de cifras, modelos y errores | Definiciones compartidas con el avance; CSV de Lab 1 y reproducción de ARIMA |
| Narrativa y jerarquía | Titular ejecutivo y cinco bloques en lectura vertical |
| Estacionalidad y cuatro comparaciones | Índice mensual y cuadrante por vía/mercado, con unidades y períodos |
| Pronóstico con incertidumbre | Banda predictiva completa del 95 %, «Estimación», escala log explícita |
| Recomendaciones fundamentadas | Cuatro acciones vinculadas a calendario, mercados, vías y errores de pronóstico |
| Formato y legibilidad | PNG 1200 × 2400; PDF de una página 11 × 17; revisión visual de ambos |
| Fuentes, créditos y archivos editables | Pie de infografía, scripts y Markdown versionables |

La rúbrica asigna 55 puntos a la infografía; este contraste no sustituye la calificación del docente. **Pendiente de comprobación externa:** inscripción en grupo de Canvas, permisos para docente/auxiliares, acceso a los enlaces y entrega a tiempo (avance: 15-oct; final: 18-oct-2026). No se puede verificar el cumplimiento de esas condiciones desde los archivos locales.

**Uso estrictamente académico:** el enunciado prohíbe publicar la infografía abiertamente sin consulta previa. No subir a un repositorio público ni difundir la base o las piezas sin autorización. Los cambios locales no implican publicación ni entrega en Canvas.
