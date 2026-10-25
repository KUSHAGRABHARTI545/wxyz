import pandas as pd
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
CUTOFF_HOUR_UTC = 9  # decision cut-off on the day before delivery


def load_data():
    a = pd.read_csv(DATA / "actuals.csv", usecols=["startTime", "generation"])
    f = pd.read_csv(DATA / "forecasts.csv",
                    usecols=["publishTime", "startTime", "generation"])
    a["startTime"] = pd.to_datetime(a["startTime"], utc=True)
    f["startTime"] = pd.to_datetime(f["startTime"], utc=True)
    f["publishTime"] = pd.to_datetime(f["publishTime"], utc=True)
    a = a.rename(columns={"generation": "actual"})
    f = f.rename(columns={"generation": "forecast"})
    return a, f


def latest_forecast_before_cutoff(f, cutoff_hour=CUTOFF_HOUR_UTC):
    """For each target half-hour, keep the latest forecast published
    at or before 'cutoff_hour' UTC on the previous day."""
    f = f.copy()
    target_day = f["startTime"].dt.floor("D")
    f["cutoff"] = target_day - pd.Timedelta(days=1) + pd.Timedelta(hours=cutoff_hour)
    f = f[f["publishTime"] <= f["cutoff"]]
    f = f.sort_values("publishTime").groupby("startTime", as_index=False).last()
    f["horizon_h"] = (f["startTime"] - f["publishTime"]).dt.total_seconds() / 3600
    return f


def build_dataset(cutoff_hour=CUTOFF_HOUR_UTC):
    a, f = load_data()
    chosen = latest_forecast_before_cutoff(f, cutoff_hour)
    df = a.merge(chosen, on="startTime", how="inner")
    df = df[(df["startTime"] >= "2026-01-01") & (df["startTime"] < "2026-02-01")]
    df["error"] = df["forecast"] - df["actual"]
    df["abs_error"] = df["error"].abs()
    return df.sort_values("startTime").reset_index(drop=True)


def compute_metrics(df):
    nonzero = df[df["actual"] > 0]
    return {
        "n_points": int(len(df)),
        "mae_mw": float(df["abs_error"].mean()),
        "rmse_mw": float((df["error"] ** 2).mean() ** 0.5),
        "bias_mw": float(df["error"].mean()),
        "mape_pct": float((nonzero["abs_error"] / nonzero["actual"]).mean() * 100),
        "p90_abs_error_mw": float(df["abs_error"].quantile(0.90)),
        "p95_abs_error_mw": float(df["abs_error"].quantile(0.95)),
    }


if __name__ == "__main__":
    df = build_dataset()
    print("Target half-hours matched:", len(df), "(expect about 1488)")
    print("Chosen forecast horizon (h):")
    print(df["horizon_h"].describe())
    print()
    for k, v in compute_metrics(df).items():
        print(f"{k}: {round(v, 2)}")
    print()
    print(df.head())
    df.to_csv("../data/merged.csv", index=False)
    