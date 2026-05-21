"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { formatDate, formatUzsCompact } from "@umrabor/ui";
import type { Booking, BookingStatus, Paginated } from "@umrabor/shared";
import { api } from "@/lib/api";

const tones: Record<BookingStatus, string> = {
  new: "bg-blue-500/20 text-blue-300",
  processing: "bg-orange-500/20 text-orange-300",
  kabul: "bg-umGreen/20 text-umGreen",
  completed: "bg-white/10 text-white/60",
  cancelled: "bg-red-500/20 text-red-300",
};
const labels: Record<BookingStatus, string> = {
  new: "Янги",
  processing: "Жараёнда",
  kabul: "Қабул",
  completed: "Тугалланди",
  cancelled: "Бекор",
};

export default function OrdersPage() {
  const router = useRouter();
  const [items, setItems] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!api.accessToken) {
      router.replace("/login");
      return;
    }
    api
      .get<Paginated<Booking>>("/api/v1/bookings/me", { page_size: 50 })
      .then((d) => setItems(d.items))
      .catch(() => router.replace("/login"))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return <main className="container-mx py-12 text-textmuted">Юкланмоқда...</main>;

  return (
    <main className="container-mx py-12">
      <h1 className="text-3xl font-extrabold">Менинг буюртмаларим</h1>
      {items.length === 0 ? (
        <div className="mt-8 rounded-xl border border-line bg-card p-8 text-center text-textmuted">
          У вас пока нет заказов
        </div>
      ) : (
        <div className="mt-8 space-y-3">
          {items.map((b) => (
            <div key={b.id} className="rounded-xl border border-line bg-card p-5">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-mono text-xs text-textmuted">{b.code}</div>
                  <h3 className="mt-1 font-bold">{b.package_name}</h3>
                  <p className="text-xs text-textmuted">{b.partner_brand}</p>
                </div>
                <span className={`rounded px-2 py-1 text-xs font-bold ${tones[b.status]}`}>
                  {labels[b.status]}
                </span>
              </div>
              <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
                <div>
                  <div className="text-textmuted">Вылет</div>
                  <div>{formatDate(b.departure_date_out)} → {formatDate(b.departure_date_in)}</div>
                </div>
                <div>
                  <div className="text-textmuted">Источник</div>
                  <div className="uppercase">{b.source}</div>
                </div>
                <div className="text-right">
                  <div className="text-textmuted">Сумма</div>
                  <div className="font-mono font-bold">{formatUzsCompact(b.total_uzs)}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
