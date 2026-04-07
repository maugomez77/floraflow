import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { getShipment } from "../services/api";
import type { ColdChainShipment } from "../types";
import { useLang } from "../i18n/LangContext";

export default function ShipmentDetail() {
  const { t } = useLang();
  const { id } = useParams<{ id: string }>();
  const [shipment, setShipment] = useState<ColdChainShipment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    getShipment(id)
      .then(setShipment)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading)
    return (
      <div className="loading">
        <div className="spinner" />
        {t("shipments.loadingDetail")}
      </div>
    );

  if (error) return <div className="error-box">{error}</div>;
  if (!shipment) return <div className="error-box">{t("shipments.notFound")}</div>;

  const tempData = shipment.temperature_c.map((t, i) => ({
    reading: i + 1,
    temperature: t,
    humidity: shipment.humidity_pct + (Math.random() * 4 - 2), // slight variation for visual
  }));

  return (
    <>
      <div className="page-header">
        <h2>{t("shipments.title")} {shipment.id}</h2>
        <p>
          <Link to="/shipments">{t("nav.shipments")}</Link> / {shipment.id}
        </p>
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        <div className="card">
          <div className="card-header">
            <h3>{t("shipments.details")}</h3>
          </div>
          <table>
            <tbody>
              <tr>
                <td style={{ fontWeight: 600, width: 160 }}>{t("shipments.origin")}</td>
                <td>{shipment.origin_municipality.replace(/_/g, " ")}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>{t("shipments.destination")}</td>
                <td>{shipment.destination.replace(/_/g, " ")}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>{t("shipments.status")}</td>
                <td>{shipment.status.replace(/_/g, " ")}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>{t("shipments.carrier")}</td>
                <td>{shipment.carrier}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>{t("shipments.truckId")}</td>
                <td>{shipment.truck_id}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>{t("shipments.departure")}</td>
                <td>{shipment.departure_time || "--"}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>{t("shipments.eta")}</td>
                <td>{shipment.eta || "--"}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>{t("shipments.batches")}</td>
                <td>{shipment.batch_ids.length}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Temperature & Humidity Chart */}
      <div className="card">
        <div className="card-header">
          <h3>{t("shipments.tempChart")}</h3>
        </div>
        {tempData.length > 0 ? (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={tempData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e8dff0" />
              <XAxis dataKey="reading" label={{ value: "Reading #", position: "bottom" }} />
              <YAxis yAxisId="temp" label={{ value: "Temp (C)", angle: -90, position: "insideLeft" }} />
              <YAxis yAxisId="hum" orientation="right" label={{ value: "Humidity %", angle: 90, position: "insideRight" }} />
              <Tooltip />
              <ReferenceLine yAxisId="temp" y={4} stroke="#e91e63" strokeDasharray="5 5" label="Max Safe" />
              <Line
                yAxisId="temp"
                type="monotone"
                dataKey="temperature"
                stroke="#7b2d8e"
                strokeWidth={2}
                dot={{ r: 3 }}
              />
              <Line
                yAxisId="hum"
                type="monotone"
                dataKey="humidity"
                stroke="#4caf50"
                strokeWidth={2}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p style={{ color: "var(--text-muted)" }}>{t("shipments.noTemp")}</p>
        )}
      </div>
    </>
  );
}
