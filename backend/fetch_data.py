import requests
import pandas as pd

BASE = "https://data.elexon.co.uk/bmrs/api/v1/datasets"

r = requests.get(
    f"{BASE}/FUELHH/stream",
    params={
        "settlementDateFrom": "2026-01-01",
        "settlementDateTo": "2026-01-31",
        "fuelType": "WIND",
    },
    timeout=120,
)
print("Status:", r.status_code)
r.raise_for_status()

actuals = pd.DataFrame(r.json())
print(actuals.head())
print(actuals.columns.tolist())
print("Rows:", len(actuals))
actuals.to_csv("../data/actuals.csv", index=False)
