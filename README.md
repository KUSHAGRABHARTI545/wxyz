# Wind Forecast Dashboard (Elexon, January 2026)

A web app for a UK energy utility that buys power day-ahead. It shows the
latest wind generation forecast available at the day-ahead decision time and
quantifies how accurate that forecast was against actual wind generation.

**Deployed app:** https://wxyz-lake.vercel.app/
**Backend API:** https://wxyz-w8nx.onrender.com/api/health

Note: the backend runs on a free Render instance that sleeps when idle, so
the first load can take 30-60 seconds.

## Data (Elexon only)
- Actuals: FUELHH, filtered to fuelType WIND (half-hourly, January 2026)
- Forecasts: WINDFOR (hourly target times, published about 8 times a day)

## Method and assumptions
- Day-ahead decision time: 09:00 UTC on the day before the target hour
  (an assumption; the cut-off hour is configurable in the UI and API).
- For each target hour, the latest forecast published at or before that
  cut-off is used.
- Actuals are compared with forecasts on an hourly basis (744 matched hours).
- Metrics: MAE, RMSE, bias (forecast minus actual), MAPE, P90 and P95
  absolute error.
- With the 09:00 cut-off: MAE about 2,127 MW, RMSE about 2,606 MW, bias about
  +1,851 MW (the forecast tends to overestimate), MAPE about 22.2%.

## Project structure
- `backend/` Python FastAPI service
  - `main.py` API endpoints: /api/health, /api/series, /api/metrics, /api/daily
    (query params: start, end, cutoff_hour)
  - `core.py` forecast selection, joining with actuals, error metrics
  - `fetch_data.py`, `fetch_forecasts.py` download data from Elexon
  - `explore.py`, `check_data.py` data exploration and sanity checks
  - `requirements.txt`, `Dockerfile`
- `data/` `actuals.csv`, `forecasts.csv`, `merged.csv`
- `frontend/` React (Vite) dashboard with Recharts; reads the API address
  from `VITE_API_URL`
- `docker-compose.yml` runs backend and frontend together

## How to start the app
With Docker: Open http://localhost:3000 (the API runs on http://localhost:8000).

Without Docker: cd backend
pip install -r requirements.txt
uvicorn main:app --port 8000

In a second terminal:
cd frontend
npm install
npm run dev


## Deployment
- Backend: Render (Docker, `backend/Dockerfile`, build context = repo root)
- Frontend: Vercel (root directory `frontend`, env var `VITE_API_URL`
  set to the backend URL)

## AI tools
AI tools (Claude) were used to help plan, write and debug this project and
to help prepare this README.
