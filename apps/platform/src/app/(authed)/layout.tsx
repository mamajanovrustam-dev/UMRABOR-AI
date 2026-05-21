"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { UmraborUser } from "@umrabor/shared";
import { initials } from "@umrabor/ui";
import { api } from "@/lib/api";

const NAV = [
  { href: "/dashboard", icon: "📊", label: "Дашборд" },
  { href: "/partners", icon: "🏢", label: "Партнёры" },
  { href: "/moderation", icon: "🛡", label: "Модерация" },
  { href: "/packages", icon: "📦", label: "Пакеты" },
  { href: "/bookings", icon: "📋", label: "Заявки" },
  { href: "/payments", icon: "💰", label: "Платежи" },
  { href: "/team", icon: "🧑‍💼", label: "Пользователи" },
  { href: "/history", icon: "📜", label: "История" },
  { href: "/directories", icon: "📚", label: "Справочники" },
  { href: "/settings", icon: "⚙️", label: "Настройки" },
];

export default function AuthedLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<UmraborUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!api.accessToken) {
      router.replace("/login");
      return;
    }
    api
      .get<UmraborUser>("/api/v1/auth/umrabor/me")
      .then(setUser)
      .catch(() => router.replace("/login"))
      .finally(() => setLoading(false));
  }, [router]);

  function logout() {
    api.clearAuth();
    router.replace("/login");
  }

  if (loading) {
    return <div className="flex h-screen items-center justify-center">Загрузка...</div>;
  }
  if (!user) return null;

  return (
    <div className="flex min-h-screen bg-cream">
      <aside className="flex w-60 flex-col bg-navy text-white">
        <div className="px-5 py-5">
          <div className="font-display text-2xl tracking-wider">
            UMRA<span className="text-gold">BOR</span>
          </div>
          <div className="text-[10px] uppercase tracking-widest text-white/40">
            Платформа · v1
          </div>
        </div>
        <nav className="flex-1 space-y-1 px-2">
          {NAV.map((item) => {
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
          UMRABOR · Платформа v1
        </div>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex h-14 items-center justify-end gap-3 border-b border-cream bg-white px-6">
          <span className="text-xs text-ink-soft">{user.full_name}</span>
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
