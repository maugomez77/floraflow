import { useEffect, useState } from "react";
import { Satellite, TrendingUp, TrendingDown, Minus, Brain, Loader2 } from "lucide-react";
import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  PolarAngleAxis,
} from "recharts";
import { getCropHealth, analyzeCropHealth } from "../services/api";
import type { CropHealthReport } from "../types";
import { useLang } from "../i18n/LangContext";
import AIResultRenderer from "../components/AIResultRenderer";

function healthColor(score: number): string {
  if (score >= 80) return "#059669"; // green
  if (score >= 60) return "#f59e0b"; // yellow
  if (score >= 40) return "#ea580c"; // orange
  return "#dc2626"; // red
}

function healthLabel(score: number, t: (k: string) => string): string {
  if (score >= 80) return t("satellite.healthy");
  if (score >= 60) return t("satellite.watch");
  if (score >= 40) return t("satellite.stress");
  return t("satellite.critical");
}

function ndviColor(ndvi: number): string {
  if (ndvi >= 0.6) return "#059669";
  if (ndvi >= 0.4) return "#f59e0b";
  if (ndvi >= 0.2) return "#ea580c";
  return "#dc2626";
}

function trendIcon(trend: string) {
  if (trend === "improving") return <TrendingUp size={14} />;
  if (trend === "declining") return <TrendingDown size={14} />;
  return <Minus size={14} />;
}

function trendEmoji(trend: string): string {
  if (trend === "improving") return "📈";
  if (trend === "declining") return "📉";
  return "➡️";
}

function trendColor(trend: string): string {
  if (trend === "improving") return "#059669";
  if (trend === "declining") return "#dc2626";
  return "#6b7280";
}

