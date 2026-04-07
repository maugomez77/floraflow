import { useEffect, useState } from "react";
import { getBatches } from "../services/api";
import type { FlowerBatch } from "../types";

const gradeBadge: Record<string, string> = {
  export_premium: "badge-gold",
  first: "badge-green",
  second: "badge-yellow",
  third: "badge-gray",
};

export default function Batches() {
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
        Loading flower batches...
      </div>
    );

  if (error) return <div className="error-box">{error}</div>;

  const totalStems = rows.reduce((s, b) => s + b.stems_count, 0);
  const totalValue = rows.reduce((s, b) => s + b.estimated_value_mxn, 0);

  return (
    <>
      <div className="page-header">
        <h2>Flower Batches</h2>
        <p>
          {rows.length} batches | {totalStems.toLocaleString()} stems | $
          {totalValue.toLocaleString()} MXN total value
        </p>
      </div>

      <div className="card">
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Flower</th>
                <th>Variety</th>
                <th>Stems</th>
                <th>Grade</th>
                <th>Color</th>
                <th>Stem Length</th>
                <th>Harvest Date</th>
                <th>Shelf Life</th>
                <th>Value (MXN)</th>
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
                  <td>{b.shelf_life_days} days</td>
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
