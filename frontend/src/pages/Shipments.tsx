import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getShipments } from "../services/api";
import type { ColdChainShipment } from "../types";
import { useLang } from "../i18n/LangContext";

const statusBadge: Record<string, string> = {
  harvesting: "badge-yellow",
  cooling: "badge-blue",
  loading: "badge-purple",
  in_transit: "badge-orange",
  at_market: "badge-teal",
  delivered: "badge-green",
};

export default function Shipments() {
  const { t } = useLang();
  const [rows, setRows] = useState<ColdChainShipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    getShipments()
      .then(setRows)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <div className="loading">
        <div className="spinner" />
        {t("shipments.loading")}
      </div>
    );

  if (error) return <div className="error-box">{error}</div>;

  return (
    <>
      <div className="page-header">
        <h2>{t("shipments.title")}</h2>
        <p>{t("shipments.subtitle")}</p>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>{t("shipments.origin")}</th>
                <th>{t("shipments.destination")}</th>
                <th>{t("shipments.status")}</th>
                <th>{t("shipments.carrier")}</th>
                <th>{t("shipments.truck")}</th>
                <th>{t("shipments.temp")}</th>
                <th>{t("shipments.humidity")}</th>
                <th>{t("shipments.eta")}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((s) => {
                const lastTemp =
                  s.temperature_c.length > 0
                    ? s.temperature_c[s.temperature_c.length - 1]
                    : null;
                return (
                  <tr
                    key={s.id}
                    className="clickable"
                    onClick={() => navigate(`/shipments/${s.id}`)}
                  >
                    <td>{s.origin_municipality.replace(/_/g, " ")}</td>
                    <td>{s.destination.replace(/_/g, " ")}</td>
                    <td>
                      <span
                        className={`badge ${statusBadge[s.status] || "badge-gray"}`}
                      >
                        {s.status.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td>{s.carrier}</td>
                    <td>{s.truck_id}</td>
                    <td>
                      {lastTemp !== null ? (
                        <span
                          style={{
                            color: lastTemp > 6 ? "#ef4444" : "#4caf50",
                            fontWeight: 600,
                          }}
                        >
                          {lastTemp.toFixed(1)}
                        </span>
                      ) : (
                        "--"
                      )}
                    </td>
                    <td>{s.humidity_pct}%</td>
                    <td>{s.eta || "--"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
