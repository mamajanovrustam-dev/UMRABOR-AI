"use client";

import { useEffect, useState } from "react";
import { Badge, Card, formatDate } from "@umrabor/ui";
import type { Paginated, Partner } from "@umrabor/shared";
import { api } from "@/lib/api";

const statusTone = {
  active: "active",
  suspended: "danger",
  archived: "archived",
  pending: "warn",
} as const;

const statusLabel = {
  active: "Активен",
  suspended: "Приостановлен",
  archived: "Архив",
  pending: "Ожидает",
} as const;

export default function PartnersPage() {
  const [data, setData] = useState<Paginated<Partner> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<Paginated<Partner>>("/api/v1/partners/", { page_size: 100 })
      .then(setData)
      .catch((e) => setError(e.message ?? "Ошибка"));
  }, []);

  return (
    <div>
      <div className="mb-4 flex items-end justify-between">
        <div>
          <h1 className="font-display text-3xl">Партнёры</h1>
          <p className="text-sm text-ink-soft">Тур-операторы платформы UMRABOR</p>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded bg-status-dangerBg p-3 text-sm text-status-danger">{error}</div>
      )}

      <Card className="overflow-hidden p-0">
        <table className="w-full text-sm">
          <thead className="bg-cream text-xs uppercase tracking-wider text-ink-soft">
            <tr>
              <th className="table-cell text-left">Партнёр</th>
              <th className="table-cell text-left">Город</th>
              <th className="table-cell text-left">Лицензия</th>
              <th className="table-cell text-left">Статус</th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((p) => (
              <tr key={p.id} className="border-t border-cream hover:bg-gold-soft/40">
                <td className="table-cell">
                  <div className="font-semibold">{p.brand}</div>
                  <div className="text-xs text-ink-soft">
                    {p.legal_name} · ИНН {p.inn ?? "—"}
                  </div>
                </td>
                <td className="table-cell">{p.city}</td>
                <td className="table-cell">
                  {p.license_no ? `№ ${p.license_no}` : "—"}
                  {p.license_until && (
                    <div className="text-xs text-ink-soft">до {formatDate(p.license_until)}</div>
                  )}
                </td>
                <td className="table-cell">
                  <Badge tone={statusTone[p.status]}>{statusLabel[p.status]}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {data && (
          <div className="border-t border-cream bg-cream/40 px-4 py-2 text-xs text-ink-soft">
            Всего {data.total} партнёров
          </div>
        )}
      </Card>
    </div>
  );
}
