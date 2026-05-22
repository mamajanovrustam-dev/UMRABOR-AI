import { Link, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { HomeScreen } from "./screens/Home";
import { CatalogScreen } from "./screens/Catalog";
import { PackageScreen } from "./screens/Package";
import { OrdersScreen } from "./screens/Orders";
import { ProfileScreen } from "./screens/Profile";
import { LoginScreen } from "./screens/Login";

const TABS = [
  { to: "/home", label: "Бош саҳифа", icon: "🏠" },
  { to: "/catalog", label: "Каталог", icon: "🗂" },
  { to: "/orders", label: "Буюртмалар", icon: "🛒" },
  { to: "/profile", label: "Профиль", icon: "👤" },
];

export function App() {
  const loc = useLocation();
  return (
    <div className="phone">
      {/* Notch */}
      <div className="absolute left-1/2 top-0 z-50 h-6 w-36 -translate-x-1/2 rounded-b-2xl bg-black" />
      {/* Status bar */}
      <div className="relative z-40 flex h-9 items-center justify-between px-7 pt-2 text-xs font-semibold">
        <span>9:41</span>
        <span>📶 📡 🔋</span>
      </div>

      <div className="scr-area">
        <Routes>
          <Route path="/" element={<Navigate to="/home" replace />} />
          <Route path="/home" element={<HomeScreen />} />
          <Route path="/catalog" element={<CatalogScreen />} />
          <Route path="/package/:slug" element={<PackageScreen />} />
          <Route path="/orders" element={<OrdersScreen />} />
          <Route path="/profile" element={<ProfileScreen />} />
          <Route path="/login" element={<LoginScreen />} />
        </Routes>
      </div>

      {/* Bottom navigation */}
      <nav className="absolute inset-x-0 bottom-0 z-40 flex h-16 items-center justify-around border-t border-line bg-[#0F1115]">
        {TABS.map((t) => {
          const active = loc.pathname.startsWith(t.to);
          return (
            <Link
              key={t.to}
              to={t.to}
              className={`flex flex-col items-center gap-1 text-[11px] font-medium ${
                active ? "text-umGreen" : "text-textmuted"
              }`}
            >
              <span className="text-lg">{t.icon}</span>
              {t.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
