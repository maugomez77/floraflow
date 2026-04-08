import { useState, useRef } from "react";
import {
  Brain,
  TrendingUp,
  Sprout,
  Users,
  Camera,
  Bug,
  BarChart3,
  DollarSign,
  Snowflake,
  Tag,
  Truck,
  Trash2,
  Upload,
  Loader2,
} from "lucide-react";
import {
  analyzeMarket,
  optimizeHarvest,
  matchBuyers,
  gradeFlower,
  detectDisease,
  forecastDemand,
  predictPrices,
  assessFrost,
  dynamicPricing,
  optimizeRoutes,
  predictWaste,
} from "../services/api";
import { useLang } from "../i18n/LangContext";
import AIResultRenderer from "../components/AIResultRenderer";

type Tab = "general" | "vision" | "predictions" | "optimization";
type AnalysisType = "market" | "harvest" | "buyers";

const FLOWER_TYPES = [
  "Rosa", "Gerbera", "Crisantemo", "Clavel", "Lilium",
  "Gladiola", "Margarita", "Girasol", "Tulipan", "Orquidea",
];

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

// Extract text from various API response shapes
function extractText(data: Record<string, unknown>): string {
  return (data.report || data.plan || data.matches || data.result || data.analysis || data.recommendation || data.forecast || data.prediction || data.assessment || data.pricing || data.routes || data.waste || JSON.stringify(data, null, 2)) as string;
}

// Grade color mapping
function gradeColor(grade: string): string {
  const g = grade?.toUpperCase();
  if (g === "A" || g === "PREMIUM" || g === "EXCELLENT") return "#059669";
  if (g === "B" || g === "GOOD" || g === "STANDARD") return "#7b2d8e";
  if (g === "C" || g === "FAIR" || g === "ECONOMY") return "#d97706";
  return "#dc2626";
}

// Severity color mapping
function severityColor(severity: string): string {
  const s = severity?.toLowerCase();
  if (s === "low" || s === "healthy" || s === "none") return "#059669";
  if (s === "medium" || s === "moderate") return "#d97706";
  if (s === "high" || s === "severe") return "#dc2626";
  return "#7b2d8e";
}

