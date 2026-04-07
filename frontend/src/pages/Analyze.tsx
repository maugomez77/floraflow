import { useState } from "react";
import { Brain, TrendingUp, Sprout, Users } from "lucide-react";
import { analyzeMarket, optimizeHarvest, matchBuyers } from "../services/api";
import { useLang } from "../i18n/LangContext";

type AnalysisType = "market" | "harvest" | "buyers";

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
      let data: { result: string };
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
      setResult(data.result);
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
        <div className="card">
          <div className="card-header">
            <h3>
              {activeType === "market" && t("analyze.marketResult")}
              {activeType === "harvest" && t("analyze.harvestResult")}
              {activeType === "buyers" && t("analyze.buyersResult")}
            </h3>
          </div>
          <div className="ai-result">{result}</div>
        </div>
      )}
    </>
  );
}
