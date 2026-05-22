"use client";

import { useEffect, useState } from "react";
import { Badge, Card, formatUzsCompact } from "@umrabor/ui";
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

export default function BookingsPage() {
  const [data, setData] = useState<Paginated<Booking> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<Paginated<Booking>>("/api/v1/bookings/", { page_size: 100 })
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <div className="mb-4">
        <h1 className="font-display text-3xl">Заявки</h1>
        <p className="text-sm text-ink-soft">
          Все брони всех партнёров · read-only для аудита
        </p>
      </div>

      {error && <div className="mb-4 rounded bg-status-dangerBg p-3 text-sm text-status-danger">{error}</div>}

      <Card className="overflow-hidden p-0">
        <table className="w-full text-sm">
          <thead className="bg-cream text-xs uppercase tracking-wider text-ink-soft">
            <tr>
              <th className="table-cell text-left">ID</th>
              <th className="table-cell text-left">Партнёр</th>
              <th className="table-cell text-left">Пакет</th>
              <th className="table-cell text-left">Статус</th>
              <th className="table-cell text-right">Сумма</th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((b) => (
              <tr key={b.id} className="border-t border-cream hover:bg-gold-soft/40">
                <td className="table-cell font-mono">{b.code}</td>
                <td className="table-cell">{b.partner_brand}</td>
                <td className="table-cell">{b.package_name}</td>
                <td className="table-cell">
                  <Badge tone={tones[b.status]}>{labels[b.status]}</Badge>
                </td>
                <td className="table-cell text-right font-mono">
                  {formatUzsCompact(b.total_uzs)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {data && (
          <div className="border-t border-cream bg-cream/40 px-4 py-2 text-xs text-ink-soft">
            Показано {data.items.length} из {data.total}
          </div>
        )}
      </Card>
    </div>
  );
}
