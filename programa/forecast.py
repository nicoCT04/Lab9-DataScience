"""Reproduce ARIMA del Lab 1 y añade su intervalo predictivo, sin usar el test al ajustar."""
import json

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

from data_prep import ROOT


def evaluate(total):
    comparison = pd.read_csv(ROOT / "data/processed/modelos_total_lab1.csv")
    comparison = comparison.sort_values("rmse").reset_index(drop=True)
    cut = int(len(total) * 0.70)
    train, test = total.iloc[:cut], total.iloc[cut:]
    fit = SARIMAX(np.log(train), order=(1, 1, 1),
                  enforce_stationarity=True, enforce_invertibility=True).fit(disp=False)
    if not fit.mle_retvals["converged"]:
        raise RuntimeError("ARIMA no convergió; revisar antes de presentar el pronóstico")
    forecast = fit.get_forecast(steps=len(test))
    bounds = np.exp(forecast.conf_int(alpha=0.05))
    prediction = np.exp(forecast.predicted_mean)
    # exp(mu) reproduce el pronóstico original: mediana, no media lognormal corregida.
    mae = float(np.mean(np.abs(test - prediction)))
    rmse = float(np.sqrt(np.mean((test - prediction) ** 2)))
    reference = comparison.iloc[0]
    if not np.allclose([mae, rmse], reference[["mae", "rmse"]].to_numpy(float), atol=1, rtol=0):
        raise ValueError(f"El ajuste no reproduce Lab 1: MAE={mae}, RMSE={rmse}")
    frame = pd.DataFrame({"real": test, "estimacion": prediction,
                          "inferior_95": bounds.iloc[:, 0], "superior_95": bounds.iloc[:, 1]})
    frame.index.name = "fecha"
    summary = {
        "fuente_metricas": "Lab1DataScience/notebooks/Lab1_Series_Tiempo.ipynb, sección 21, salida Total",
        "serie": "Turista + Excursionista", "modelo": "ARIMA(1,1,1) sobre log(Total)",
        "train_inicio": str(train.index[0].date()), "train_fin": str(train.index[-1].date()),
        "test_inicio": str(test.index[0].date()), "test_fin": str(test.index[-1].date()),
        "n_train": len(train), "n_test": len(test), "mae_reproducido": mae,
        "rmse_reproducido": rmse, "nivel_intervalo": 0.95,
        "intervalo": "Predictivo puntual condicional al ARIMA; límites logarítmicos invertidos con exp; no es garantía simultánea ni incorpora cambios estructurales.",
        "pronostico": "Retrospectivo sobre prueba, sin reajustar con sus datos; no es proyección posterior a junio de 2026.",
        "complemento_24_meses": {"ganador": "Holt-Winters", "mae": 17581.15, "rmse": 20776.87},
    }
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    frame.to_csv(out / "b4_pronostico.csv")
    (out / "b4_validacion.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return comparison, frame
