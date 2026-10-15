"""Piezas gráficas de los bloques 1 a 3 de la infografía (KPIs, panorama y estacionalidad)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

from data_prep import (ROOT, build_series, comparison_table, kpis, load_data,
                       recovery_index, seasonal_profile)
from style import (ACCENT, ACCENT_TEXT, GREY, INK, LIGHT, MUTED, NAVY, TEAL, apply_style, millions,
                   thousands, title)

OUT = ROOT / "outputs"
MONTHS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
NORMAL_YEARS = list(range(2009, 2020)) + [2023, 2024, 2025]  # sin pandemia ni rebote 2020-2022


def save(fig, name):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / name, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print("->", OUT / name)


# Bloque 1
def kpi_cards(k):
    cards = [
        (millions(k["accumulated"]), "viajeros internacionales\n2009 – jun 2026", NAVY),
        (millions(k["peak_value"], 2), f"récord anual en {k['peak_year']}\n(2.2 veces 2009)", NAVY),
        (f"−{k['covid_drop_pct']:.0f} %", "caída abr–dic 2020\nvs. mismo período 2019", ACCENT),
        (f"{k['recovery_2025_pct']:.0f} %", "del nivel de 2019\nrecuperado en 2025", TEAL),
    ]
    fig, ax = plt.subplots(figsize=(12, 2.6))
    ax.set_axis_off()
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 1)
    for i, (value, label, color) in enumerate(cards):
        ax.add_patch(FancyBboxPatch((i + 0.05, 0.05), 0.9, 0.9, boxstyle="round,pad=0,rounding_size=0.06",
                                    fc=LIGHT, ec="none"))
        ax.add_patch(plt.Rectangle((i + 0.05, 0.05), 0.025, 0.9, color=color))
        ax.text(i + 0.14, 0.62, value, fontsize=30, fontweight="bold", color=color, va="center")
        ax.text(i + 0.14, 0.27, label, fontsize=11.5, color=INK, va="center", linespacing=1.3)
    save(fig, "b1_kpis.png")


# Bloque 2
EVENTS = [
    ("2010-05-01", "May 2010\nTormenta Agatha y\nerupción del Pacaya", 0.55),
    ("2018-06-01", "Jun 2018\nErupción del\nVolcán de Fuego", 0.84),
    ("2020-09-01", "Sep 2020\nReapertura\ngradual", 0.5),
    ("2023-01-01", "Ene 2023\nCambio en la\nclasificación de viajeros", 0.84),
]


def timeline(series):
    s = series["Total"]
    trend = s.rolling(12, center=True).mean()
    fig, ax = plt.subplots(figsize=(12, 4.6))
    ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2021-12-01"), color=ACCENT, alpha=0.08, lw=0)
    ax.plot(s.index, s.values, color=GREY, lw=1)
    ax.plot(trend.index, trend.values, color=NAVY, lw=2.6)
    ymax = s.max() * 1.4
    ax.set_ylim(0, ymax)
    ax.set_xlim(s.index.min(), s.index.max() + pd.DateOffset(months=4))
    thousands(ax)

    peak = s.idxmax()
    ax.scatter([peak], [s.max()], color=ACCENT, s=40, zorder=3)
    ax.annotate(f"Récord: {s.max() / 1e3:,.0f} K\n({MONTHS[peak.month - 1].lower()} {peak.year})",
                (peak, s.max()), xytext=(-100, -4), textcoords="offset points",
                fontsize=10, color=ACCENT_TEXT, fontweight="bold")
    low = s.loc["2020"].idxmin()
    ax.scatter([low], [s.loc[low]], color=ACCENT, s=40, zorder=3)
    ax.annotate(f"Mar 2020: cierre de fronteras\nmínimo de {s.loc[low] / 1e3:,.0f} K ({MONTHS[low.month - 1].lower()} 2020)",
                (low, s.loc[low]), xytext=(-175, 18), textcoords="offset points",
                fontsize=10, color=ACCENT_TEXT, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8))
    for date, text, frac in EVENTS:
        d = pd.Timestamp(date)
        ax.axvline(d, color=MUTED, ls=":", lw=0.9, ymax=frac - 0.02)
        ax.text(d, ymax * frac, text, fontsize=9, color=MUTED, ha="center", va="bottom", linespacing=1.15)

    ax.text(trend.dropna().index[-1], trend.dropna().iloc[-1] * 1.08, "Tendencia\n(prom. 12 meses)",
            fontsize=9.5, color=NAVY, fontweight="bold", ha="left")
    title(ax, "17 años de llegadas: crecimiento sostenido, un colapso y una recuperación incompleta",
          "Viajeros internacionales por mes (Turista + Excursionista), ene 2009 – jun 2026")
    save(fig, "b2_timeline.png")


# Bloque 3
SEASON_NOTES = {
    3: "Semana\nSanta", 4: "Semana\nSanta", 7: "Vacaciones\nmedio año\ny Bono 14",
    8: "Vacaciones\nmedio año", 11: "Inicio\nvacaciones\nescolares", 12: "Aguinaldo\ny fiestas",
}


def seasonality(series):
    prof = seasonal_profile(series["Total"], NORMAL_YEARS)
    colors = [ACCENT if m == 12 else (NAVY if v >= 100 else GREY) for m, v in prof.items()]
    fig, ax = plt.subplots(figsize=(12, 4.6))
    bars = ax.bar(MONTHS, prof.values - 100, bottom=100, color=colors, width=0.7)
    ax.set_axisbelow(True)
    ax.axhline(100, color=INK, lw=0.9)
    ax.set_ylim(60, 150)
    ax.set_ylabel("% del promedio mensual del año")
    for b, (m, v) in zip(bars, prof.items()):
        y = v + 2 if v >= 100 else v - 2
        ax.text(b.get_x() + b.get_width() / 2, y, f"{v:.0f}", ha="center",
                va="bottom" if v >= 100 else "top", fontsize=10.5, fontweight="bold",
                color=ACCENT_TEXT if m == 12 else INK)
        if m in SEASON_NOTES:
            ax.text(b.get_x() + b.get_width() / 2, 63, SEASON_NOTES[m], ha="center", va="bottom",
                    fontsize=8.5, color=MUTED, linespacing=1.1)
    ax.text(4.5, 101.5, "promedio del año = 100", fontsize=9, color=MUTED, ha="center", va="bottom")
    title(ax, "Diciembre es el mes más fuerte: 34 % sobre el promedio; febrero y septiembre, los más bajos",
          "Índice estacional de la serie Total (años 2009–2019 y 2023–2025; se excluyen 2020–2022)")
    save(fig, "b3_seasonality.png")


def heatmap(series):
    s = series["Total"]
    s = s[s.index.year <= 2025]
    grid = s.groupby([s.index.year, s.index.month]).sum().unstack()
    fig, ax = plt.subplots(figsize=(7, 7.5))
    im = ax.imshow(grid.values / 1e3, cmap="Blues", aspect="auto")
    ax.set_xticks(range(12), MONTHS)
    ax.set_yticks(range(len(grid)), grid.index)
    ax.tick_params(length=0)
    ax.grid(False)
    for y in [2020, 2021]:
        r = list(grid.index).index(y)
        ax.add_patch(plt.Rectangle((-0.5, r - 0.5), 12, 1, fill=False, ec=ACCENT, lw=1.6))
    ax.text(12.6, list(grid.index).index(2020) + 0.5, "Pandemia", color=ACCENT_TEXT, fontsize=10,
            fontweight="bold", va="center", rotation=90)
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.08)
    cb.set_label("miles de viajeros", color=MUTED)
    cb.outline.set_visible(False)
    title(ax, "Calendario de llegadas", "Viajeros por mes y año (miles); más oscuro = más llegadas")
    save(fig, "b3_heatmap.png")


QUESTIONS = [
    ("seasonality", "¿Cuál tiene mayor estacionalidad?", "fuerza estacional (0–1)", "{:.2f}"),
    ("growth_pct", "¿Cuál crecía más rápido? (2009–2019)", "crecimiento anual (%)", "{:.1f} %"),
    ("volatility", "¿Cuál es más volátil?", "variación irregular (desv. residuo log)", "{:.2f}"),
    ("covid_drop_pct", "¿Cuál golpeó más la pandemia?", "caída abr–dic 2020 vs 2019 (%)", "{:.1f} %"),
]


def quadrant(series):
    t = comparison_table(series)
    order = ["Aérea", "Terrestre", "Marítima*", "", "El Salvador", "EE. UU.", "Honduras"]
    t.index = [i + "*" if i == "Marítima" else i for i in t.index]
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.5))
    for ax, (col, q, unit, fmt) in zip(axes.ravel(), QUESTIONS):
        winners = t.groupby("group")[col].idxmax().values
        ypos = np.arange(len(order))[::-1]
        for y, name in zip(ypos, order):
            if not name:
                continue
            v = t.loc[name, col]
            base = NAVY if t.loc[name, "group"] == "Vía" else TEAL
            win = name in winners
            ax.barh(y, v, color=ACCENT if win else base, alpha=1 if win else 0.55, height=0.7)
            ax.text(v, y, "  " + fmt.format(v), va="center", fontsize=10,
                    fontweight="bold" if win else "normal", color=ACCENT_TEXT if win else INK)
        ax.set_yticks(ypos, order)
        ax.set_xlim(0, t[col].max() * 1.3)
        ax.grid(False)
        ax.set_xticks([])
        ax.spines["bottom"].set_visible(False)
        ax.tick_params(axis="y", length=0, labelsize=10.5)
        ax.set_title(q, loc="left", fontsize=12.5, fontweight="bold", color=INK)
        ax.text(0, -0.08, unit, transform=ax.transAxes, fontsize=9, color=MUTED)
    fig.text(0.01, 1.02, "Cuadrante comparativo: vías de ingreso y mercados de origen",
             fontsize=15, fontweight="bold", color=INK)
    fig.text(0.01, 0.985, "En naranja, la serie que lidera cada criterio dentro de su grupo "
             "(azul = vías, verde azulado = países)", fontsize=10.5, color=MUTED)
    fig.text(0.01, -0.02, "*Marítima = cruceristas, serie disponible solo de 2009 a 2022 y con meses sin "
             "cruceros; su volatilidad y crecimiento se interpretan con cautela.", fontsize=9, color=MUTED)
    fig.tight_layout(rect=(0, 0, 1, 0.95), h_pad=2.5, w_pad=3)
    save(fig, "b3_quadrant.png")


def recovery(series):
    names = {"Total": NAVY, "Aérea": GREY, "Terrestre": GREY,
             "EE. UU.": TEAL, "El Salvador": TEAL, "Honduras": TEAL}
    label_y = {"Honduras": 157, "EE. UU.": 145, "El Salvador": 133,
               "Terrestre": 91, "Total": 80, "Aérea": 69}  # evita etiquetas encimadas
    fig, ax = plt.subplots(figsize=(12, 4.6))
    ax.axhline(100, color=INK, lw=0.9)
    ax.text(2019.05, 103, "nivel 2019 = 100", fontsize=9, color=MUTED)
    for name, color in names.items():
        r = recovery_index(series[name])
        lw = 3 if name == "Total" else 1.8
        ax.plot(r.index, r.values, color=color, lw=lw, marker="o", ms=3.5)
        ax.text(2025.12, label_y[name], f"{name}  {r.iloc[-1]:.0f}", va="center", fontsize=10,
                color=color if color != GREY else MUTED, fontweight="bold" if name == "Total" else "normal")
    ax.set_xlim(2018.8, 2026.1)
    ax.set_ylim(0, 190)
    ax.set_xticks(range(2019, 2026))
    title(ax, "Los mercados vecinos y EE. UU. ya superan 2019; el total sigue en 81 %",
          "Viajeros por año como % de 2019 (años completos; 2026 excluido por ser parcial)")
    save(fig, "b3_recovery.png")


def main():
    apply_style()
    series = build_series(load_data())
    kpi_cards(kpis(series))
    timeline(series)
    seasonality(series)
    heatmap(series)
    quadrant(series)
    recovery(series)


if __name__ == "__main__":
    main()
