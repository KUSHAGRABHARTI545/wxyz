import { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid,
  ResponsiveContainer, BarChart, Bar,
} from "recharts";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const n = (v) => Math.round(v).toLocaleString();

export default function App() {
  const [start, setStart] = useState("2026-01-01");
  const [end, setEnd] = useState("2026-01-07");
  const [cutoff, setCutoff] = useState(9);
  const [series, setSeries] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [daily, setDaily] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const q = `start=${start}&end=${end}&cutoff_hour=${cutoff}`;
    setError("");
    Promise.all([
      fetch(`${API}/api/series?${q}`).then((r) => r.json()),
      fetch(`${API}/api/metrics?${q}`).then((r) => r.json()),
      fetch(`${API}/api/daily?cutoff_hour=${cutoff}`).then((r) => r.json()),
    ])
      .then(([s, m, d]) => {
        setSeries(s.map((p) => ({ ...p, label: p.startTime.slice(5, 16).replace("T", " ") })));
        setMetrics(m);
        setDaily(d);
      })
      .catch(() => setError("Could not reach the API. Is the backend running?"));
  }, [start, end, cutoff]);

  const cards = metrics && metrics.n_points
    ? [
        ["Mean abs. error (MAE)", `${n(metrics.mae_mw)} MW`],
        ["RMSE", `${n(metrics.rmse_mw)} MW`],
        ["Bias (forecast − actual)", `${n(metrics.bias_mw)} MW`],
        ["95th percentile error", `${n(metrics.p95_abs_error_mw)} MW`],
        ["MAPE", `${metrics.mape_pct.toFixed(1)} %`],
        ["Hourly points", n(metrics.n_points)],
      ]
    : [];

  return (
    <div className="page">
      <h1>UK Wind Forecast Dashboard</h1>
      <p className="sub">
        Latest forecast available at the day-ahead decision cut-off vs actual national wind generation, January 2026.
      </p>

      <div className="controls">
        <label>From
          <input type="date" value={start} min="2026-01-01" max="2026-01-31"
                 onChange={(e) => setStart(e.target.value)} />
        </label>
        <label>To
          <input type="date" value={end} min="2026-01-01" max="2026-01-31"
                 onChange={(e) => setEnd(e.target.value)} />
        </label>
        <label>Decision cut-off (UTC, day before)
          <select value={cutoff} onChange={(e) => setCutoff(Number(e.target.value))}>
            {[6, 7, 8, 9, 10, 11, 12].map((h) => (
              <option key={h} value={h}>{String(h).padStart(2, "0")}:00</option>
            ))}
          </select>
        </label>
      </div>

      {error && <p className="err">{error}</p>}

      <div className="cards">
        {cards.map(([t, v]) => (
          <div className="card" key={t}><span>{t}</span><b>{v}</b></div>
        ))}
      </div>
      {metrics && metrics.n_points > 0 && (
        <p className="note">
          Planning tip: in 95% of hours the forecast was within {n(metrics.p95_abs_error_mw)} MW
          of actual generation. A positive bias means the forecast tends to overestimate wind,
          so extra power may be needed.
        </p>
      )}

      <h2>Actual vs forecast (MW)</h2>
      <div className="chart">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={series}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" minTickGap={40} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="actual" name="Actual" stroke="#16a34a" dot={false} />
            <Line type="monotone" dataKey="forecast" name="Forecast" stroke="#2563eb" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <h2>Average daily bias (MW) across January</h2>
      <div className="chart small">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={daily}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" tickFormatter={(d) => d.slice(8)} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="bias" name="Bias" fill="#f59e0b" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
