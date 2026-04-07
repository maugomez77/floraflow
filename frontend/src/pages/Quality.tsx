import { useEffect, useState } from "react";
import { getQuality } from "../services/api";
import type { QualityAssessment } from "../types";
import { useLang } from "../i18n/LangContext";

const gradeBadge: Record<string, string> = {
  export_premium: "badge-gold",
  first: "badge-green",
  second: "badge-yellow",
  third: "badge-gray",
};

export default function Quality() {
  const { t } = useLang();
  const [rows, setRows] = useState<QualityAssessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getQuality()
      .then(setRows)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <div className="loading">
        <div className="spinner" />
        {t("quality.loading")}
      </div>
    );

  if (error) return <div className="error-box">{error}</div>;

  return (
    <>
      <div className="page-header">
        <h2>{t("quality.title")}</h2>
        <p>{t("quality.subtitle")}</p>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>{t("quality.batch")}</th>
                <th>{t("quality.inspector")}</th>
                <th>{t("quality.straightness")}</th>
                <th>{t("quality.petals")}</th>
                <th>{t("quality.colorIntensity")}</th>
                <th>{t("quality.blemish")}</th>
                <th>{t("quality.vaseLife")}</th>
                <th>{t("quality.grade")}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((q) => (
                <tr key={q.id}>
                  <td style={{ fontFamily: "monospace", fontSize: "0.8rem" }}>
                    {q.batch_id}
                  </td>
                  <td>{q.inspector}</td>
                  <td>
                    <span
                      style={{
                        color: q.stem_straightness >= 8 ? "#4caf50" : q.stem_straightness >= 5 ? "#ff9800" : "#ef4444",
                        fontWeight: 600,
                      }}
                    >
                      {q.stem_straightness}/10
                    </span>
                  </td>
                  <td>{q.petal_count}</td>
                  <td>
                    <span
                      style={{
                        color: q.color_intensity >= 8 ? "#4caf50" : q.color_intensity >= 5 ? "#ff9800" : "#ef4444",
                        fontWeight: 600,
                      }}
                    >
                      {q.color_intensity}/10
                    </span>
                  </td>
                  <td>
                    <span
                      style={{
                        color: q.blemish_pct <= 3 ? "#4caf50" : q.blemish_pct <= 8 ? "#ff9800" : "#ef4444",
                        fontWeight: 600,
                      }}
                    >
                      {q.blemish_pct.toFixed(1)}%
                    </span>
                  </td>
                  <td>{q.vase_life_estimate_days}</td>
                  <td>
                    <span
                      className={`badge ${gradeBadge[q.grade_recommendation] || "badge-gray"}`}
                    >
                      {q.grade_recommendation.replace("_", " ")}
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
