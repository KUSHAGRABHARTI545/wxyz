import pandas as pd

a = pd.read_csv("../data/actuals.csv")
f = pd.read_csv("../data/forecasts.csv")

print("ACTUALS columns:", a.columns.tolist())
print("ACTUALS rows:", len(a))
print(a.head(3))

f["publishTime"] = pd.to_datetime(f["publishTime"], utc=True)
f["startTime"] = pd.to_datetime(f["startTime"], utc=True)
f["horizon_h"] = (f["startTime"] - f["publishTime"]).dt.total_seconds() / 3600

print()
print("Forecast startTime range:", f["startTime"].min(), "->", f["startTime"].max())
print("Forecast publishTime range:", f["publishTime"].min(), "->", f["publishTime"].max())
print("Unique publish times:", f["publishTime"].nunique())
print()
print("Horizon in hours (startTime minus publishTime):")
print(f["horizon_h"].describe())
print()
print("First 10 distinct publish times:")
print(f["publishTime"].drop_duplicates().sort_values().head(10).to_string())
