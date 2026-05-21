"use client";

import { useEffect, useState } from "react";
import { Badge, Button, Card, formatUzsCompact } from "@umrabor/ui";
import type { Booking, BookingStatus, Paginated } from "@umrabor/shared";
import { api } from "@/lib/api";

const tones: Record<BookingStatus, "info" | "warn" | "active" | "danger" | "archived"> = {
  new: "info",
  processing: "warn",
  kabul: "active",
  completed: "archived",
  cancelled: "danger",
};
const labels: Record<BookingStatus, string> = {
  new: "Янги",
  processing: "Жараёнда",
  kabul: "Қабул",
  completed: "Тугалланди",
  cancelled: "Бекор",
};

export default function PartnerBookingsPage() {
  const [items, setItems] = useState<Booking[]>([]);
  const [filter, setFilter] = useState<BookingStatus | "all">("all");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function refresh() {
    const q: Record<string, string | number | undefined> = { page_size: 100 };
    if (filter !== "all") q.status_filter = filter;
    api.get<Paginated<Booking>>("/api/v1/bookings/partner", q)
      .then((d) => setItems(d.items))
      .catch((e) => setError(e.message));
  }

  useEffect(refresh, [filter]);

  async function confirm(id: string) {
    setBusy(id);
    try {
      await api.post(`/api/v1/bookings/partner/${id}/confirm`);
      refresh();
    } catch (e) {
      alert((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  async function reject(id: string) {
    if (!confirm) return;
    const comment = window.prompt("Причина отказа:");
    if (!comment) return;
    setBusy(id);
    try {
      await api.post(`/api/v1/bookings/partner/${id}/reject`, { comment });
      refresh();
    } catch (e) {
      alert((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  return (
    <div>
      <div className="mb-4 flex items-end justify-between">
        <div>
          <h1 className="font-display text-3xl">Заявки</h1>
          <p className="text-sm text-ink-soft">Lifecycle · Янги → Қабул → Тугалланди</p>
        </div>
      </div>

      <div className="mb-4 flex gap-2">
        {(["all", "new", "kabul", "completed", "cancelled"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`rounded-md border px-3 py-1.5 text-sm ${
              filter === f
                ? "border-gold bg-gold-soft text-gold-dark"
                : "border-cream bg-white text-navy"
            }`}
          >
            {f === "all" ? "Барчаси" : labels[f]}
          </button>
        ))}
      </div>

      {error && <div className="mb-4 rounded bg-status-dangerBg p-3 text-sm text-status-danger">{error}</div>}

      <Card className="overflow-hidden p-0">
        <table className="w-full text-sm">
          <thead className="bg-cream text-xs uppercase tracking-wider text-ink-soft">
            <tr>
              <th className="table-cell text-left">ID</th>
              <th className="table-cell text-left">Клиент</th>
              <th className="table-cell text-left">Пакет</th>
              <th className="table-cell text-left">Статус</th>
              <th className="table-cell text-right">Сумма</th>
              <th className="table-cell text-right">Действие</th>
            </tr>
          </thead>
          <tbody>
            {items.map((b) => (
              <tr key={b.id} className="border-t border-cream">
                <td className="table-cell font-mono">{b.code}</td>
                <td className="table-cell">
                  {b.customer_name ?? "—"}
                  <div className="text-xs text-ink-soft">{b.customer_phone}</div>
                </td>
                <td className="table-cell">{b.package_name}</td>
                <td className="table-cell">
                  <Badge tone={tones[b.status]}>{labels[b.status]}</Badge>
                </td>
                <td className="table-cell text-right font-mono">{formatUzsCompact(b.total_uzs)}</td>
                <td className="table-cell text-right">
                  {b.status === "new" && (
                    <div className="flex justify-end gap-2">
                      <Button size="sm" loading={busy === b.id} onClick={() => confirm(b.id)}>
                        ✓ Тасдиқлаш
                      </Button>
                      <Button
                        size="sm"
                        variant="danger"
                        loading={busy === b.id}
                        onClick={() => reject(b.id)}
                      >
                        ✕
                      </Button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {items.length === 0 && (
          <div className="bg-cream/40 p-6 text-center text-ink-soft">Нет заявок</div>
        )}
      </Card>
    </div>
  );
}
