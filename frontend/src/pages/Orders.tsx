import { useEffect, useState } from "react";
import { getOrders } from "../services/api";
import type { BuyerOrder } from "../types";
import { useLang } from "../i18n/LangContext";

const statusBadge: Record<string, string> = {
  pending: "badge-yellow",
  matched: "badge-purple",
  confirmed: "badge-blue",
  shipped: "badge-orange",
  delivered: "badge-green",
};

const statusSteps = ["pending", "matched", "confirmed", "shipped", "delivered"];

const buyerTypeBadge: Record<string, string> = {
  wholesaler: "badge-purple",
  retailer: "badge-blue",
  event_planner: "badge-pink",
  exporter: "badge-teal",
  hotel_chain: "badge-orange",
};

export default function Orders() {
  const { t } = useLang();
  const [orders, setOrders] = useState<BuyerOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getOrders()
      .then(setOrders)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <div className="loading">
        <div className="spinner" />
        {t("orders.loading")}
      </div>
    );

  if (error) return <div className="error-box">{error}</div>;

  const pendingCount = orders.filter((o) => o.status === "pending").length;

  return (
    <>
      <div className="page-header">
        <h2>{t("orders.title")}</h2>
        <p>
          {t("orders.summary")
            .replace("{count}", String(orders.length))
            .replace("{pending}", String(pendingCount))}
        </p>
      </div>

      <div className="grid-3">
        {orders.map((o) => {
          const currentIdx = statusSteps.indexOf(o.status);
          return (
            <div key={o.id} className="order-card">
              <div className="order-header">
                <div>
                  <div style={{ fontWeight: 700, fontSize: "1rem" }}>
                    {o.buyer_name}
                  </div>
                  <span
                    className={`badge ${buyerTypeBadge[o.buyer_type] || "badge-gray"}`}
                    style={{ marginTop: 4 }}
                  >
                    {o.buyer_type.replace("_", " ")}
                  </span>
                </div>
                <span className={`badge ${statusBadge[o.status] || "badge-gray"}`}>
                  {o.status}
                </span>
              </div>
              <div className="order-detail">
                {t("orders.flowers")}: {o.flower_types_needed.join(", ")}
              </div>
              <div className="order-detail">
                {t("orders.stems")}: {o.stems_needed.toLocaleString()} | {t("orders.quality")}:{" "}
                {o.quality_required.replace("_", " ")}
              </div>
              <div className="order-detail">
                {t("orders.delivery")}: {o.delivery_date}
              </div>
              <div className="order-detail" style={{ fontWeight: 600 }}>
                {t("orders.price")}: ${o.price_offered_mxn.toLocaleString()} MXN
              </div>

              {/* Status flow */}
              <div className="status-flow">
                {statusSteps.map((step, i) => (
                  <div
                    key={step}
                    className={`status-step ${
                      i < currentIdx
                        ? "active"
                        : i === currentIdx
                        ? "current"
                        : ""
                    }`}
                    title={step}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}
