import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Flower2,
  Package,
  Truck,
  ShoppingCart,
  CheckCircle,
  Brain,
} from "lucide-react";
import type { ReactNode } from "react";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/greenhouses", label: "Greenhouses", icon: Flower2 },
  { to: "/batches", label: "Batches", icon: Package },
  { to: "/shipments", label: "Shipments", icon: Truck },
  { to: "/orders", label: "Orders", icon: ShoppingCart },
  { to: "/quality", label: "Quality", icon: CheckCircle },
  { to: "/analyze", label: "AI Analysis", icon: Brain },
];

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>FloraFlow</h1>
          <div className="subtitle">Estado de Mexico Floriculture</div>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) => (isActive ? "active" : "")}
            >
              <item.icon />
              <span>{item.label}</span>
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
