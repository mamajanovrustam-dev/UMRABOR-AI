"use client";

import { useEffect, useState } from "react";
import { Card, formatDateTime, formatUzsCompact } from "@umrabor/ui";
import type { Paginated, Payment } from "@umrabor/shared";
import { api } from "@/lib/api";

export default function PaymentsPage() {
  const [data, setData] = useState<Paginated<Payment> | null>(null);
  useEffect(() => {
    api.get<Paginated<Payment>>("/api/v1/payments/", { page_size: 100 }).then(setData);
  }, []);
  return (
    <div>
      <div className="mb-4">
        <h1 className="font-display text-3xl">Платежи</h1>
        <p className="text-sm text-ink-soft">Лента транзакций Click · только просмотр</p>
      </div>
      <Card className="overflow-hidden p-0">
        <table className="w-full text-sm">
          <thead className="bg-cream text-xs uppercase tracking-wider text-ink-soft">
            <tr>
              <th className="table-cell text-left">ID транзакции</th>
              <th className="table-cell text-left">Дата</th>
              <th className="table-cell text-left">Клиент</th>
              <th className="table-cell text-left">Партнёр</th>
              <th className="table-cell text-left">ID заказа</th>
              <th className="table-cell text-right">Сумма</th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((p) => (
              <tr key={p.id} className="border-t border-cream hover:bg-gold-soft/40">
                <td className="table-cell font-mono">{p.code}</td>
                <td className="table-cell">{formatDateTime(p.paid_at || p.created_at)}</td>
                <td className="table-cell">
                  {p.customer_name ?? "—"}
                  <div className="font-mono text-xs text-ink-soft">{p.customer_phone}</div>
                </td>
                <td className="table-cell">{p.partner_brand}</td>
                <td className="table-cell font-mono">{p.booking_code}</td>
                <td className="table-cell text-right font-mono">
                  {formatUzsCompact(p.amount_uzs)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
