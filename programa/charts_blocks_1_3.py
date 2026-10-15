"""Piezas gráficas de los bloques 1 y 2 de la infografía (KPIs, panorama y estacionalidad)."""
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

from data_prep import ROOT, build_series, kpis, load_data
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


def main():
    apply_style()
    series = build_series(load_data())
    kpi_cards(kpis(series))
    timeline(series)


if __name__ == "__main__":
    main()
