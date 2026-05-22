"use client";

import { useEffect, useState } from "react";
import { Badge, Card, formatUzsCompact } from "@umrabor/ui";
import type { Package, PackageStatus, Paginated } from "@umrabor/shared";
import { api } from "@/lib/api";

const tones: Record<PackageStatus, "info" | "warn" | "active" | "danger" | "archived" | "neutral"> = {
  draft: "neutral",
  moderation: "warn",
  rework: "warn",
  published: "active",
  rejected: "danger",
  withdrawn: "archived",
};
const labels: Record<PackageStatus, string> = {
  draft: "Черновик",
  moderation: "На модерации",
  rework: "На доработке",
  published: "Опубликовано",
  rejected: "Отклонён",
  withdrawn: "Снят",
};

export default function PackagesPage() {
  const [data, setData] = useState<Paginated<Package> | null>(null);
  useEffect(() => {
    api.get<Paginated<Package>>("/api/v1/packages/", { page_size: 100 }).then(setData);
  }, []);
  return (
    <div>
      <div className="mb-4">
        <h1 className="font-display text-3xl">Пакеты</h1>
        <p className="text-sm text-ink-soft">Каталог всех пакетов всех партнёров</p>
      </div>
      <Card className="overflow-hidden p-0">
        <table className="w-full text-sm">
          <thead className="bg-cream text-xs uppercase tracking-wider text-ink-soft">
            <tr>
              <th className="table-cell text-left">Пакет</th>
              <th className="table-cell text-left">Партнёр</th>
              <th className="table-cell text-right">Вылетов</th>
              <th className="table-cell text-right">Продано</th>
              <th className="table-cell text-right">DBL</th>
              <th className="table-cell text-left">Статус</th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((p) => (
              <tr key={p.id} className="border-t border-cream hover:bg-gold-soft/40">
                <td className="table-cell">
                  <div className="font-semibold">{p.name}</div>
                  <div className="text-xs text-ink-soft">{p.route.join(" → ")}</div>
                </td>
                <td className="table-cell">{p.partner_brand}</td>
                <td className="table-cell text-right">{p.departures_count}</td>
                <td className="table-cell text-right">{p.sold_total}</td>
                <td className="table-cell text-right font-mono">{formatUzsCompact(p.price_dbl)}</td>
                <td className="table-cell">
                  <Badge tone={tones[p.status]}>{labels[p.status]}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
