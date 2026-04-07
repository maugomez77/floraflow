import { useEffect, useState } from "react";
import { getBatches } from "../services/api";
import type { FlowerBatch } from "../types";
import { useLang } from "../i18n/LangContext";

const gradeBadge: Record<string, string> = {
  export_premium: "badge-gold",
  first: "badge-green",
  second: "badge-yellow",
  third: "badge-gray",
};

export default function Batches() {
  const { t } = useLang();
  const [rows, setRows] = useState<FlowerBatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getBatches()
      .then(setRows)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <div className="loading">
        <div className="spinner" />
        {t("batches.loading")}
      </div>
    );

  if (error) return <div className="error-box">{error}</div>;

  const totalStems = rows.reduce((s, b) => s + b.stems_count, 0);
  const totalValue = rows.reduce((s, b) => s + b.estimated_value_mxn, 0);

  return (
    <>
      <div className="page-header">
        <h2>{t("batches.title")}</h2>
        <p>
          {t("batches.summary")
            .replace("{count}", String(rows.length))
            .replace("{stems}", totalStems.toLocaleString())
            .replace("{value}", totalValue.toLocaleString())}
        </p>
      </div>

      <div className="card">
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
                <th>{t("batches.harvest")}</th>
                <th>{t("batches.shelf")}</th>
                <th>{t("batches.value")}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((b) => (
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
                  <td>{b.harvest_date}</td>
                  <td>{b.shelf_life_days} {t("common.days")}</td>
                  <td>${b.estimated_value_mxn.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
