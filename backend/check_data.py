import pandas as pd

a = pd.read_csv("../data/actuals.csv")
print("Actuals columns:", a.columns.tolist())
if "fuelType" in a.columns:
    print("Fuel types present:", a["fuelType"].unique())
print("Actuals rows:", len(a))
print("Duplicate startTimes in actuals:", a["startTime"].duplicated().sum())
print(a.head(4))

m = pd.read_csv("../data/merged.csv", parse_dates=["startTime"])
m["day"] = m["startTime"].dt.date
daily = m.groupby("day").agg(
    actual=("actual", "mean"),
    forecast=("forecast", "mean"),
    bias=("error", "mean"),
    mae=("abs_error", "mean"),
).round(0)
print()
print(daily.to_string())