export default function Analyze() {
  const { t } = useLang();
  const [activeTab, setActiveTab] = useState<Tab>("general");

  // General analysis state
  const [generalResult, setGeneralResult] = useState("");
  const [activeType, setActiveType] = useState<AnalysisType | null>(null);
  const [generalLoading, setGeneralLoading] = useState(false);
  const [generalError, setGeneralError] = useState("");

  // Vision state
  const [gradeFile, setGradeFile] = useState<File | null>(null);
  const [gradePreview, setGradePreview] = useState("");
  const [gradeFlowerType, setGradeFlowerType] = useState("Rosa");
  const [gradeResult, setGradeResult] = useState<Record<string, unknown> | null>(null);
  const [gradeLoading, setGradeLoading] = useState(false);
  const [diseaseFile, setDiseaseFile] = useState<File | null>(null);
  const [diseasePreview, setDiseasePreview] = useState("");
  const [diseaseResult, setDiseaseResult] = useState<Record<string, unknown> | null>(null);
  const [diseaseLoading, setDiseaseLoading] = useState(false);
  const gradeInputRef = useRef<HTMLInputElement>(null);
  const diseaseInputRef = useRef<HTMLInputElement>(null);

  // Predictive state
  const [demandFlower, setDemandFlower] = useState("Rosa");
  const [demandDays, setDemandDays] = useState(7);
  const [demandResult, setDemandResult] = useState<Record<string, unknown> | null>(null);
  const [demandLoading, setDemandLoading] = useState(false);
  const [priceFlower, setPriceFlower] = useState("Rosa");
  const [priceResult, setPriceResult] = useState<Record<string, unknown> | null>(null);
  const [priceLoading, setPriceLoading] = useState(false);
  const [frostResult, setFrostResult] = useState<Record<string, unknown> | null>(null);
  const [frostLoading, setFrostLoading] = useState(false);

  // Optimization state
  const [pricingResult, setPricingResult] = useState<Record<string, unknown> | null>(null);
  const [pricingLoading, setPricingLoading] = useState(false);
  const [routesResult, setRoutesResult] = useState<Record<string, unknown> | null>(null);
  const [routesLoading, setRoutesLoading] = useState(false);
  const [wasteResult, setWasteResult] = useState<Record<string, unknown> | null>(null);
  const [wasteLoading, setWasteLoading] = useState(false);

  const [error, setError] = useState("");

  // General analysis
  const runGeneral = async (type: AnalysisType) => {
    setGeneralLoading(true);
    setGeneralError("");
    setGeneralResult("");
    setActiveType(type);
    try {
      let data: Record<string, unknown>;
      switch (type) {
        case "market": data = await analyzeMarket(); break;
        case "harvest": data = await optimizeHarvest(); break;
        case "buyers": data = await matchBuyers(); break;
      }
      setGeneralResult(extractText(data));
    } catch (e: unknown) {
      setGeneralError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setGeneralLoading(false);
    }
  };

  // File handlers
  const handleFileSelect = (
    file: File | undefined,
    setFile: (f: File | null) => void,
    setPreview: (s: string) => void,
  ) => {
    if (!file) return;
    setFile(file);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(file);
  };

  // Vision handlers
  const runGrade = async () => {
    if (!gradeFile) return;
    setGradeLoading(true);
    setError("");
    setGradeResult(null);
    try {
      const data = await gradeFlower(gradeFile, gradeFlowerType);
      setGradeResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Grading failed");
    } finally {
      setGradeLoading(false);
    }
  };

  const runDisease = async () => {
    if (!diseaseFile) return;
    setDiseaseLoading(true);
    setError("");
    setDiseaseResult(null);
    try {
      const data = await detectDisease(diseaseFile);
      setDiseaseResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Detection failed");
    } finally {
      setDiseaseLoading(false);
    }
  };

  // Predictive handlers
  const runDemand = async () => {
    setDemandLoading(true);
    setError("");
    setDemandResult(null);
    try {
      setDemandResult(await forecastDemand(demandFlower, demandDays));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Forecast failed");
    } finally {
      setDemandLoading(false);
    }
  };

  const runPrices = async () => {
    setPriceLoading(true);
    setError("");
    setPriceResult(null);
    try {
      setPriceResult(await predictPrices(priceFlower));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Prediction failed");
    } finally {
      setPriceLoading(false);
    }
  };

  const runFrost = async () => {
    setFrostLoading(true);
    setError("");
    setFrostResult(null);
    try {
      setFrostResult(await assessFrost());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Assessment failed");
    } finally {
      setFrostLoading(false);
    }
  };

  // Optimization handlers
  const runPricing = async () => {
    setPricingLoading(true);
    setError("");
    setPricingResult(null);
    try {
      setPricingResult(await dynamicPricing());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Pricing failed");
    } finally {
      setPricingLoading(false);
    }
  };

  const runRoutes = async () => {
    setRoutesLoading(true);
    setError("");
    setRoutesResult(null);
    try {
      setRoutesResult(await optimizeRoutes());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Route optimization failed");
    } finally {
      setRoutesLoading(false);
    }
  };

  const runWaste = async () => {
    setWasteLoading(true);
    setError("");
    setWasteResult(null);
    try {
      setWasteResult(await predictWaste());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Waste prediction failed");
    } finally {
      setWasteLoading(false);
    }
  };

  // Render result data using the AIResultRenderer for structured data,
  // or markdown for text responses
  const renderResult = (data: Record<string, unknown> | null) => {
    if (!data) return null;
    // Check if the API returned structured JSON (has known array/object keys)
    const hasStructuredData = [
      "recommendations", "forecast", "predictions", "optimized_routes",
      "at_risk_shipments", "greenhouses_at_risk", "overall_risk",
    ].some((key) => data[key] != null);
    if (hasStructuredData) {
      return <AIResultRenderer data={data} />;
    }
    // Fall back to markdown text rendering
    const text = extractText(data);
    if (typeof text === "string" && text !== JSON.stringify(data, null, 2)) {
      return <div className="ai-result">{renderMarkdown(text)}</div>;
    }
    // Last resort: render as formatted key-value via AIResultRenderer
    return <AIResultRenderer data={data} />;
  };

  const tabs: { key: Tab; icon: React.ReactNode; label: string }[] = [
    { key: "general", icon: <Brain size={16} />, label: t("ai.tab.general") },
    { key: "vision", icon: <Camera size={16} />, label: t("ai.tab.vision") },
    { key: "predictions", icon: <BarChart3 size={16} />, label: t("ai.tab.predictions") },
    { key: "optimization", icon: <DollarSign size={16} />, label: t("ai.tab.optimization") },
  ];

  return (
    <>
      <div className="page-header">
        <h2>
          <Brain size={28} style={{ marginRight: 8, verticalAlign: "middle" }} />
          {t("analyze.title")}
        </h2>
        <p>{t("analyze.description")}</p>
      </div>

      {/* Tab Navigation */}
      <div className="ai-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            className={`ai-tab ${activeTab === tab.key ? "ai-tab-active" : ""}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {error && <div className="error-box" style={{ marginTop: 16 }}>{error}</div>}

      {/* TAB: General Analysis */}
      {activeTab === "general" && (
        <div className="ai-section">
          <div className="btn-group">
            <button
              className={`btn ${activeType === "market" ? "btn-primary" : "btn-outline"}`}
              onClick={() => runGeneral("market")}
              disabled={generalLoading}
            >
              <TrendingUp size={18} />
              {t("analyze.market")}
            </button>
            <button
              className={`btn ${activeType === "harvest" ? "btn-secondary" : "btn-outline"}`}
              onClick={() => runGeneral("harvest")}
              disabled={generalLoading}
            >
              <Sprout size={18} />
              {t("analyze.harvest")}
            </button>
            <button
              className={`btn ${activeType === "buyers" ? "btn-accent" : "btn-outline"}`}
              onClick={() => runGeneral("buyers")}
              disabled={generalLoading}
            >
              <Users size={18} />
              {t("analyze.buyers")}
            </button>
          </div>

          {generalLoading && (
            <div className="loading">
              <div className="spinner" />
              {t("analyze.running")}
            </div>
          )}

          {generalError && <div className="error-box">{generalError}</div>}

          {generalResult && (
            <div className="card ai-result-card" style={{ marginTop: 24 }}>
              <div className="card-header">
                <h3>
                  {activeType === "market" && t("analyze.marketResult")}
                  {activeType === "harvest" && t("analyze.harvestResult")}
                  {activeType === "buyers" && t("analyze.buyersResult")}
                </h3>
              </div>
              <div className="ai-result" style={{ padding: 24, lineHeight: 1.7, maxHeight: "70vh", overflowY: "auto" }}>
                {renderMarkdown(generalResult)}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB: Vision AI */}
      {activeTab === "vision" && (
        <div className="ai-section">
          <h3 className="ai-section-title">
            <Camera size={20} /> {t("ai.vision")}
          </h3>

          <div className="ai-feature-grid">
            {/* Quality Grading */}
            <div className="ai-feature-card ai-feature-card--purple">
              <div className="ai-feature-header">
                <Camera size={24} className="ai-feature-icon" />
                <div>
                  <h4>{t("ai.vision.grade")}</h4>
                  <p>{t("ai.vision.gradeDesc")}</p>
                </div>
              </div>

              <div className="ai-feature-controls">
                <select
                  className="ai-select"
                  value={gradeFlowerType}
                  onChange={(e) => setGradeFlowerType(e.target.value)}
                >
                  {FLOWER_TYPES.map((f) => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>

                <input
                  ref={gradeInputRef}
                  type="file"
                  accept="image/*"
                  style={{ display: "none" }}
                  onChange={(e) => handleFileSelect(e.target.files?.[0], setGradeFile, setGradePreview)}
                />
                <button
                  className="btn btn-outline btn-sm"
                  onClick={() => gradeInputRef.current?.click()}
                >
                  <Upload size={16} /> {t("ai.upload")}
                </button>

                {gradePreview && (
                  <div className="ai-image-preview">
                    <img src={gradePreview} alt="Preview" />
                  </div>
                )}

                <button
                  className="btn btn-primary btn-sm"
                  onClick={runGrade}
                  disabled={!gradeFile || gradeLoading}
                >
                  {gradeLoading ? <><Loader2 size={16} className="ai-spin" /> {t("ai.processing")}</> : <>{t("ai.run")}</>}
                </button>
              </div>

              {gradeResult && (
                <div className="ai-feature-result">
                  {typeof gradeResult.grade === "string" && (
                    <div className="ai-grade-badge" style={{ borderColor: gradeColor(gradeResult.grade), color: gradeColor(gradeResult.grade) }}>
                      {gradeResult.grade.toUpperCase()}
                    </div>
                  )}
                  {renderResult(gradeResult)}
                </div>
              )}
            </div>

            {/* Disease Detection */}
            <div className="ai-feature-card ai-feature-card--pink">
              <div className="ai-feature-header">
                <Bug size={24} className="ai-feature-icon" />
                <div>
                  <h4>{t("ai.vision.disease")}</h4>
                  <p>{t("ai.vision.diseaseDesc")}</p>
                </div>
              </div>

              <div className="ai-feature-controls">
                <input
                  ref={diseaseInputRef}
                  type="file"
                  accept="image/*"
                  style={{ display: "none" }}
                  onChange={(e) => handleFileSelect(e.target.files?.[0], setDiseaseFile, setDiseasePreview)}
                />
                <button
                  className="btn btn-outline btn-sm"
                  onClick={() => diseaseInputRef.current?.click()}
                >
                  <Upload size={16} /> {t("ai.upload")}
                </button>

                {diseasePreview && (
                  <div className="ai-image-preview">
                    <img src={diseasePreview} alt="Preview" />
                  </div>
                )}

                <button
                  className="btn btn-primary btn-sm"
                  onClick={runDisease}
                  disabled={!diseaseFile || diseaseLoading}
                >
                  {diseaseLoading ? <><Loader2 size={16} className="ai-spin" /> {t("ai.processing")}</> : <>{t("ai.run")}</>}
                </button>
              </div>

              {diseaseResult && (
                <div className="ai-feature-result">
                  {typeof diseaseResult.severity === "string" && (
                    <div className="ai-severity-badge" style={{ background: severityColor(diseaseResult.severity), color: "white" }}>
                      {diseaseResult.severity.toUpperCase()}
                    </div>
                  )}
                  {renderResult(diseaseResult)}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB: Predictions */}
      {activeTab === "predictions" && (
        <div className="ai-section">
          <h3 className="ai-section-title">
            <BarChart3 size={20} /> {t("ai.predictive")}
          </h3>

          <div className="ai-feature-grid ai-feature-grid--3">
            {/* Demand Forecast */}
            <div className="ai-feature-card ai-feature-card--purple">
              <div className="ai-feature-header">
                <BarChart3 size={24} className="ai-feature-icon" />
                <div>
                  <h4>{t("ai.predict.demand")}</h4>
                  <p>{t("ai.predict.demandDesc")}</p>
                </div>
              </div>

              <div className="ai-feature-controls">
                <select
                  className="ai-select"
                  value={demandFlower}
                  onChange={(e) => setDemandFlower(e.target.value)}
                >
                  {FLOWER_TYPES.map((f) => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>

                <div className="ai-input-row">
                  <label>{t("ai.days")}:</label>
                  <select
                    className="ai-select ai-select--sm"
                    value={demandDays}
                    onChange={(e) => setDemandDays(Number(e.target.value))}
                  >
                    {[7, 14, 30, 60, 90].map((d) => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>

                <button
                  className="btn btn-primary btn-sm"
                  onClick={runDemand}
                  disabled={demandLoading}
                >
                  {demandLoading ? <><Loader2 size={16} className="ai-spin" /> {t("ai.processing")}</> : <><BarChart3 size={16} /> {t("ai.run")}</>}
                </button>
              </div>

              {demandResult && (
                <div className="ai-feature-result">
                  {renderResult(demandResult)}
                </div>
              )}
            </div>

            {/* Price Prediction */}
            <div className="ai-feature-card ai-feature-card--green">
              <div className="ai-feature-header">
                <DollarSign size={24} className="ai-feature-icon" />
                <div>
                  <h4>{t("ai.predict.prices")}</h4>
                  <p>{t("ai.predict.pricesDesc")}</p>
                </div>
              </div>

              <div className="ai-feature-controls">
                <select
                  className="ai-select"
                  value={priceFlower}
                  onChange={(e) => setPriceFlower(e.target.value)}
                >
                  {FLOWER_TYPES.map((f) => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>

                <button
                  className="btn btn-primary btn-sm"
                  onClick={runPrices}
                  disabled={priceLoading}
                >
                  {priceLoading ? <><Loader2 size={16} className="ai-spin" /> {t("ai.processing")}</> : <><DollarSign size={16} /> {t("ai.run")}</>}
                </button>
              </div>

              {priceResult && (
                <div className="ai-feature-result">
                  {renderResult(priceResult)}
                </div>
              )}
            </div>

            {/* Frost Risk */}
            <div className="ai-feature-card ai-feature-card--blue">
              <div className="ai-feature-header">
                <Snowflake size={24} className="ai-feature-icon" />
                <div>
                  <h4>{t("ai.predict.frost")}</h4>
                  <p>{t("ai.predict.frostDesc")}</p>
                </div>
              </div>

              <div className="ai-feature-controls">
                <button
                  className="btn btn-primary btn-sm"
                  onClick={runFrost}
                  disabled={frostLoading}
                >
                  {frostLoading ? <><Loader2 size={16} className="ai-spin" /> {t("ai.processing")}</> : <><Snowflake size={16} /> {t("ai.run")}</>}
                </button>
              </div>

              {frostResult && (
                <div className="ai-feature-result">
                  {renderResult(frostResult)}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB: Optimization */}
      {activeTab === "optimization" && (
        <div className="ai-section">
          <h3 className="ai-section-title">
            <DollarSign size={20} /> {t("ai.optimization")}
          </h3>

          <div className="ai-feature-grid ai-feature-grid--3">
            {/* Dynamic Pricing */}
            <div className="ai-feature-card ai-feature-card--purple">
              <div className="ai-feature-header">
                <Tag size={24} className="ai-feature-icon" />
                <div>
                  <h4>{t("ai.opt.pricing")}</h4>
                  <p>{t("ai.opt.pricingDesc")}</p>
                </div>
              </div>

              <div className="ai-feature-controls">
                <button
                  className="btn btn-primary btn-sm"
                  onClick={runPricing}
                  disabled={pricingLoading}
                >
                  {pricingLoading ? <><Loader2 size={16} className="ai-spin" /> {t("ai.processing")}</> : <><Tag size={16} /> {t("ai.run")}</>}
                </button>
              </div>

              {pricingResult && (
                <div className="ai-feature-result">
                  {renderResult(pricingResult)}
                </div>
              )}
            </div>

            {/* Route Optimization */}
            <div className="ai-feature-card ai-feature-card--green">
              <div className="ai-feature-header">
                <Truck size={24} className="ai-feature-icon" />
                <div>
                  <h4>{t("ai.opt.routes")}</h4>
                  <p>{t("ai.opt.routesDesc")}</p>
                </div>
              </div>

              <div className="ai-feature-controls">
                <button
                  className="btn btn-primary btn-sm"
                  onClick={runRoutes}
                  disabled={routesLoading}
                >
                  {routesLoading ? <><Loader2 size={16} className="ai-spin" /> {t("ai.processing")}</> : <><Truck size={16} /> {t("ai.run")}</>}
                </button>
              </div>

              {routesResult && (
                <div className="ai-feature-result">
                  {renderResult(routesResult)}
                </div>
              )}
            </div>

            {/* Waste Prediction */}
            <div className="ai-feature-card ai-feature-card--pink">
              <div className="ai-feature-header">
                <Trash2 size={24} className="ai-feature-icon" />
                <div>
                  <h4>{t("ai.opt.waste")}</h4>
                  <p>{t("ai.opt.wasteDesc")}</p>
                </div>
              </div>

              <div className="ai-feature-controls">
                <button
                  className="btn btn-primary btn-sm"
                  onClick={runWaste}
                  disabled={wasteLoading}
                >
                  {wasteLoading ? <><Loader2 size={16} className="ai-spin" /> {t("ai.processing")}</> : <><Trash2 size={16} /> {t("ai.run")}</>}
                </button>
              </div>

              {wasteResult && (
                <div className="ai-feature-result">
                  {renderResult(wasteResult)}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
