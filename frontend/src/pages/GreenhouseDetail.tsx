import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getGreenhouse, getBatches } from "../services/api";
import type { Greenhouse, FlowerBatch } from "../types";

const gradeBadge: Record<string, string> = {
  export_premium: "badge-gold",
  first: "badge-green",
  second: "badge-yellow",
  third: "badge-gray",
};

export default function GreenhouseDetail() {
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
        Loading greenhouse...
      </div>
    );

  if (error) return <div className="error-box">{error}</div>;
  if (!gh) return <div className="error-box">Greenhouse not found</div>;

  return (
    <>
      <div className="page-header">
        <h2>{gh.name}</h2>
        <p>
          <Link to="/greenhouses">Greenhouses</Link> / {gh.name}
        </p>
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        <div className="card">
          <div className="card-header">
            <h3>Details</h3>
          </div>
          <table>
            <tbody>
              <tr>
                <td style={{ fontWeight: 600, width: 160 }}>Municipality</td>
                <td>{gh.municipality.replace(/_/g, " ")}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Area</td>
                <td>{gh.area_m2.toLocaleString()} m2</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Owner</td>
                <td>{gh.owner}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Contact</td>
                <td>{gh.contact}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Tech Level</td>
                <td>{gh.tech_level}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Flower Types</td>
                <td>{gh.flower_types.join(", ")}</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Coordinates</td>
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
          <h3>Flower Batches ({batches.length})</h3>
        </div>
        {batches.length === 0 ? (
          <p style={{ color: "var(--text-muted)" }}>No batches for this greenhouse</p>
        ) : (
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
                  <th>Value (MXN)</th>
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
