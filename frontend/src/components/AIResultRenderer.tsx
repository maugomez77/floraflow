import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

interface Props {
  data: Record<string, unknown>;
  type?: string;
}

const COLORS = {
  purple: "#7b2d8e",
  purpleLight: "#9c4dcc",
  pink: "#e91e63",
  pinkLight: "#ff6090",
  green: "#4caf50",
  greenLight: "#81c784",
  orange: "#f59e0b",
  red: "#dc2626",
  darkRed: "#991b1b",
  blue: "#3b82f6",
  gray: "#999",
};

const CHART_COLORS = [COLORS.purple, COLORS.pink, COLORS.green, COLORS.blue, COLORS.orange];

// Urgency badge colors
function urgencyStyle(urgency: string): React.CSSProperties {
  const u = (urgency || "").toLowerCase().replace(/\s+/g, "_");
  if (u === "sell_today" || u === "urgent" || u === "high")
    return { background: COLORS.red, color: "#fff" };
  if (u === "this_week" || u === "medium" || u === "moderate")
    return { background: COLORS.orange, color: "#fff" };
  return { background: COLORS.green, color: "#fff" };
}

// Risk level colors
function riskColor(level: string): string {
  const l = (level || "").toLowerCase();
  if (l === "critical") return COLORS.darkRed;
  if (l === "high" || l === "alto") return COLORS.red;
  if (l === "medium" || l === "medio" || l === "moderate") return COLORS.orange;
  if (l === "low" || l === "bajo") return COLORS.green;
  return COLORS.gray;
}

// Demand level color
function demandColor(level: string): string {
  const l = (level || "").toLowerCase();
  if (l === "high" || l === "alta" || l === "very_high") return COLORS.green;
  if (l === "medium" || l === "media") return COLORS.orange;
  if (l === "low" || l === "baja") return COLORS.red;
  return COLORS.purple;
}

// Shared styles
const badge: React.CSSProperties = {
  display: "inline-block",
  padding: "2px 10px",
  borderRadius: 12,
  fontSize: "0.75rem",
  fontWeight: 600,
  textTransform: "uppercase" as const,
  letterSpacing: "0.03em",
};

const tableStyle: React.CSSProperties = {
  width: "100%",
  borderCollapse: "collapse" as const,
  fontSize: "0.85rem",
  marginTop: 12,
};

const thStyle: React.CSSProperties = {
  textAlign: "left" as const,
  padding: "8px 12px",
  borderBottom: "2px solid #e8dff0",
  color: COLORS.purple,
  fontWeight: 600,
  fontSize: "0.78rem",
  textTransform: "uppercase" as const,
  letterSpacing: "0.04em",
};

const tdStyle: React.CSSProperties = {
  padding: "8px 12px",
  borderBottom: "1px solid #f0e8f5",
};

const cardGrid: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
  gap: 12,
  marginTop: 12,
};

const miniCard: React.CSSProperties = {
  background: "#faf5ff",
  borderRadius: 10,
  padding: "14px 16px",
  border: "1px solid #e8dff0",
};

const summaryBox: React.CSSProperties = {
  background: "linear-gradient(135deg, #faf5ff 0%, #fff0f5 100%)",
  borderRadius: 10,
  padding: "14px 18px",
  marginTop: 14,
  fontSize: "0.88rem",
  lineHeight: 1.65,
  color: "#444",
  borderLeft: `3px solid ${COLORS.purple}`,
};

const sectionTitle: React.CSSProperties = {
  fontSize: "0.82rem",
  fontWeight: 600,
  color: COLORS.purple,
  textTransform: "uppercase" as const,
  letterSpacing: "0.04em",
  marginBottom: 8,
  marginTop: 16,
};

