"""Monta los cinco bloques con el estilo y las series del avance. Uso: python programa/infografia.py."""
import textwrap

import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.text import Text

from charts_blocks_1_3 import MONTHS, NORMAL_YEARS, QUESTIONS
from data_prep import (ROOT, build_series, comparison_table, kpis, load_data,
                       recovery_index, seasonal_profile)
from forecast import evaluate
from style import (ACCENT, ACCENT_TEXT, BG, GREY, INK, LIGHT, MUTED, NAVY,
                   TEAL, apply_style, millions, thousands)


def recommendations(series):
    profile = seasonal_profile(series["Total"], NORMAL_YEARS)
    recovery = recovery_index(series["Total"]).loc[2025]
    return [
        ("Preparar la temporada alta", f"Diciembre alcanza {profile.loc[12]:.0f} % del promedio mensual. "
         "Coordinar capacidad y promoción antes de las fiestas; ajustar Semana Santa a su fecha anual."),
        ("Priorizar mercados recuperados", "El Salvador, Honduras y EE. UU. superan su nivel de 2019. "
         "Probar campañas segmentadas y medir llegadas por mercado antes de ampliar el gasto."),
        ("Planificar por vía y con contingencias", f"El Total equivale al {recovery:.0f} % de 2019 en 2025. "
         "Revisar capacidad aérea y terrestre por separado; no extrapolar cruceros después de 2022."),
        ("Actualizar el pronóstico cada mes", "El ganador cambia con el horizonte. Usar escenarios, "
         "revalidar modelos con datos recientes y evitar compromisos rígidos basados en el test largo."),
    ]


