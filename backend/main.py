from functools import lru_cache

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from core import build_dataset, compute_metrics

app = FastAPI(title="Wind Forecast API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=24)
def cached_dataset(cutoff_hour: int) -> pd.DataFrame:
    return build_dataset(cutoff_hour)


def get_slice(start: str, end: str, cutoff_hour: int) -> pd.DataFrame:
    df = cached_dataset(cutoff_hour)
    lo = pd.Timestamp(start, tz="UTC")
    hi = pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1)
    return df[(df["startTime"] >= lo) & (df["startTime"] < hi)]


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/series")
def series(
    start: str = "2026-01-01",
    end: str = "2026-01-31",
    cutoff_hour: int = Query(9, ge=0, le=23),
):
    df = get_slice(start, end, cutoff_hour).copy()
    df["startTime"] = df["startTime"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df["publishTime"] = df["publishTime"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    cols = ["startTime", "actual", "forecast", "publishTime", "horizon_h", "error"]
    return df[cols].to_dict("records")


@app.get("/api/metrics")
def metrics(
    start: str = "2026-01-01",
    end: str = "2026-01-31",
    cutoff_hour: int = Query(9, ge=0, le=23),
):
    df = get_slice(start, end, cutoff_hour)
    if df.empty:
        return {"n_points": 0}
    return compute_metrics(df)


@app.get("/api/daily")
def daily(cutoff_hour: int = Query(9, ge=0, le=23)):
    df = cached_dataset(cutoff_hour).copy()
    df["day"] = df["startTime"].dt.strftime("%Y-%m-%d")
    out = df.groupby("day").agg(
        actual=("actual", "mean"),
        forecast=("forecast", "mean"),
        bias=("error", "mean"),
        mae=("abs_error", "mean"),
    ).round(0).reset_index()
    return out.to_dict("records")