// Format MXN currency
function fmtMXN(val: unknown): string {
  if (typeof val !== "number") return String(val ?? "-");
  return `$${val.toLocaleString("es-MX", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function fmtPct(val: unknown): string {
  if (typeof val !== "number") return String(val ?? "-");
  const sign = val >= 0 ? "+" : "";
  return `${sign}${val.toFixed(1)}%`;
}

// ─── Renderer for each detected shape ────────────────────────

function renderPricingRecommendations(data: Record<string, unknown>) {
  const recs = data.recommendations as Array<Record<string, unknown>>;
  if (!recs || recs.length === 0) return null;

  const chartData = recs.map((r) => ({
    name: String(r.flower_type || r.tipo_flor || ""),
    "Precio Actual": Number(r.current_avg_price_mxn || r.precio_actual || 0),
    "Precio Recomendado": Number(r.recommended_price_mxn || r.precio_recomendado || 0),
  }));

  return (
    <div>
      <div style={sectionTitle}>Comparacion de Precios (MXN)</div>
      <div className="ai-chart-container">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData} barGap={4}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e8dff0" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v}`} />
            <Tooltip formatter={(v) => fmtMXN(v)} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="Precio Actual" fill={COLORS.gray} radius={[4, 4, 0, 0]} />
            <Bar dataKey="Precio Recomendado" fill={COLORS.purple} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={sectionTitle}>Detalle de Recomendaciones</div>
      <div style={{ overflowX: "auto" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>Flor</th>
              <th style={thStyle}>Actual</th>
              <th style={thStyle}>Recomendado</th>
              <th style={thStyle}>Cambio</th>
              <th style={thStyle}>Mercado</th>
              <th style={thStyle}>Urgencia</th>
            </tr>
          </thead>
          <tbody>
            {recs.map((r, i) => (
              <tr key={i}>
                <td style={tdStyle}><strong>{String(r.flower_type || r.tipo_flor || "-")}</strong></td>
                <td style={tdStyle}>{fmtMXN(r.current_avg_price_mxn ?? r.precio_actual)}</td>
                <td style={{ ...tdStyle, color: COLORS.purple, fontWeight: 600 }}>
                  {fmtMXN(r.recommended_price_mxn ?? r.precio_recomendado)}
                </td>
                <td style={{ ...tdStyle, color: Number(r.change_pct ?? r.cambio_pct) >= 0 ? COLORS.green : COLORS.red }}>
                  {fmtPct(r.change_pct ?? r.cambio_pct)}
                </td>
                <td style={tdStyle}>{String(r.best_market || r.mejor_mercado || "-")}</td>
                <td style={tdStyle}>
                  <span style={{ ...badge, ...urgencyStyle(String(r.urgency || r.urgencia || "")) }}>
                    {String(r.urgency || r.urgencia || "-")}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {recs.length === 1 && typeof recs[0].reasoning === "string" && (
        <div style={summaryBox}>{String(recs[0].reasoning)}</div>
      )}
      {typeof data.summary === "string" && <div style={summaryBox}>{String(data.summary)}</div>}
    </div>
  );
}

function renderDemandForecast(data: Record<string, unknown>) {
  const forecast = data.forecast as Array<Record<string, unknown>>;
  if (!forecast || forecast.length === 0) return null;

  const chartData = forecast.map((f) => ({
    semana: `Sem ${f.week ?? f.semana ?? ""}`,
    Precio: Number(f.predicted_price_mxn ?? f.precio_predicho ?? 0),
    demandLevel: String(f.demand_level ?? f.nivel_demanda ?? ""),
  }));

  return (
    <div>
      <div style={sectionTitle}>Pronostico de Demanda</div>
      <div className="ai-chart-container">
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e8dff0" />
            <XAxis dataKey="semana" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v}`} />
            <Tooltip formatter={(v) => fmtMXN(v)} />
            <Line
              type="monotone"
              dataKey="Precio"
              stroke={COLORS.purple}
              strokeWidth={2.5}
              dot={{ fill: COLORS.purple, r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div style={sectionTitle}>Nivel de Demanda por Semana</div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 4 }}>
        {chartData.map((d, i) => (
          <span
            key={i}
            style={{
              ...badge,
              background: demandColor(d.demandLevel),
              color: "#fff",
            }}
          >
            {d.semana}: {d.demandLevel}
          </span>
        ))}
      </div>

      {typeof data.summary === "string" && <div style={summaryBox}>{String(data.summary)}</div>}
    </div>
  );
}

function renderPricePredictions(data: Record<string, unknown>) {
  const predictions = data.predictions as Array<Record<string, unknown>>;
  if (!predictions || predictions.length === 0) return null;

  // Group by market
  const markets = new Map<string, Array<Record<string, unknown>>>();
  for (const p of predictions) {
    const mkt = String(p.market || p.mercado || "general");
    if (!markets.has(mkt)) markets.set(mkt, []);
    markets.get(mkt)!.push(p);
  }

  // If single market, simple line chart; multi-market, overlayed lines
  if (markets.size <= 1) {
    const chartData = predictions.map((p) => ({
      dia: `Dia ${p.day ?? p.dia ?? ""}`,
      Precio: Number(p.predicted_price_mxn ?? p.precio_predicho ?? 0),
    }));

    return (
      <div>
        <div style={sectionTitle}>Prediccion de Precios (MXN)</div>
        <div className="ai-chart-container">
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e8dff0" />
              <XAxis dataKey="dia" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v}`} />
              <Tooltip formatter={(v) => fmtMXN(v)} />
              <Line type="monotone" dataKey="Precio" stroke={COLORS.green} strokeWidth={2.5} dot={{ fill: COLORS.green, r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        {typeof data.summary === "string" && <div style={summaryBox}>{String(data.summary)}</div>}
      </div>
    );
  }

  // Multi-market: pivot data by day
  const days = [...new Set(predictions.map((p) => Number(p.day ?? p.dia ?? 0)))].sort((a, b) => a - b);
  const marketNames = [...markets.keys()];
  const pivoted = days.map((day) => {
    const row: Record<string, unknown> = { dia: `Dia ${day}` };
    for (const mkt of marketNames) {
      const match = markets.get(mkt)!.find((p) => Number(p.day ?? p.dia) === day);
      row[mkt] = match ? Number(match.predicted_price_mxn ?? match.precio_predicho ?? 0) : null;
    }
    return row;
  });

  return (
    <div>
      <div style={sectionTitle}>Prediccion de Precios por Mercado</div>
      <div className="ai-chart-container">
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={pivoted}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e8dff0" />
            <XAxis dataKey="dia" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v}`} />
            <Tooltip formatter={(v) => fmtMXN(v)} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {marketNames.map((mkt, i) => (
              <Line
                key={mkt}
                type="monotone"
                dataKey={mkt}
                stroke={CHART_COLORS[i % CHART_COLORS.length]}
                strokeWidth={2}
                dot={{ r: 3 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      {typeof data.summary === "string" && <div style={summaryBox}>{String(data.summary)}</div>}
    </div>
  );
}

function renderRoutes(data: Record<string, unknown>) {
  const routes = data.optimized_routes as Array<Record<string, unknown>>;
  if (!routes || routes.length === 0) return null;

  const savings = data.savings_vs_current_pct as number | undefined;

  return (
    <div>
      {typeof savings === "number" && (
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            background: "linear-gradient(135deg, #e8f5e9, #c8e6c9)",
            borderRadius: 10,
            padding: "10px 18px",
            marginBottom: 14,
            fontWeight: 600,
            color: COLORS.green,
            fontSize: "0.95rem",
          }}
        >
          Ahorro vs. actual: {savings}%
        </div>
      )}

      <div style={sectionTitle}>Rutas Optimizadas</div>
      <div style={cardGrid}>
        {routes.map((r, i) => (
          <div key={i} style={miniCard}>
            <div style={{ fontWeight: 700, fontSize: "0.95rem", color: COLORS.purple, marginBottom: 8 }}>
              {String(r.route_name || r.nombre_ruta || `Ruta ${i + 1}`)}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px 16px", fontSize: "0.82rem" }}>
              <div><span style={{ color: COLORS.gray }}>Distancia:</span></div>
              <div style={{ fontWeight: 600 }}>{Number(r.total_km || 0).toFixed(1)} km</div>
              <div><span style={{ color: COLORS.gray }}>Tiempo:</span></div>
              <div style={{ fontWeight: 600 }}>{Number(r.estimated_hours || r.horas_estimadas || 0).toFixed(1)} hrs</div>
              <div><span style={{ color: COLORS.gray }}>Combustible:</span></div>
              <div style={{ fontWeight: 600, color: COLORS.pink }}>{fmtMXN(r.fuel_cost_mxn ?? r.costo_combustible)}</div>
            </div>
            {typeof r.stops === "number" && (
              <div style={{ marginTop: 6, fontSize: "0.78rem", color: COLORS.gray }}>{r.stops} paradas</div>
            )}
          </div>
        ))}
      </div>
      {typeof data.summary === "string" && <div style={summaryBox}>{String(data.summary)}</div>}
    </div>
  );
}

function renderWaste(data: Record<string, unknown>) {
  const shipments = data.at_risk_shipments as Array<Record<string, unknown>>;
  const totalLoss = data.total_estimated_loss_mxn as number | undefined;

  // Build pie chart for risk distribution
  const riskBuckets: Record<string, number> = { "Bajo (<20%)": 0, "Medio (20-50%)": 0, "Alto (>50%)": 0 };
  if (shipments) {
    for (const s of shipments) {
      const pct = Number(s.spoilage_risk_pct ?? s.riesgo_pct ?? 0);
      if (pct > 50) riskBuckets["Alto (>50%)"]++;
      else if (pct >= 20) riskBuckets["Medio (20-50%)"]++;
      else riskBuckets["Bajo (<20%)"]++;
    }
  }
  const pieData = Object.entries(riskBuckets)
    .filter(([, v]) => v > 0)
    .map(([name, value]) => ({ name, value }));
  const pieColors = [COLORS.green, COLORS.orange, COLORS.red];

  return (
    <div>
      {typeof totalLoss === "number" && (
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            background: "linear-gradient(135deg, #fff5f5, #fee2e2)",
            borderRadius: 10,
            padding: "10px 18px",
            marginBottom: 14,
            fontWeight: 600,
            color: COLORS.red,
            fontSize: "0.95rem",
          }}
        >
          Perdida estimada total: {fmtMXN(totalLoss)}
        </div>
      )}

      {pieData.length > 0 && (
        <>
          <div style={sectionTitle}>Distribucion de Riesgo</div>
          <div className="ai-chart-container">
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={pieColors[i % pieColors.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </>
      )}

      {shipments && shipments.length > 0 && (
        <>
          <div style={sectionTitle}>Envios en Riesgo</div>
          <div style={{ overflowX: "auto" }}>
            <table style={tableStyle}>
              <thead>
                <tr>
                  <th style={thStyle}>Envio</th>
                  <th style={thStyle}>Riesgo</th>
                  <th style={thStyle}>Perdida Est.</th>
                </tr>
              </thead>
              <tbody>
                {shipments.map((s, i) => {
                  const riskPct = Number(s.spoilage_risk_pct ?? s.riesgo_pct ?? 0);
                  return (
                    <tr key={i}>
                      <td style={tdStyle}><strong>{String(s.shipment_id || s.envio_id || `#${i + 1}`)}</strong></td>
                      <td style={tdStyle}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <div
                            style={{
                              width: 60,
                              height: 8,
                              background: "#e8dff0",
                              borderRadius: 4,
                              overflow: "hidden",
                            }}
                          >
                            <div
                              style={{
                                width: `${Math.min(riskPct, 100)}%`,
                                height: "100%",
                                background: riskPct > 50 ? COLORS.red : riskPct >= 20 ? COLORS.orange : COLORS.green,
                                borderRadius: 4,
                              }}
                            />
                          </div>
                          <span style={{ fontSize: "0.8rem", fontWeight: 600 }}>{riskPct}%</span>
                        </div>
                      </td>
                      <td style={{ ...tdStyle, color: COLORS.red, fontWeight: 600 }}>
                        {fmtMXN(s.estimated_loss_mxn ?? s.perdida_estimada)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}
      {typeof data.summary === "string" && <div style={summaryBox}>{String(data.summary)}</div>}
    </div>
  );
}

function renderFrost(data: Record<string, unknown>) {
  const overallRisk = String(data.overall_risk || data.riesgo_general || "");
  const greenhouses = data.greenhouses_at_risk as Array<Record<string, unknown>>;

  return (
    <div>
      {overallRisk && (
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            borderRadius: 10,
            padding: "10px 18px",
            marginBottom: 14,
            fontWeight: 700,
            fontSize: "0.95rem",
            background: `${riskColor(overallRisk)}18`,
            color: riskColor(overallRisk),
            border: `2px solid ${riskColor(overallRisk)}`,
          }}
        >
          Riesgo general de helada: {overallRisk.toUpperCase()}
        </div>
      )}

      {greenhouses && greenhouses.length > 0 && (
        <>
          <div style={sectionTitle}>Invernaderos en Riesgo</div>
          <div style={cardGrid}>
            {greenhouses.map((g, i) => {
              const level = String(g.risk_level || g.nivel_riesgo || "low");
              const color = riskColor(level);
              const temp = g.min_temp_forecast_c ?? g.temp_min_pronostico;
              return (
                <div
                  key={i}
                  style={{
                    ...miniCard,
                    borderLeft: `4px solid ${color}`,
                    background: `${color}08`,
                  }}
                >
                  <div style={{ fontWeight: 700, fontSize: "0.95rem", marginBottom: 6 }}>
                    {String(g.name || g.nombre || `Invernadero ${i + 1}`)}
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ ...badge, background: color, color: "#fff" }}>
                      {level.toUpperCase()}
                    </span>
                    {temp != null && (
                      <span style={{ fontSize: "0.85rem", color: COLORS.gray }}>
                        Min: <strong style={{ color }}>{Number(temp).toFixed(1)}C</strong>
                      </span>
                    )}
                  </div>
                  {typeof g.recommendation === "string" && (
                    <div style={{ marginTop: 8, fontSize: "0.82rem", color: "#555", lineHeight: 1.5 }}>
                      {String(g.recommendation)}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}
      {typeof data.summary === "string" && <div style={summaryBox}>{String(data.summary)}</div>}
    </div>
  );
}

// ─── Fallback: render any JSON as a nice key-value table ─────

function renderKeyValue(data: Record<string, unknown>) {
  const entries = Object.entries(data).filter(
    ([, v]) => v != null && !(Array.isArray(v) && v.length === 0)
  );

  return (
    <div style={{ marginTop: 8 }}>
      {entries.map(([key, val]) => {
        // Render nested arrays as sub-tables
        if (Array.isArray(val) && val.length > 0 && typeof val[0] === "object") {
          const cols = Object.keys(val[0] as Record<string, unknown>);
          return (
            <div key={key} style={{ marginBottom: 16 }}>
              <div style={sectionTitle}>{formatKey(key)}</div>
              <div style={{ overflowX: "auto" }}>
                <table style={tableStyle}>
                  <thead>
                    <tr>
                      {cols.map((c) => (
                        <th key={c} style={thStyle}>{formatKey(c)}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(val as Array<Record<string, unknown>>).map((row, i) => (
                      <tr key={i}>
                        {cols.map((c) => (
                          <td key={c} style={tdStyle}>
                            {typeof row[c] === "number" ? row[c].toLocaleString("es-MX") : String(row[c] ?? "-")}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          );
        }

        // Render nested objects as mini cards
        if (typeof val === "object" && val !== null && !Array.isArray(val)) {
          return (
            <div key={key} style={{ marginBottom: 16 }}>
              <div style={sectionTitle}>{formatKey(key)}</div>
              <div style={miniCard}>
                {Object.entries(val as Record<string, unknown>).map(([k, v]) => (
                  <div key={k} style={{ display: "flex", gap: 8, marginBottom: 4, fontSize: "0.85rem" }}>
                    <span style={{ color: COLORS.gray, minWidth: 120 }}>{formatKey(k)}:</span>
                    <span style={{ fontWeight: 500 }}>{typeof v === "number" ? v.toLocaleString("es-MX") : String(v ?? "-")}</span>
                  </div>
                ))}
              </div>
            </div>
          );
        }

        // Render simple values
        if (typeof val === "string" && val.length > 100) {
          return (
            <div key={key} style={{ marginBottom: 12 }}>
              <div style={sectionTitle}>{formatKey(key)}</div>
              <div style={summaryBox}>{val}</div>
            </div>
          );
        }

        return (
          <div key={key} style={{ display: "flex", gap: 8, marginBottom: 6, fontSize: "0.88rem" }}>
            <span style={{ color: COLORS.gray, minWidth: 140, fontWeight: 500 }}>{formatKey(key)}:</span>
            <span style={{ fontWeight: 600 }}>
              {typeof val === "number" ? val.toLocaleString("es-MX") : String(val ?? "-")}
            </span>
          </div>
        );
      })}
    </div>
  );
}

// Convert snake_case keys to readable labels
function formatKey(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase())
    .replace(/Mxn/g, "(MXN)")
    .replace(/Pct/g, "(%)");
}

// ─── Main component ──────────────────────────────────────────

export default function AIResultRenderer({ data }: Props) {
  if (!data || typeof data !== "object") return null;

  // Detect shape and dispatch to specialized renderer
  if (Array.isArray(data.recommendations) && (data.recommendations as unknown[]).length > 0) {
    return renderPricingRecommendations(data);
  }

  if (Array.isArray(data.forecast) && (data.forecast as unknown[]).length > 0) {
    return renderDemandForecast(data);
  }

  if (Array.isArray(data.predictions) && (data.predictions as unknown[]).length > 0) {
    return renderPricePredictions(data);
  }

  if (Array.isArray(data.optimized_routes) && (data.optimized_routes as unknown[]).length > 0) {
    return renderRoutes(data);
  }

  if (Array.isArray(data.at_risk_shipments)) {
    return renderWaste(data);
  }

  if (data.greenhouses_at_risk || data.overall_risk || data.riesgo_general) {
    return renderFrost(data);
  }

  // Fallback: structured key-value rendering
  return renderKeyValue(data);
}