def model_table(ax, comparison):
    ax.set_axis_off()
    rows = [[r.modelo, f"{r.mae:,.0f}", f"{r.rmse:,.0f}"] for r in comparison.itertuples()]
    table = ax.table(cellText=rows, colLabels=["Modelo", "MAE", "RMSE"],
                     colWidths=[0.54, 0.23, 0.23], cellLoc="left", bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(BG)
        cell.set_facecolor(LIGHT if row in (0, 1) else BG)
        cell.get_text().set_color(ACCENT_TEXT if row == 1 else INK)
        if row in (0, 1):
            cell.get_text().set_weight("bold")
        if col:
            cell.get_text().set_ha("right")


def prediction_chart(ax, forecast):
    ax.fill_between(forecast.index, forecast.inferior_95, forecast.superior_95,
                    color=ACCENT, alpha=0.16, linewidth=0)
    ax.plot(forecast.index, forecast.real, color=NAVY, lw=1.8)
    ax.plot(forecast.index, forecast.estimacion, color=ACCENT_TEXT, ls="--", lw=1.8)
    ax.set_yscale("log")
    ax.set_ylim(forecast.inferior_95.min() * 0.7, forecast.superior_95.max() * 2)
    ax.set_xlim(forecast.index[0], forecast.index[-1])
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_yticks([1e3, 1e5, 1e7], ["1 K", "100 K", "10 M"])
    ax.yaxis.set_minor_locator(mticker.NullLocator())
    ax.set_ylabel("Viajeros / mes · escala log")
    ax.text(0.02, 0.94, "Banda: Estimación · 95 %", transform=ax.transAxes,
            color=ACCENT_TEXT, va="top", fontsize=10)
    ax.annotate("Real", (forecast.index[-1], forecast.real.iloc[-1]),
                xytext=(-5, 12), textcoords="offset points", ha="right", color=NAVY, fontsize=10)
    ax.annotate("Estimación ARIMA", (forecast.index[-1], forecast.estimacion.iloc[-1]),
                xytext=(-5, -14), textcoords="offset points", ha="right", color=ACCENT_TEXT, fontsize=10)


def poster(series, comparison, forecast, print_version=False):
    # Coordenadas del lienzo digital: x de izquierda a derecha, y de arriba abajo.
    fig = plt.figure(figsize=(11, 17) if print_version else (12, 24), dpi=100)

    def text(x, y, message, size=11, color=INK, weight="normal", **kw):
        return fig.text(x / 1200, 1 - y / 2400, message, fontsize=size,
                        color=color, weight=weight, va="top", **kw)

    def axes(x, y, w, h):
        return fig.add_axes([x / 1200, 1 - (y + h) / 2400, w / 1200, h / 2400])

    def section(y, number, heading, subtitle):
        text(50, y, number, 14, TEAL, "bold")
        text(90, y, heading, 16, NAVY, "bold")
        text(90, y + 29, subtitle, 10, MUTED)

    text(50, 35, "01  GUATEMALA  /  TURISMO EN DATOS  /  2009–JUN 2026", 10, TEAL, "bold")
    text(50, 65, "El turismo se recupera,\npero no al mismo ritmo", 30, NAVY, "bold", linespacing=1.08)
    text(50, 166, "17 años de llegadas: anticipar las temporadas y planificar sin ignorar la incertidumbre.", 12, MUTED)

    k = kpis(series)
    cards = [(millions(k["accumulated"]), "viajeros acumulados\n2009–jun 2026", NAVY),
             (millions(k["peak_value"], 2), f"récord anual\n{k['peak_year']}", NAVY),
             (f"−{k['covid_drop_pct']:.0f} %", "abr–dic 2020\nvs. abr–dic 2019", ACCENT_TEXT),
             (f"{k['recovery_2025_pct']:.0f} %", "nivel de 2019\nalcanzado en 2025", TEAL)]
    for i, (value, label, color) in enumerate(cards):
        x = 50 + i * 278
        fig.add_artist(Rectangle((x / 1200, 1 - 345 / 2400), 260 / 1200, 125 / 2400,
                                 transform=fig.transFigure, fc=LIGHT, ec="none", zorder=0))
        text(x + 15, 233, value, 25, color, "bold")
        text(x + 15, 285, label, 11)

    section(375, "02", "Un colapso interrumpió el crecimiento", "Total mensual: Turista + Excursionista. Los eventos aportan contexto, no prueban causalidad.")
    ax = axes(100, 465, 1020, 215)
    s = series["Total"]
    ax.plot(s.index, s, color=GREY, lw=0.9)
    trend = s.rolling(12, center=True).mean()
    ax.plot(trend.index, trend, color=NAVY, lw=2)
    ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2021-12-01"), color=ACCENT, alpha=0.1)
    ax.set_ylim(0, s.max() * 1.32)
    ax.set_xlim(s.index[0], s.index[-1])
    thousands(ax)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    for date, label, y in [("2010-05-01", "2010: Agatha\ny Pacaya", 510000),
                           ("2018-06-01", "2018: Volcán\nde Fuego", 510000),
                           ("2020-03-01", "2020: cierre\nde fronteras", 430000),
                           ("2023-01-01", "2023: cambio\nde clasificación", 510000)]:
        d = pd.Timestamp(date)
        ax.axvline(d, color=MUTED, ls=":", lw=0.6)
        ax.text(d, y, label, ha="center", va="top", fontsize=9, color=MUTED)
    text(100, 718, "Gris: datos mensuales · Azul: promedio móvil de 12 meses · Naranja: período pandémico.", 9, MUTED)

    section(760, "03", "Diciembre concentra la temporada alta", "Índice mensual: promedio del año = 100. Se excluyen 2020–2022 y el año parcial 2026.")
    ax = axes(100, 835, 1020, 155)
    prof = seasonal_profile(s, NORMAL_YEARS)
    ax.bar(np.arange(12), prof.values - 100, bottom=100,
           color=[ACCENT if m == 12 else NAVY if v >= 100 else GREY for m, v in prof.items()])
    ax.axhline(100, color=INK, lw=0.8)
    ax.set_xticks(range(12), MONTHS)
    ax.set_ylim(65, 145)
    ax.set_yticks([75, 100, 125])
    for i, v in enumerate(prof):
        ax.text(i, v + (2 if v >= 100 else -2), f"{v:.0f}", ha="center",
                va="bottom" if v >= 100 else "top", fontsize=10, color=ACCENT_TEXT if i == 11 else INK)
    text(100, 1024, "Mar–abr: Semana Santa (fecha variable) · Jul–ago: vacaciones / Bono 14 · Dic: aguinaldo y fiestas.", 9, MUTED)
    text(90, 1062, "Vías y mercados: cuatro preguntas para decidir", 14, NAVY, "bold")
    text(90, 1092, "Azul = vías · Verde azulado = mercados · Naranja = mayor valor dentro de cada grupo", 9, MUTED)
    table = comparison_table(series)
    for i, (column, question, unit, fmt) in enumerate(QUESTIONS):
        x, y = 190 + (i % 2) * 545, 1170 + (i // 2) * 215
        ax = axes(x, y, 355, 135)
        vals = table[column]
        winners = table.groupby("group")[column].idxmax().values
        pos = np.array([6, 5, 4, 2, 1, 0])
        for name, yy in zip(table.index, pos):
            win = name in winners
            color = ACCENT if win else NAVY if table.loc[name, "group"] == "Vía" else TEAL
            ax.barh(yy, vals[name], height=0.7, color=color)
            ax.text(vals[name] + vals.max() * .02, yy, fmt.format(vals[name]), va="center", fontsize=9,
                    color=ACCENT_TEXT if win else INK, weight="bold" if win else "normal")
        ax.set_yticks(pos, ["Marítima*" if n == "Marítima" else n for n in table.index], fontsize=9)
        ax.set_xlim(0, vals.max() * 1.4)
        ax.set_xticks([])
        ax.grid(False)
        ax.spines["bottom"].set_visible(False)
        ax.tick_params(length=0)
        text(x - 100, y - 42, question.replace(" (2009–2019)", ""), 11, INK, "bold")
        text(x - 100, y - 18, unit + ("; 2009–2019" if column == "growth_pct" else ""), 8.5, MUTED)
    text(90, 1534, "*Marítima: cruceristas 2009–2022, con meses en cero. Volatilidad: residuo en log; estacionalidad: 0–1.", 9, MUTED)
    text(90, 1556, "En 2025, El Salvador, EE. UU. y Honduras superan 2019; el Total aún está en 81 %.", 10, TEAL, "bold")

    section(1605, "04", "El menor error no elimina la incertidumbre", "Prueba 70/30: abr 2021–jun 2026 (63 meses). Ajuste solo hasta mar 2021. Errores en viajeros; menor = mejor.")
    model_table(axes(60, 1680, 495, 205), comparison)
    prediction_chart(axes(680, 1680, 440, 205), forecast)
    text(60, 1923, "ARIMA gana el test largo: RMSE 169,120. En 24 meses gana Holt-Winters: RMSE 20,777.", 11, NAVY, "bold")
    text(60, 1952, "Pronóstico retrospectivo, no posterior a jun 2026. Banda predictiva puntual del 95 %, condicionada al modelo.", 9, MUTED)
    text(60, 1974, "El entrenamiento acaba en pandemia: el error alto aconseja revalidar, no extrapolar una recuperación segura.", 9, MUTED)

    section(2020, "05", "Cuatro decisiones para INGUAT", "De la evidencia a la acción: priorizar, medir y ajustar antes de comprometer recursos.")
    for i, (heading, body) in enumerate(recommendations(series)):
        x, y = 60 + (i % 2) * 555, 2090 + (i // 2) * 110
        text(x, y, f"{i + 1}. {heading}", 11, TEAL, "bold")
        text(x, y + 26, textwrap.fill(body, width=70), 9.5, linespacing=1.3)
    text(60, 2320, "FUENTE  Base de Migración 2009–2026, INGUAT/IGM · Ene 2009–jun 2026 · Uso académico, no difusión pública.", 9, MUTED)
    text(60, 2342, "Total = Turista + Excursionista. 2026 parcial; no se compara con años completos. Modelos: Laboratorio 1, serie Total.", 9, MUTED)
    text(60, 2364, "AUTORES  Nicolás Concuá (23197) y Felipe Aguilar (23195) · CC3084, Universidad del Valle de Guatemala · Octubre 2026", 9, MUTED)
    if print_version:
        for item in fig.findobj(Text):
            item.set_fontsize(item.get_fontsize() * 0.78)
    return fig


def main():
    apply_style()
    series = build_series(load_data())
    comparison, forecast = evaluate(series["Total"])
    out = ROOT / "outputs"
    fig, ax = plt.subplots(figsize=(9, 3.5))
    model_table(ax, comparison)
    fig.suptitle("Modelos del Lab 1 · Total · prueba 70/30 · errores en viajeros", color=NAVY)
    fig.savefig(out / "b4_modelos.png", bbox_inches="tight")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 4))
    prediction_chart(ax, forecast)
    ax.set_title("ARIMA(1,1,1) · prueba abr 2021–jun 2026", loc="left", pad=15, color=NAVY)
    fig.tight_layout()
    fig.savefig(out / "b4_pronostico.png", bbox_inches="tight")
    plt.close(fig)
    fig = poster(series, comparison, forecast)
    fig.savefig(out / "Infografia_Lab9.png", dpi=100)
    plt.close(fig)
    fig = poster(series, comparison, forecast, print_version=True)
    fig.savefig(out / "Infografia_Lab9.pdf", metadata={"Title": "El turismo se recupera, pero no al mismo ritmo",
                                                      "Author": "Nicolás Concuá y Felipe Aguilar"})
    plt.close(fig)
    print("Infografía generada: PNG 1200 × 2400 y PDF de una página, 11 × 17 pulgadas.")


if __name__ == "__main__":
    main()
