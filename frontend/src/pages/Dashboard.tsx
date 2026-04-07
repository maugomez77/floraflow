import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  Warehouse,
  Ruler,
  Truck,
  Sprout,
  DollarSign,
  AlertTriangle,
  TrendingUp,
  Calendar,
} from "lucide-react";
import { getStats, getDemand, getWeatherAlerts, getSignals } from "../services/api";
import type { FlowStats, MarketDemand, WeatherAlert, PriceSignal } from "../types";
import { useLang } from "../i18n/LangContext";

const formatMXN = (v: number) =>
  `$${v.toLocaleString("es-MX", { minimumFractionDigits: 0 })}`;

const formatNumber = (v: number) => v.toLocaleString("es-MX");

const eventColors: Record<string, string> = {
  valentines: "#e91e63",
  mothers_day: "#e91e63",
  dia_muertos: "#ff9800",
  xmas: "#4caf50",
  weddings: "#9c27b0",
  none: "#999",
};

const eventLabels: Record<string, string> = {
  valentines: "San Valentin",
  mothers_day: "Dia de las Madres",
  dia_muertos: "Dia de Muertos",
  xmas: "Navidad",
  weddings: "Temporada de Bodas",
};

export default function Dashboard() {
  const { t } = useLang();
  const [stats, setStats] = useState<FlowStats | null>(null);
  const [demand, setDemand] = useState<MarketDemand[]>([]);
  const [alerts, setAlerts] = useState<WeatherAlert[]>([]);
  const [signals, setSignals] = useState<PriceSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.allSettled([getStats(), getDemand(), getWeatherAlerts(), getSignals()])
      .then(([s, d, a, sig]) => {
        if (s.status === "fulfilled") setStats(s.value);
        if (d.status === "fulfilled") setDemand(d.value);
        if (a.status === "fulfilled") setAlerts(a.value);
        if (sig.status === "fulfilled") setSignals(sig.value);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        {t("dashboard.loading")}
      </div>
    );
  }

  if (error) {
    return <div className="error-box">{error}</div>;
  }

  // Aggregate demand by flower type for chart
  const demandByFlower = demand.reduce<Record<string, number>>((acc, d) => {
    const label = d.flower_type.charAt(0).toUpperCase() + d.flower_type.slice(1);
    acc[label] = (acc[label] || 0) + d.price_per_stem_mxn;
    return acc;
  }, {});
  const chartData = Object.entries(demandByFlower).map(([name, price]) => ({
    name,
    price: Math.round(price * 100) / 100,
  }));

  return (
    <>
      <div className="page-header">
        <h2>{t("dashboard.title")}</h2>
        <p>{t("dashboard.subtitle")}</p>
      </div>

      {/* KPI cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <Warehouse size={24} className="kpi-icon" />
          <span className="kpi-label">{t("dashboard.greenhouses")}</span>
          <span className="kpi-value">{stats?.total_greenhouses ?? 0}</span>
        </div>
        <div className="kpi-card">
          <Ruler size={24} className="kpi-icon" />
          <span className="kpi-label">{t("dashboard.area")}</span>
          <span className="kpi-value">
            {formatNumber(stats?.total_area_m2 ?? 0)}
          </span>
        </div>
        <div className="kpi-card">
          <Truck size={24} className="kpi-icon" />
          <span className="kpi-label">{t("dashboard.shipments")}</span>
          <span className="kpi-value">{stats?.active_shipments ?? 0}</span>
        </div>
        <div className="kpi-card">
          <Sprout size={24} className="kpi-icon" />
          <span className="kpi-label">{t("dashboard.stems")}</span>
          <span className="kpi-value">
            {formatNumber(stats?.weekly_stems_shipped ?? 0)}
          </span>
        </div>
        <div className="kpi-card">
          <DollarSign size={24} className="kpi-icon" />
          <span className="kpi-label">{t("dashboard.revenue")}</span>
          <span className="kpi-value">
            {formatMXN(stats?.revenue_mtd_mxn ?? 0)}
          </span>
        </div>
      </div>

      <div className="grid-2">
        {/* Weather Alerts */}
        <div className="card">
          <div className="card-header">
            <h3>
              <AlertTriangle size={18} style={{ marginRight: 8, verticalAlign: "middle" }} />
              {t("dashboard.alerts")}
            </h3>
          </div>
          {alerts.length === 0 ? (
            <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
              {t("dashboard.noAlerts")}
            </p>
          ) : (
            alerts.slice(0, 5).map((a) => (
              <div key={a.id} className={`alert-card ${a.alert_type}`}>
                <div className="alert-title">
                  <span className={`badge severity-${a.severity}`}>
                    {a.severity.toUpperCase()}
                  </span>
                  {a.alert_type.replace("_", " ").toUpperCase()} — {a.municipality.replace("_", " ")}
                </div>
                <div className="alert-desc">{a.description}</div>
              </div>
            ))
          )}
        </div>

        {/* Market Demand Chart */}
        <div className="card">
          <div className="card-header">
            <h3>
              <TrendingUp size={18} style={{ marginRight: 8, verticalAlign: "middle" }} />
              {t("dashboard.demand")}
            </h3>
          </div>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8dff0" />
                <XAxis dataKey="name" fontSize={12} />
                <YAxis fontSize={12} />
                <Tooltip
                  formatter={(value) => [`$${value} MXN`, "Avg Price/Stem"]}
                />
                <Bar dataKey="price" fill="#7b2d8e" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
              {t("dashboard.noDemand")}
            </p>
          )}
        </div>

        {/* Price Signals */}
        <div className="card">
          <div className="card-header">
            <h3>
              <TrendingUp size={18} style={{ marginRight: 8, verticalAlign: "middle" }} />
              {t("dashboard.signals")}
            </h3>
          </div>
          {signals.length === 0 ? (
            <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
              {t("dashboard.noSignals")}
            </p>
          ) : (
            signals.slice(0, 5).map((s) => (
              <div key={s.id} className="signal-item">
                <span className={`badge severity-${s.priority}`}>
                  {s.priority.toUpperCase()}
                </span>
                <div>
                  <div style={{ fontWeight: 600, fontSize: "0.85rem" }}>
                    {s.flower_type} — {s.signal_type.replace("_", " ")}
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                    {s.description}
                  </div>
                  <div
                    style={{
                      fontSize: "0.75rem",
                      color: "var(--accent)",
                      marginTop: 4,
                    }}
                  >
                    {t("dashboard.action")}: {s.recommended_action}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Upcoming Events */}
        <div className="card">
          <div className="card-header">
            <h3>
              <Calendar size={18} style={{ marginRight: 8, verticalAlign: "middle" }} />
              {t("dashboard.events")}
            </h3>
          </div>
          {(stats?.upcoming_events ?? []).length === 0 ? (
            <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
              {t("dashboard.noEvents")}
            </p>
          ) : (
            (stats?.upcoming_events ?? []).map((ev, i) => (
              <div key={i} className="event-item">
                <div
                  className="event-dot"
                  style={{ background: eventColors[ev] || "#7b2d8e" }}
                />
                <span style={{ fontWeight: 500, fontSize: "0.9rem" }}>
                  {eventLabels[ev] || ev.replace("_", " ")}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
}
