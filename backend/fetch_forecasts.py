import requests
import pandas as pd
from datetime import datetime, timedelta

URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream"

start = datetime(2025, 12, 25)   # forecasts for 1 Jan are published earlier
end = datetime(2026, 1, 31)
step = timedelta(days=3)

frames = []
cur = start
while cur < end:
    nxt = min(cur + step, end)
    params = {
        "publishDateTimeFrom": cur.strftime("%Y-%m-%dT%H:%MZ"),
        "publishDateTimeTo": nxt.strftime("%Y-%m-%dT%H:%MZ"),
    }
    r = requests.get(URL, params=params, timeout=120)
    print(cur.date(), "->", nxt.date(), "status:", r.status_code)
    if r.status_code != 200:
        print(r.text[:500])
        break
    data = r.json()
    print("  rows:", len(data))
    if data:
        frames.append(pd.DataFrame(data))
    cur = nxt

if frames:
    df = pd.concat(frames, ignore_index=True).drop_duplicates()
    print(df.head())
    print(df.columns.tolist())
    print("Total rows:", len(df))
    df.to_csv("../data/forecasts.csv", index=False)
    