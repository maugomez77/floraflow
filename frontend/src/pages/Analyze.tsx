import { useState } from "react";
import { Brain, TrendingUp, Sprout, Users } from "lucide-react";
import { analyzeMarket, optimizeHarvest, matchBuyers } from "../services/api";
import { useLang } from "../i18n/LangContext";

type AnalysisType = "market" | "harvest" | "buyers";

// Simple markdown-to-HTML for rendering AI results
function renderMarkdown(md: string) {
  return md
    .split("\n")
    .map((line, i) => {
      if (line.startsWith("### ")) return <h4 key={i}>{line.slice(4)}</h4>;
      if (line.startsWith("## ")) return <h3 key={i}>{line.slice(3)}</h3>;
      if (line.startsWith("# ")) return <h2 key={i}>{line.slice(2)}</h2>;
      if (line.startsWith("---")) return <hr key={i} />;
      if (line.startsWith("- ") || line.startsWith("• "))
        return <li key={i} style={{ marginLeft: 16 }}>{line.slice(2)}</li>;
      if (line.startsWith("**") && line.endsWith("**"))
        return <p key={i}><strong>{line.slice(2, -2)}</strong></p>;
      if (line.trim() === "") return <br key={i} />;
      // Bold inline
      const parts = line.split(/(\*\*.*?\*\*)/g);
      return (
        <p key={i}>
          {parts.map((part, j) =>
            part.startsWith("**") && part.endsWith("**") ? (
              <strong key={j}>{part.slice(2, -2)}</strong>
            ) : (
              <span key={j}>{part}</span>
            )
          )}
        </p>
      );
    });
}

export default function Analyze() {
  const { t } = useLang();
  const [result, setResult] = useState("");
  const [activeType, setActiveType] = useState<AnalysisType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async (type: AnalysisType) => {
    setLoading(true);
    setError("");
    setResult("");
    setActiveType(type);
    try {
      let data: Record<string, unknown>;
      switch (type) {
        case "market":
          data = await analyzeMarket();
          break;
        case "harvest":
          data = await optimizeHarvest();
          break;
        case "buyers":
          data = await matchBuyers();
          break;
      }
      // API returns {report: ...}, {plan: ...}, or {matches: ...}
      const text = (data.report || data.plan || data.matches || data.result || JSON.stringify(data, null, 2)) as string;
      setResult(text);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Analysis failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="page-header">
        <h2>
          <Brain size={28} style={{ marginRight: 8, verticalAlign: "middle" }} />
          {t("analyze.title")}
        </h2>
        <p>{t("analyze.description")}</p>
      </div>

      <div className="btn-group">
        <button
          className={`btn ${activeType === "market" ? "btn-primary" : "btn-outline"}`}
          onClick={() => run("market")}
          disabled={loading}
        >
          <TrendingUp size={18} />
          {t("analyze.market")}
        </button>
        <button
          className={`btn ${activeType === "harvest" ? "btn-secondary" : "btn-outline"}`}
          onClick={() => run("harvest")}
          disabled={loading}
        >
          <Sprout size={18} />
          {t("analyze.harvest")}
        </button>
        <button
          className={`btn ${activeType === "buyers" ? "btn-accent" : "btn-outline"}`}
          onClick={() => run("buyers")}
          disabled={loading}
        >
          <Users size={18} />
          {t("analyze.buyers")}
        </button>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner" />
          {t("analyze.running")}
        </div>
      )}

      {error && <div className="error-box">{error}</div>}

      {result && (
        <div className="card" style={{ marginTop: 24 }}>
          <div className="card-header">
            <h3>
              {activeType === "market" && (t("analyze.marketResult") || "Reporte de Mercado")}
              {activeType === "harvest" && (t("analyze.harvestResult") || "Plan de Cosecha")}
              {activeType === "buyers" && (t("analyze.buyersResult") || "Matching de Compradores")}
            </h3>
          </div>
          <div className="ai-result" style={{ padding: 24, lineHeight: 1.7, maxHeight: "70vh", overflowY: "auto" }}>
            {renderMarkdown(result)}
          </div>
        </div>
      )}
    </>
  );
}
