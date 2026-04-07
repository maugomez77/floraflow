import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getGreenhouse, getBatches } from "../services/api";
import type { Greenhouse, FlowerBatch } from "../types";
import { useLang } from "../i18n/LangContext";

const gradeBadge: Record<string, string> = {
  export_premium: "badge-gold",
  first: "badge-green",
  second: "badge-yellow",
  third: "badge-gray",
};

export default function GreenhouseDetail() {
  const { t } = useLang();
  const { id } = useParams<{ id: string }>();
  const [gh, setGh] = useState<Greenhouse | null>(null);
  const [batches, setBatches] = useState<FlowerBatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    Promise.all([getGreenhouse(id), getBatches({ greenhouse_id: id })])
      .then(([g, b]) => {
        setGh(g);
        setBatches(b);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading)
    return (
      <div className="loading">
        <div className="spinner" />
        {t("greenhouses.loading")}
      </div>
    );

  if (error) return <div className="error-box">{error}</div>;
  if (!gh) return <div className="error-box">{t("greenhouses.notFound")}</div>;

  return (
    <>
      <div className="page-header">
        <h2>{gh.name}</h2>
        <p>
          <Link to="/greenhouses">{t("greenhouses.title")}</Link> / {gh.name}
        </p>
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        <div className="card">
          <div className="card-header">
            <h3>{t("greenhouses.detail")}</h3>
          </div>
          <table>
            <tbody>
              <tr>
                <td style={{ fontWeight: 600, width: 160 }}>{t("greenhouses.municipality")}</td>
                <td>{gh.municipality.replace(/_/g, " ")}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>{t("greenhouses.area")}</td>
                <td>{gh.area_m2.toLocaleString()} m2</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>{t("greenhouses.owner")}</td>
                <td>{gh.owner}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>{t("greenhouses.contact")}</td>
                <td>{gh.contact}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>{t("greenhouses.tech")}</td>
                <td>{gh.tech_level}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>{t("greenhouses.flowers")}</td>
                <td>{gh.flower_types.join(", ")}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>{t("greenhouses.coordinates")}</td>
                <td>
                  {gh.location_lat.toFixed(4)}, {gh.location_lng.toFixed(4)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>{t("nav.batches")} ({batches.length})</h3>
        </div>
        {batches.length === 0 ? (
          <p style={{ color: "var(--text-muted)" }}>{t("batches.noBatches")}</p>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>{t("batches.flower")}</th>
                  <th>{t("batches.variety")}</th>
                  <th>{t("batches.stems")}</th>
                  <th>{t("batches.grade")}</th>
                  <th>{t("batches.color")}</th>
                  <th>{t("batches.length")}</th>
                  <th>{t("batches.value")}</th>
                </tr>
              </thead>
              <tbody>
                {batches.map((b) => (
                  <tr key={b.id}>
                    <td style={{ fontWeight: 600 }}>{b.flower_type}</td>
                    <td>{b.variety}</td>
                    <td>{b.stems_count.toLocaleString()}</td>
                    <td>
                      <span
                        className={`badge ${gradeBadge[b.quality_grade] || "badge-gray"}`}
                      >
                        {b.quality_grade.replace("_", " ")}
                      </span>
                    </td>
                    <td>{b.color}</td>
                    <td>{b.stem_length_cm} cm</td>
                    <td>${b.estimated_value_mxn.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
