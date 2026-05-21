"use client";

import { useEffect, useState } from "react";
import { Badge, Card, formatUzsCompact } from "@umrabor/ui";
import type { Package, PackageStatus, Paginated } from "@umrabor/shared";
import { api } from "@/lib/api";

const tones = { draft: "neutral", moderation: "warn", rework: "warn", published: "active", rejected: "danger", withdrawn: "archived" } as const;
const labels = { draft: "Черновик", moderation: "На модерации", rework: "На доработке", published: "Опубликован", rejected: "Отклонён", withdrawn: "Снят" } as const;

export default function PartnerPackagesPage() {
  const [items, setItems] = useState<Package[]>([]);
  useEffect(() => {
    api.get<Paginated<Package>>("/api/v1/packages/me", { page_size: 100 }).then((d) => setItems(d.items));
  }, []);
  return (
    <div>
      <div className="mb-4 flex items-end justify-between">
        <div>
          <h1 className="font-display text-3xl">Пакеты</h1>
          <p className="text-sm text-ink-soft">Каталог пакетов агентства</p>
        </div>
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {items.map((p) => (
          <Card key={p.id}>
            <div className="mb-2 flex items-center justify-between">
              <Badge tone={tones[p.status as PackageStatus]}>{labels[p.status as PackageStatus]}</Badge>
              <span className="text-xs text-ink-soft">{p.duration_days} кун</span>
            </div>
            <h3 className="font-display text-xl">{p.name}</h3>
            <p className="text-sm text-ink-soft">{p.route.join(" → ")}</p>
            <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
              <div>
                <div className="text-ink-soft">Вылетов</div>
                <div className="font-mono">{p.departures_count}</div>
              </div>
              <div>
                <div className="text-ink-soft">Продано</div>
                <div className="font-mono">{p.sold_total}</div>
              </div>
              <div>
                <div className="text-ink-soft">DBL</div>
                <div className="font-mono">{formatUzsCompact(p.price_dbl)}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
