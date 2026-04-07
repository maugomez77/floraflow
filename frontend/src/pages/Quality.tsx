import { useEffect, useState } from "react";
import { getQuality } from "../services/api";
import type { QualityAssessment } from "../types";

const gradeBadge: Record<string, string> = {
  export_premium: "badge-gold",
  first: "badge-green",
  second: "badge-yellow",
  third: "badge-gray",
};

export default function Quality() {
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
        Loading quality assessments...
      </div>
    );

  if (error) return <div className="error-box">{error}</div>;

  return (
    <>
      <div className="page-header">
        <h2>Quality Assessments</h2>
        <p>Flower quality grading and inspection results</p>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Batch</th>
                <th>Inspector</th>
                <th>Straightness</th>
                <th>Petals</th>
                <th>Color Intensity</th>
                <th>Blemish %</th>
                <th>Vase Life (days)</th>
                <th>Grade</th>
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
