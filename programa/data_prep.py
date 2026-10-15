"""Carga de la base de migración y construcción de las series del Lab 1."""
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "raw" / "Base_Migracion_2009-2026jun.xlsx"

COUNTRIES = ["El Salvador", "Estados Unidos de América", "Honduras"]
COUNTRY_LABELS = {"El Salvador": "El Salvador", "Estados Unidos de América": "EE. UU.",
                  "Honduras": "Honduras"}


def load_data(path=DATA_FILE):
    df = pd.read_excel(path, sheet_name="Datos")
    df["Fecha"] = pd.to_datetime(dict(year=df["Año"], month=df["Mes cod"], day=1))
    return df


def build_series(df):
    """Mismas definiciones del Lab 1: Turista + Excursionista; Marítima = Cruceristas 2009-2022."""
    full_range = pd.date_range(df["Fecha"].min(), df["Fecha"].max(), freq="MS")
    base = df[df["Tipo de Viajero"].isin(["Turista", "Excursionista"])]

    def monthly(frame, idx=full_range):
        return frame.groupby("Fecha")["Viajero"].sum().reindex(idx).fillna(0).asfreq("MS")

    sea_range = pd.date_range("2009-01-01", "2022-12-01", freq="MS")
    series = {
        "Total": monthly(base),
        "Aérea": monthly(base[base["Vía"] == "Aérea"]),
        "Terrestre": monthly(base[base["Vía"] == "Terrestre"]),
        "Marítima": monthly(df[(df["Vía"] == "Marítima") & (df["Tipo de Viajero"] == "Cruceristas")],
                            sea_range),
    }
    for c in COUNTRIES:
        series[COUNTRY_LABELS[c]] = monthly(base[base["País"] == c])
    return series


def indicators(s):
    """Indicadores del análisis comparativo (Lab 1, Notebook 2, sección 11)."""
    pre = np.log1p(s.loc["2009":"2019"])
    dec = seasonal_decompose(pre, model="additive", period=12)
    ok = dec.resid.notna()
    resid, seas = dec.resid[ok], dec.seasonal[ok]
    slope = np.polyfit(np.arange(len(pre)), pre.values, 1)[0]
    y19 = s[(s.index.year == 2019) & (s.index.month >= 4)].sum()
    y20 = s[(s.index.year == 2020) & (s.index.month >= 4)].sum()
    return {
        "seasonality": max(0, 1 - np.var(resid) / np.var(resid + seas)),
        "growth_pct": (np.exp(12 * slope) - 1) * 100,
        "volatility": resid.std(),
        "covid_drop_pct": (1 - y20 / y19) * 100,
    }


def comparison_table(series):
    names = ["Aérea", "Terrestre", "Marítima", "El Salvador", "EE. UU.", "Honduras"]
    t = pd.DataFrame({n: indicators(series[n]) for n in names}).T
    t["group"] = ["Vía"] * 3 + ["País"] * 3
    return t


def recovery_index(s, years=range(2019, 2026)):
    """Año completo como % de 2019 (2019 = 100)."""
    annual = s.groupby(s.index.year).sum()
    return (annual.reindex(list(years)) / annual.loc[2019] * 100).dropna()


def kpis(series):
    total = series["Total"]
    annual = total.groupby(total.index.year).sum()
    rec = recovery_index(total)
    return {
        "accumulated": total.sum(),
        "peak_year": int(annual.loc[:2025].idxmax()),
        "peak_value": annual.loc[:2025].max(),
        "covid_drop_pct": indicators(total)["covid_drop_pct"],
        "recovery_2025_pct": rec.loc[2025],
        "value_2025": annual.loc[2025],
        "seasonality": indicators(total)["seasonality"],
    }


def seasonal_profile(s, years):
    """Índice estacional: cada mes como % del promedio mensual de su año."""
    sub = s[s.index.year.isin(years)]
    ratio = sub / sub.groupby(sub.index.year).transform("mean") * 100
    return ratio.groupby(ratio.index.month).mean()
