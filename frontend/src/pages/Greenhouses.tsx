import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getGreenhouses } from "../services/api";
import type { Greenhouse } from "../types";
import { useLang } from "../i18n/LangContext";

const techBadge: Record<string, string> = {
  basic: "badge-gray",
  intermediate: "badge-yellow",
  advanced: "badge-green",
};

export default function Greenhouses() {
  const { t } = useLang();
  const [rows, setRows] = useState<Greenhouse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    getGreenhouses()
      .then(setRows)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <div className="loading">
        <div className="spinner" />
        {t("greenhouses.loading")}
      </div>
    );

  if (error) return <div className="error-box">{error}</div>;

  return (
    <>
      <div className="page-header">
        <h2>{t("greenhouses.title")}</h2>
        <p>{t("greenhouses.subtitle")}</p>
      </div>
      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>{t("greenhouses.name")}</th>
                <th>{t("greenhouses.municipality")}</th>
                <th>{t("greenhouses.area")}</th>
                <th>{t("greenhouses.flowers")}</th>
                <th>{t("greenhouses.owner")}</th>
                <th>{t("greenhouses.tech")}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((g) => (
                <tr
                  key={g.id}
                  className="clickable"
                  onClick={() => navigate(`/greenhouses/${g.id}`)}
                >
                  <td style={{ fontWeight: 600 }}>{g.name}</td>
                  <td>{g.municipality.replace(/_/g, " ")}</td>
                  <td>{g.area_m2.toLocaleString()}</td>
                  <td>{g.flower_types.join(", ")}</td>
                  <td>{g.owner}</td>
                  <td>
                    <span className={`badge ${techBadge[g.tech_level] || "badge-gray"}`}>
                      {g.tech_level}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
