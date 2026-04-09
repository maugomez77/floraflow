import { useEffect, useMemo, useState } from "react";
import { ShoppingBag, Clock, User, Gavel, X, Loader2 } from "lucide-react";
import { getAuctions, getAuction, placeBid, buyNow } from "../services/api";
import type { Auction, Bid } from "../types";
import { useLang } from "../i18n/LangContext";

type StatusFilter = "all" | "open" | "bidding" | "sold" | "expired";

const flowerEmoji = (type: string): string => {
  const t = (type || "").toLowerCase();
  if (t.includes("rosa") || t.includes("rose")) return "🌹";
  if (t.includes("girasol") || t.includes("sunflower")) return "🌻";
  if (t.includes("gerbera")) return "🌸";
  if (t.includes("tulipan") || t.includes("tulip")) return "🌷";
  if (t.includes("orquidea") || t.includes("orchid")) return "🌺";
  if (t.includes("margarita") || t.includes("daisy")) return "🌼";
  if (t.includes("clavel") || t.includes("carnation")) return "💐";
  if (t.includes("crisantemo") || t.includes("chrysanthemum")) return "🏵️";
  if (t.includes("lilium") || t.includes("lily")) return "⚜️";
  return "🌸";
};

const qualityBadgeClass: Record<string, string> = {
  export_premium: "badge-gold",
  first: "badge-green",
  second: "badge-yellow",
  third: "badge-gray",
};

const statusBadgeClass: Record<string, string> = {
  open: "badge-blue",
  bidding: "badge-orange",
  sold: "badge-green",
  expired: "badge-gray",
  cancelled: "badge-gray",
};

