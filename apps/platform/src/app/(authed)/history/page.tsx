"use client";

import { useEffect, useState } from "react";
import { Badge, Card, formatDateTime } from "@umrabor/ui";
import type { AuditLogEntry, Paginated } from "@umrabor/shared";
import { api } from "@/lib/api";

export default function HistoryPage() {
  const [data, setData] = useState<Paginated<AuditLogEntry> | null>(null);
  useEffect(() => {
    api.get<Paginated<AuditLogEntry>>("/api/v1/audit/", { page_size: 100 }).then(setData);
  }, []);

  return (
    <div>
      <div className="mb-4">
        <h1 className="font-display text-3xl">История действий</h1>
        <p className="text-sm text-ink-soft">Аудит-лог · только действия сотрудников UMRABOR</p>
      </div>
      <Card className="space-y-2">
        {data?.items.map((r) => (
          <div key={r.id} className="flex items-start gap-3 border-b border-cream pb-2 last:border-0">
            <div className="w-32 shrink-0 text-xs text-ink-soft">{formatDateTime(r.created_at)}</div>
            <Badge tone={r.action === "approve" || r.action === "publish" ? "active" : "neutral"}>
              {r.action}
            </Badge>
            <div className="flex-1 text-sm">
              <div>
                <b>{r.actor_name ?? "—"}</b> · {r.object_kind}{" "}
                {r.object_label && <span className="text-ink-soft">· {r.object_label}</span>}
              </div>
              {r.description && (
                <div className="text-xs text-ink-soft">{r.description}</div>
              )}
            </div>
          </div>
        ))}
        {data && data.items.length === 0 && (
          <div className="text-ink-soft">Аудит-лог пока пуст.</div>
        )}
      </Card>
    </div>
  );
}
