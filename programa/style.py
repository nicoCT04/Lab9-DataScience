"""Paleta y estilo comunes para todas las piezas de la infografía."""
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# 2 tonos fríos temáticos + neutros + 1 acento cálido (complementario del azul)
NAVY = "#14365D"      # serie principal / titulares
TEAL = "#1F7A7A"      # serie secundaria / comparaciones
GREY = "#A3ADB8"      # contexto, series no destacadas
LIGHT = "#E9EDF1"     # fondos de tarjetas y rejillas
INK = "#1E2329"       # texto
MUTED = "#5B6670"     # texto secundario
ACCENT = "#E8702A"    # picos, anomalías y pronóstico (rellenos y cifras grandes)
ACCENT_TEXT = "#B8501A"  # acento oscurecido para texto pequeño (contraste 5:1)
BG = "#FFFFFF"

DPI = 300


def apply_style():
    plt.rcParams.update({
        "font.family": "Arial",
        "font.size": 11,
        "text.color": INK,
        "axes.labelcolor": MUTED,
        "axes.edgecolor": GREY,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": LIGHT,
        "grid.linewidth": 0.8,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "ytick.left": False,
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "savefig.facecolor": BG,
        "savefig.dpi": DPI,
    })


def thousands(ax, axis="y"):
    fmt = mticker.FuncFormatter(lambda x, _: f"{x / 1e3:,.0f} K")
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def millions(value, decimals=1):
    return f"{value / 1e6:,.{decimals}f} M"


def title(ax, text, subtitle=None):
    ax.set_title(text, loc="left", fontsize=15, fontweight="bold", color=INK, pad=26 if subtitle else 10)
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=10.5, color=MUTED, va="bottom")