function fmtMXN(val: number): string {
  return val.toLocaleString("es-MX", {
    style: "currency",
    currency: "MXN",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function fmtDateMX(iso: string, lang: string): string {
  try {
    return new Date(iso).toLocaleString(lang === "es" ? "es-MX" : "en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

function timeRemaining(expiresAt: string, lang: string): string {
  const now = new Date().getTime();
  const end = new Date(expiresAt).getTime();
  const diff = end - now;
  if (diff <= 0) return lang === "es" ? "Expirada" : "Expired";
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
  const mins = Math.floor((diff / (1000 * 60)) % 60);
  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${mins}m`;
  return `${mins}m`;
}

export default function Marketplace() {
  const { t, lang } = useLang();
  const [auctions, setAuctions] = useState<Auction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<StatusFilter>("all");
  const [, setTick] = useState(0);

  // Modal state
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<{ auction: Auction; bids: Bid[] } | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState("");

  // Bid form state
  const [bidderName, setBidderName] = useState("");
  const [bidderType, setBidderType] = useState("wholesaler");
  const [bidAmount, setBidAmount] = useState<number | "">("");
  const [bidMessage, setBidMessage] = useState("");
  const [bidSubmitting, setBidSubmitting] = useState(false);
  const [bidFormError, setBidFormError] = useState("");

  // Countdown tick
  useEffect(() => {
    const id = setInterval(() => setTick((n) => n + 1), 30000);
    return () => clearInterval(id);
  }, []);

  const loadAuctions = () => {
    setLoading(true);
    getAuctions()
      .then(setAuctions)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAuctions();
  }, []);

  const filtered = useMemo(() => {
    if (filter === "all") return auctions;
    return auctions.filter((a) => a.status === filter);
  }, [auctions, filter]);

  const openDetail = async (id: string) => {
    setSelectedId(id);
    setDetailLoading(true);
    setDetailError("");
    setDetail(null);
    setBidFormError("");
    try {
      const data = await getAuction(id);
      setDetail(data);
      setBidAmount(data.auction.current_bid_mxn || data.auction.min_price_mxn);
    } catch (e: unknown) {
      setDetailError(e instanceof Error ? e.message : "Failed to load auction");
    } finally {
      setDetailLoading(false);
    }
  };

  const closeDetail = () => {
    setSelectedId(null);
    setDetail(null);
    setBidderName("");
    setBidAmount("");
    setBidMessage("");
    setBidFormError("");
  };

  const submitBid = async () => {
    if (!detail) return;
    if (!bidderName.trim()) {
      setBidFormError(lang === "es" ? "Nombre requerido" : "Name required");
      return;
    }
    if (typeof bidAmount !== "number" || bidAmount <= 0) {
      setBidFormError(lang === "es" ? "Monto inválido" : "Invalid amount");
      return;
    }
    setBidSubmitting(true);
    setBidFormError("");
    try {
      await placeBid(detail.auction.id, bidderName, bidderType, bidAmount, bidMessage);
      // Refresh detail + list
      const refreshed = await getAuction(detail.auction.id);
      setDetail(refreshed);
      loadAuctions();
      setBidMessage("");
    } catch (e: unknown) {
      setBidFormError(e instanceof Error ? e.message : "Bid failed");
    } finally {
      setBidSubmitting(false);
    }
  };

  const submitBuyNow = async () => {
    if (!detail) return;
    if (!bidderName.trim()) {
      setBidFormError(lang === "es" ? "Nombre requerido" : "Name required");
      return;
    }
    setBidSubmitting(true);
    setBidFormError("");
    try {
      await buyNow(detail.auction.id, bidderName);
      const refreshed = await getAuction(detail.auction.id);
      setDetail(refreshed);
      loadAuctions();
    } catch (e: unknown) {
      setBidFormError(e instanceof Error ? e.message : "Buy now failed");
    } finally {
      setBidSubmitting(false);
    }
  };

  if (loading)
    return (
      <div className="loading">
        <div className="spinner" />
        {t("common.loading")}
      </div>
    );

  if (error) return <div className="error-box">{error}</div>;

  const filterBtn = (key: StatusFilter, label: string) => (
    <button
      key={key}
      className={`btn btn-sm ${filter === key ? "btn-primary" : "btn-outline"}`}
      onClick={() => setFilter(key)}
    >
      {label}
    </button>
  );

  return (
    <>
      <div className="page-header">
        <h2>
          <ShoppingBag size={28} style={{ marginRight: 8, verticalAlign: "middle" }} />
          {t("marketplace.title")}
        </h2>
        <p>{t("marketplace.subtitle")}</p>
      </div>

      <div className="btn-group" style={{ marginBottom: 20, flexWrap: "wrap" }}>
        {filterBtn("all", t("marketplace.allAuctions"))}
        {filterBtn("open", t("marketplace.open"))}
        {filterBtn("bidding", t("marketplace.bidding"))}
        {filterBtn("sold", t("marketplace.sold"))}
        {filterBtn("expired", t("marketplace.expired"))}
      </div>

      {filtered.length === 0 ? (
        <div className="card" style={{ padding: 32, textAlign: "center", color: "#888" }}>
          {t("common.noData")}
        </div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
            gap: 16,
          }}
        >
          {filtered.map((a) => (
            <div
              key={a.id}
              className="card clickable"
              style={{ padding: 18, display: "flex", flexDirection: "column", gap: 10, cursor: "pointer" }}
              onClick={() => openDetail(a.id)}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontSize: "2rem", lineHeight: 1 }}>{flowerEmoji(a.flower_type)}</span>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: "1.05rem", color: "#222" }}>{a.flower_type}</div>
                    <div style={{ fontSize: "0.82rem", color: "#666" }}>{a.variety}</div>
                  </div>
                </div>
                <span className={`badge ${statusBadgeClass[a.status] || "badge-gray"}`}>
                  {t(`marketplace.${a.status}`) !== `marketplace.${a.status}`
                    ? t(`marketplace.${a.status}`)
                    : a.status}
                </span>
              </div>

              <div>
                <span className={`badge ${qualityBadgeClass[a.quality_grade] || "badge-gray"}`}>
                  {a.quality_grade.replace(/_/g, " ")}
                </span>
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", color: "#555" }}>
                <span>
                  <strong>{a.stems_count.toLocaleString("es-MX")}</strong> {t("marketplace.stems")}
                </span>
                <span>
                  {a.stem_length_cm} cm {t("marketplace.length")}
                </span>
              </div>

              <div
                style={{
                  background: "#faf5ff",
                  borderRadius: 8,
                  padding: "10px 12px",
                  display: "flex",
                  flexDirection: "column",
                  gap: 4,
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", color: "#666" }}>
                  <span>{t("marketplace.currentBid")}</span>
                  <strong style={{ color: "#7b2d8e", fontSize: "0.95rem" }}>
                    {fmtMXN(a.current_bid_mxn || a.min_price_mxn)}
                  </strong>
                </div>
                {a.buy_now_price_mxn > 0 && (
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", color: "#666" }}>
                    <span>{t("marketplace.buyNow")}</span>
                    <strong style={{ color: "#059669" }}>{fmtMXN(a.buy_now_price_mxn)}</strong>
                  </div>
                )}
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", color: "#888" }}>
                <span style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
                  <User size={12} /> {a.seller_name}
                </span>
                <span style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
                  <Clock size={12} /> {timeRemaining(a.expires_at, lang)}
                </span>
              </div>

              <button
                className="btn btn-primary btn-sm"
                onClick={(e) => {
                  e.stopPropagation();
                  openDetail(a.id);
                }}
              >
                <Gavel size={14} /> {t("marketplace.details")}
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {selectedId && (
        <div
          onClick={closeDetail}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(20, 10, 30, 0.55)",
            zIndex: 1000,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 16,
            backdropFilter: "blur(4px)",
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "#fff",
              borderRadius: 14,
              maxWidth: 720,
              width: "100%",
              maxHeight: "90vh",
              overflowY: "auto",
              boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
              position: "relative",
            }}
          >
            <button
              onClick={closeDetail}
              aria-label="Close"
              style={{
                position: "absolute",
                top: 12,
                right: 12,
                background: "rgba(0,0,0,0.06)",
                border: "none",
                borderRadius: "50%",
                width: 32,
                height: 32,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                zIndex: 2,
              }}
            >
              <X size={18} />
            </button>

            {detailLoading && (
              <div className="loading" style={{ padding: 40 }}>
                <div className="spinner" />
                {t("common.loading")}
              </div>
            )}
            {detailError && <div className="error-box" style={{ margin: 24 }}>{detailError}</div>}

            {detail && (
              <div style={{ padding: 24 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
                  <span style={{ fontSize: "2.5rem" }}>{flowerEmoji(detail.auction.flower_type)}</span>
                  <div>
                    <h2 style={{ margin: 0, fontSize: "1.4rem", color: "#2a1a3a" }}>
                      {detail.auction.flower_type} — {detail.auction.variety}
                    </h2>
                    <div style={{ fontSize: "0.82rem", color: "#777", marginTop: 2 }}>
                      <User size={12} style={{ verticalAlign: "middle" }} /> {detail.auction.seller_name}
                    </div>
                  </div>
                </div>

                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
                  <span className={`badge ${statusBadgeClass[detail.auction.status] || "badge-gray"}`}>
                    {detail.auction.status}
                  </span>
                  <span className={`badge ${qualityBadgeClass[detail.auction.quality_grade] || "badge-gray"}`}>
                    {detail.auction.quality_grade.replace(/_/g, " ")}
                  </span>
                  <span className="badge badge-purple">
                    <Clock size={10} style={{ verticalAlign: "middle", marginRight: 4 }} />
                    {timeRemaining(detail.auction.expires_at, lang)}
                  </span>
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
                    gap: 10,
                    marginBottom: 18,
                  }}
                >
                  <div style={miniStat}>
                    <div style={miniLabel}>{t("marketplace.stems")}</div>
                    <div style={miniValue}>{detail.auction.stems_count.toLocaleString("es-MX")}</div>
                  </div>
                  <div style={miniStat}>
                    <div style={miniLabel}>{t("marketplace.length")}</div>
                    <div style={miniValue}>{detail.auction.stem_length_cm} cm</div>
                  </div>
                  <div style={miniStat}>
                    <div style={miniLabel}>{t("marketplace.minPrice")}</div>
                    <div style={miniValue}>{fmtMXN(detail.auction.min_price_mxn)}</div>
                  </div>
                  <div style={miniStat}>
                    <div style={miniLabel}>{t("marketplace.currentBid")}</div>
                    <div style={{ ...miniValue, color: "#7b2d8e" }}>
                      {fmtMXN(detail.auction.current_bid_mxn || detail.auction.min_price_mxn)}
                    </div>
                  </div>
                  {detail.auction.buy_now_price_mxn > 0 && (
                    <div style={miniStat}>
                      <div style={miniLabel}>{t("marketplace.buyNow")}</div>
                      <div style={{ ...miniValue, color: "#059669" }}>
                        {fmtMXN(detail.auction.buy_now_price_mxn)}
                      </div>
                    </div>
                  )}
                  <div style={miniStat}>
                    <div style={miniLabel}>Color</div>
                    <div style={miniValue}>{detail.auction.color}</div>
                  </div>
                </div>

                {/* Bid History */}
                <div style={{ marginBottom: 18 }}>
                  <h3 style={sectionHeading}>{t("marketplace.bidHistory")}</h3>
                  {detail.bids.length === 0 ? (
                    <div style={{ fontSize: "0.85rem", color: "#999", padding: 8 }}>
                      {t("common.noData")}
                    </div>
                  ) : (
                    <div style={{ maxHeight: 180, overflowY: "auto", border: "1px solid #f0e8f5", borderRadius: 8 }}>
                      {detail.bids
                        .slice()
                        .sort((a, b) => b.amount_mxn - a.amount_mxn)
                        .map((b) => (
                          <div
                            key={b.id}
                            style={{
                              padding: "10px 14px",
                              borderBottom: "1px solid #f5eefa",
                              display: "flex",
                              justifyContent: "space-between",
                              alignItems: "center",
                              fontSize: "0.85rem",
                            }}
                          >
                            <div>
                              <strong>{b.bidder_name}</strong>
                              <span style={{ color: "#888", marginLeft: 6, fontSize: "0.78rem" }}>
                                ({b.bidder_type})
                              </span>
                              {b.message && (
                                <div style={{ color: "#777", fontSize: "0.78rem", marginTop: 2 }}>
                                  {b.message}
                                </div>
                              )}
                              <div style={{ fontSize: "0.72rem", color: "#aaa", marginTop: 2 }}>
                                {fmtDateMX(b.created_at, lang)}
                              </div>
                            </div>
                            <strong style={{ color: "#7b2d8e" }}>{fmtMXN(b.amount_mxn)}</strong>
                          </div>
                        ))}
                    </div>
                  )}
                </div>

                {/* Bid form */}
                {(detail.auction.status === "open" || detail.auction.status === "bidding") && (
                  <div style={{ borderTop: "1px solid #f0e8f5", paddingTop: 16 }}>
                    <h3 style={sectionHeading}>{t("marketplace.placeBid")}</h3>
                    {bidFormError && <div className="error-box" style={{ marginBottom: 10 }}>{bidFormError}</div>}
                    <div style={{ display: "grid", gap: 10 }}>
                      <input
                        type="text"
                        className="ai-select"
                        placeholder={t("marketplace.bidder")}
                        value={bidderName}
                        onChange={(e) => setBidderName(e.target.value)}
                        style={inputStyle}
                      />
                      <select
                        className="ai-select"
                        value={bidderType}
                        onChange={(e) => setBidderType(e.target.value)}
                        style={inputStyle}
                      >
                        <option value="wholesaler">Wholesaler</option>
                        <option value="retailer">Retailer</option>
                        <option value="exporter">Exporter</option>
                        <option value="florist">Florist</option>
                        <option value="hotel">Hotel</option>
                      </select>
                      <input
                        type="number"
                        placeholder={t("marketplace.bidAmount")}
                        value={bidAmount}
                        onChange={(e) => setBidAmount(e.target.value === "" ? "" : Number(e.target.value))}
                        style={inputStyle}
                      />
                      <textarea
                        placeholder={t("marketplace.bidMessage")}
                        value={bidMessage}
                        onChange={(e) => setBidMessage(e.target.value)}
                        rows={2}
                        style={{ ...inputStyle, resize: "vertical" }}
                      />
                      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                        <button
                          className="btn btn-primary"
                          onClick={submitBid}
                          disabled={bidSubmitting}
                          style={{ flex: 1 }}
                        >
                          {bidSubmitting ? <Loader2 size={16} className="ai-spin" /> : <Gavel size={16} />}
                          {t("marketplace.confirmBid")}
                        </button>
                        {detail.auction.buy_now_price_mxn > 0 && (
                          <button
                            className="btn btn-accent"
                            onClick={submitBuyNow}
                            disabled={bidSubmitting}
                            style={{ flex: 1 }}
                          >
                            {t("marketplace.buyNow")} · {fmtMXN(detail.auction.buy_now_price_mxn)}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

// Inline styles
const miniStat: React.CSSProperties = {
  background: "#faf5ff",
  borderRadius: 8,
  padding: "10px 12px",
  border: "1px solid #f0e8f5",
};

const miniLabel: React.CSSProperties = {
  fontSize: "0.7rem",
  color: "#888",
  textTransform: "uppercase",
  letterSpacing: "0.04em",
  marginBottom: 4,
};

const miniValue: React.CSSProperties = {
  fontSize: "1rem",
  fontWeight: 700,
  color: "#2a1a3a",
};

const sectionHeading: React.CSSProperties = {
  fontSize: "0.85rem",
  color: "#7b2d8e",
  textTransform: "uppercase",
  letterSpacing: "0.04em",
  marginBottom: 10,
  marginTop: 0,
};

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: 8,
  border: "1px solid #e0d5ea",
  fontSize: "0.9rem",
  fontFamily: "inherit",
  outline: "none",
  background: "#fff",
};