function fmtMunicipality(m: string): string {
  return m.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function SatellitePage() {
  const { t, lang } = useLang();
  const [reports, setReports] = useState<CropHealthReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [analysisResult, setAnalysisResult] = useState<Record<string, unknown> | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState("");

  useEffect(() => {
    getCropHealth()
      .then(setReports)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const runAnalysis = async () => {
    setAnalysisLoading(true);
    setAnalysisError("");
    setAnalysisResult(null);
    try {
      const data = await analyzeCropHealth();
      setAnalysisResult(data);
    } catch (e: unknown) {
      setAnalysisError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setAnalysisLoading(false);
    }
  };

  if (loading)
    return (
      <div className="loading">
        <div className="spinner" />
        {t("common.loading")}
      </div>
    );

  if (error) return <div className="error-box">{error}</div>;

  const avgScore =
    reports.length > 0
      ? Math.round(reports.reduce((sum, r) => sum + r.health_score, 0) / reports.length)
      : 0;
  const avgColor = healthColor(avgScore);
  const healthyCount = reports.filter((r) => r.health_score >= 80).length;
  const watchCount = reports.filter((r) => r.health_score >= 60 && r.health_score < 80).length;
  const stressCount = reports.filter((r) => r.health_score >= 40 && r.health_score < 60).length;
  const criticalCount = reports.filter((r) => r.health_score < 40).length;

  return (
    <>
      <div className="page-header">
        <h2>
          <Satellite size={28} style={{ marginRight: 8, verticalAlign: "middle" }} />
          {t("satellite.title")}
        </h2>
        <p>{t("satellite.subtitle")}</p>
      </div>

      {/* Overall summary */}
      <div
        className="card"
        style={{
          padding: 24,
          marginBottom: 20,
          background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
          color: "#e2e8f0",
          border: "none",
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "auto 1fr auto",
            gap: 24,
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <div style={{ width: 140, height: 140, position: "relative" }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart
                innerRadius="72%"
                outerRadius="100%"
                data={[{ name: "avg", value: avgScore, fill: avgColor }]}
                startAngle={90}
                endAngle={-270}
              >
                <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
                <RadialBar background={{ fill: "#334155" }} dataKey="value" cornerRadius={10} />
              </RadialBarChart>
            </ResponsiveContainer>
            <div
              style={{
                position: "absolute",
                inset: 0,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                pointerEvents: "none",
              }}
            >
              <div style={{ fontSize: "2rem", fontWeight: 800, color: avgColor }}>{avgScore}</div>
              <div style={{ fontSize: "0.65rem", color: "#94a3b8", letterSpacing: "0.05em" }}>
                / 100
              </div>
            </div>
          </div>

          <div>
            <div
              style={{
                fontSize: "0.7rem",
                textTransform: "uppercase",
                letterSpacing: "0.1em",
                color: "#94a3b8",
                marginBottom: 4,
              }}
            >
              {lang === "es" ? "Salud General del Sistema" : "Overall System Health"}
            </div>
            <div style={{ fontSize: "1.6rem", fontWeight: 700, color: "#fff", marginBottom: 8 }}>
              {healthLabel(avgScore, t)}
            </div>
            <div style={{ display: "flex", gap: 16, flexWrap: "wrap", fontSize: "0.82rem" }}>
              <span style={{ color: "#059669" }}>
                ● {healthyCount} {t("satellite.healthy")}
              </span>
              <span style={{ color: "#f59e0b" }}>
                ● {watchCount} {t("satellite.watch")}
              </span>
              <span style={{ color: "#ea580c" }}>
                ● {stressCount} {t("satellite.stress")}
              </span>
              <span style={{ color: "#dc2626" }}>
                ● {criticalCount} {t("satellite.critical")}
              </span>
            </div>
            <div style={{ fontSize: "0.72rem", color: "#64748b", marginTop: 8, fontFamily: "monospace" }}>
              {reports.length} {lang === "es" ? "municipios monitoreados" : "municipalities monitored"} ·{" "}
              {lang === "es" ? "datos Open-Meteo" : "Open-Meteo feed"}
            </div>
          </div>

          <button
            className="btn btn-primary"
            onClick={runAnalysis}
            disabled={analysisLoading}
            style={{ whiteSpace: "nowrap" }}
          >
            {analysisLoading ? (
              <>
                <Loader2 size={16} className="ai-spin" /> {t("ai.processing")}
              </>
            ) : (
              <>
                <Brain size={16} /> {t("satellite.analyze")}
              </>
            )}
          </button>
        </div>
      </div>

      {analysisError && <div className="error-box" style={{ marginBottom: 16 }}>{analysisError}</div>}

      {analysisResult && (
        <div className="card ai-result-card" style={{ marginBottom: 24 }}>
          <div className="card-header">
            <h3>
              <Brain size={18} style={{ verticalAlign: "middle", marginRight: 6 }} />
              {t("satellite.analyze")}
            </h3>
          </div>
          <div style={{ padding: 20 }}>
            <AIResultRenderer data={analysisResult} />
          </div>
        </div>
      )}

      {/* Municipality cards grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
          gap: 16,
        }}
      >
        {reports.map((r, idx) => {
          const color = healthColor(r.health_score);
          const score = Math.round(r.health_score);
          return (
            <div
              key={r.id || `${r.municipality}-${idx}`}
              className="card"
              style={{
                padding: 18,
                borderTop: `3px solid ${color}`,
                display: "flex",
                flexDirection: "column",
                gap: 12,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: "1.05rem", color: "#2a1a3a" }}>
                    {fmtMunicipality(r.municipality)}
                  </h3>
                  <div style={{ fontSize: "0.72rem", color: "#888", marginTop: 2, fontFamily: "monospace" }}>
                    {r.farm_ids.length} {lang === "es" ? "granjas" : "farms"}
                  </div>
                </div>
                <span
                  className="badge"
                  style={{
                    background: `${trendColor(r.trend)}18`,
                    color: trendColor(r.trend),
                    border: `1px solid ${trendColor(r.trend)}40`,
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 4,
                  }}
                >
                  <span>{trendEmoji(r.trend)}</span>
                  {trendIcon(r.trend)}
                  {t(`satellite.${r.trend}`)}
                </span>
              </div>

              {/* Health gauge */}
              <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                <div style={{ width: 110, height: 110, position: "relative", flexShrink: 0 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <RadialBarChart
                      innerRadius="70%"
                      outerRadius="100%"
                      data={[{ name: "hs", value: score, fill: color }]}
                      startAngle={90}
                      endAngle={-270}
                    >
                      <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
                      <RadialBar background={{ fill: "#f0e8f5" }} dataKey="value" cornerRadius={8} />
                    </RadialBarChart>
                  </ResponsiveContainer>
                  <div
                    style={{
                      position: "absolute",
                      inset: 0,
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      pointerEvents: "none",
                    }}
                  >
                    <div style={{ fontSize: "1.6rem", fontWeight: 800, color, lineHeight: 1 }}>{score}</div>
                    <div style={{ fontSize: "0.6rem", color: "#888", marginTop: 2 }}>
                      {t("satellite.healthScore")}
                    </div>
                  </div>
                </div>

                <div style={{ flex: 1, display: "grid", gap: 6, fontSize: "0.78rem" }}>
                  <MetricRow
                    label={t("satellite.ndvi")}
                    value={r.ndvi_estimate.toFixed(2)}
                    dotColor={ndviColor(r.ndvi_estimate)}
                  />
                  <MetricRow
                    label={t("satellite.moisture")}
                    value={`${(r.soil_moisture * 100).toFixed(0)}%`}
                  />
                  <MetricRow label={t("satellite.soilTemp")} value={`${r.soil_temp_c.toFixed(1)} °C`} />
                  <MetricRow label={t("satellite.et0")} value={`${r.et0_mm.toFixed(1)} mm`} />
                </div>
              </div>

              {/* Stress indicators */}
              {r.stress_indicators.length > 0 && (
                <div>
                  <div
                    style={{
                      fontSize: "0.68rem",
                      color: "#888",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                      marginBottom: 4,
                    }}
                  >
                    {t("satellite.stressIndicators")}
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                    {r.stress_indicators.map((s, i) => (
                      <span
                        key={i}
                        className="badge badge-red"
                        style={{ fontSize: "0.68rem" }}
                      >
                        {s.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {r.farm_ids.length > 0 && (
                <div
                  style={{
                    fontSize: "0.66rem",
                    color: "#999",
                    fontFamily: "monospace",
                    borderTop: "1px dashed #eee",
                    paddingTop: 6,
                    wordBreak: "break-all",
                  }}
                >
                  {r.farm_ids.slice(0, 3).join(" · ")}
                  {r.farm_ids.length > 3 && ` +${r.farm_ids.length - 3}`}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </>
  );
}

function MetricRow({
  label,
  value,
  dotColor,
}: {
  label: string;
  value: string;
  dotColor?: string;
}) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <span style={{ color: "#666", display: "inline-flex", alignItems: "center", gap: 6 }}>
        {dotColor && (
          <span
            style={{
              display: "inline-block",
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: dotColor,
            }}
          />
        )}
        {label}
      </span>
      <strong style={{ color: "#2a1a3a", fontFamily: "monospace" }}>{value}</strong>
    </div>
  );
}
