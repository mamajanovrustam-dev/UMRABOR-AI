"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { PartnerUser } from "@umrabor/shared";
import { initials } from "@umrabor/ui";
import { api } from "@/lib/api";

const NAV_ALL = [
  { href: "/dashboard", icon: "📊", label: "Дашборд", adminOnly: false },
  { href: "/profile", icon: "👤", label: "Профиль", adminOnly: true },
  { href: "/bookings", icon: "📋", label: "Заявки", adminOnly: false },
  { href: "/chat", icon: "💬", label: "Чат", adminOnly: false },
  { href: "/packages", icon: "📦", label: "Пакеты", adminOnly: false },
  { href: "/inventory", icon: "🏨", label: "Остатки", adminOnly: false },
  { href: "/pilgrims", icon: "👥", label: "Зиератчилар", adminOnly: false },
  { href: "/team", icon: "🧑‍💼", label: "Команда", adminOnly: true },
  { href: "/history", icon: "📜", label: "История", adminOnly: true },
  { href: "/settings", icon: "⚙️", label: "Настройки", adminOnly: true },
];

export default function PartnerAuthedLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<PartnerUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!api.accessToken) {
      router.replace("/login");
      return;
    }
    api
      .get<PartnerUser>("/api/v1/auth/partner/me")
      .then((u) => {
        if (u.must_change_password) router.replace("/change-password");
        else setUser(u);
      })
      .catch(() => router.replace("/login"))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return <div className="flex h-screen items-center justify-center">Загрузка...</div>;
  if (!user) return null;

  const isAdmin = user.role === "admin";
  const nav = NAV_ALL.filter((i) => !i.adminOnly || isAdmin);

  function logout() {
    api.clearAuth();
    router.replace("/login");
  }

  return (
    <div className="flex min-h-screen bg-cream">
      <aside className="flex w-60 flex-col bg-navy text-white">
        <div className="px-5 py-5">
          <div className="font-display text-2xl tracking-wider">
            UMRA<span className="text-gold">BOR</span>
          </div>
          <div className="text-[10px] uppercase tracking-widest text-white/40">
            Operator console · v5
          </div>
          <div className="mt-3 flex items-center gap-2 rounded-md bg-white/5 p-2">
            <div className="grid h-8 w-8 place-items-center rounded-full bg-gold text-navy text-xs font-bold">
              {initials(user.partner_brand)}
            </div>
            <div className="text-xs">
              <div className="font-semibold">{user.partner_brand}</div>
              <div className="text-white/40">Лицензия 002</div>
            </div>
          </div>
        </div>
        <nav className="flex-1 space-y-1 px-2">
          {nav.map((item) => {
            const active = pathname?.startsWith(item.href) ?? false;
            return (
              <Link key={item.href} href={item.href} className={`sb-link ${active ? "active" : ""}`}>
                <span className="text-base">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-white/10 px-5 py-3 text-[10px] uppercase tracking-widest text-white/40">
          UMRABOR · v5
        </div>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex h-14 items-center justify-end gap-3 border-b border-cream bg-white px-6">
          <span className="text-xs text-ink-soft">
            {user.full_name} · {user.role === "admin" ? "Админ" : "Оператор"}
          </span>
          <div className="grid h-9 w-9 place-items-center rounded-full bg-navy font-semibold text-gold">
            {initials(user.full_name)}
          </div>
          <button onClick={logout} className="text-xs text-ink-soft hover:text-status-danger">
            Выйти
          </button>
        </header>
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
