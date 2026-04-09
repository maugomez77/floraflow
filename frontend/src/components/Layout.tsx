import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Flower2,
  Package,
  Truck,
  ShoppingCart,
  CheckCircle,
  Brain,
  ShoppingBag,
  Satellite,
} from "lucide-react";
import type { ReactNode } from "react";
import { useLang } from "../i18n/LangContext";

const navKeys = [
  { to: "/", key: "nav.dashboard", icon: LayoutDashboard },
  { to: "/greenhouses", key: "nav.greenhouses", icon: Flower2 },
  { to: "/batches", key: "nav.batches", icon: Package },
  { to: "/shipments", key: "nav.shipments", icon: Truck },
  { to: "/orders", key: "nav.orders", icon: ShoppingCart },
  { to: "/quality", key: "nav.quality", icon: CheckCircle },
  { to: "/analyze", key: "nav.analyze", icon: Brain },
  { to: "/marketplace", key: "nav.marketplace", icon: ShoppingBag },
  { to: "/satellite", key: "nav.satellite", icon: Satellite },
];

export default function Layout({ children }: { children: ReactNode }) {
  const { lang, setLang, t } = useLang();

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <h1>FloraFlow</h1>
            <div
              style={{
                display: "inline-flex",
                borderRadius: 20,
                overflow: "hidden",
                border: "1px solid rgba(255,255,255,0.3)",
                fontSize: "0.7rem",
                fontWeight: 600,
                letterSpacing: "0.5px",
              }}
            >
              <button
                onClick={() => setLang("es")}
                style={{
                  padding: "4px 10px",
                  border: "none",
                  cursor: "pointer",
                  background: lang === "es" ? "rgba(255,255,255,0.25)" : "transparent",
                  color: lang === "es" ? "#fff" : "rgba(255,255,255,0.6)",
                  fontWeight: lang === "es" ? 700 : 500,
                  transition: "all 0.2s",
                }}
              >
                ES
              </button>
              <button
                onClick={() => setLang("en")}
                style={{
                  padding: "4px 10px",
                  border: "none",
                  cursor: "pointer",
                  background: lang === "en" ? "rgba(255,255,255,0.25)" : "transparent",
                  color: lang === "en" ? "#fff" : "rgba(255,255,255,0.6)",
                  fontWeight: lang === "en" ? 700 : 500,
                  transition: "all 0.2s",
                }}
              >
                EN
              </button>
            </div>
          </div>
          <div className="subtitle">{t("app.subtitle")}</div>
        </div>
        <nav className="sidebar-nav">
          {navKeys.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) => (isActive ? "active" : "")}
            >
              <item.icon />
              <span>{t(item.key)}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          FloraFlow v0.1.0 — Villa Guerrero, Tenancingo, Coatepec Harinas
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
