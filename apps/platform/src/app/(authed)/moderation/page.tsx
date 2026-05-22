"use client";

import { useEffect, useState } from "react";
import { Badge, Button, Card, formatDateTime, formatUzsCompact } from "@umrabor/ui";
import type { Package, Paginated } from "@umrabor/shared";
import { api } from "@/lib/api";

export default function ModerationPage() {
  const [items, setItems] = useState<Package[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  function refresh() {
    api.get<Paginated<Package>>("/api/v1/packages/", { status_filter: "moderation", page_size: 50 })
      .then((d) => setItems(d.items))
      .catch((e) => setError(e.message));
  }

  useEffect(refresh, []);

  async function decide(id: string, decision: "approved" | "rejected" | "rework") {
    setBusy(id);
    try {
      await api.post(`/api/v1/packages/${id}/moderate`, { decision });
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
          <h1 className="font-display text-3xl">Модерация</h1>
          <p className="text-sm text-ink-soft">Пакеты, ожидающие проверки · SLA 1 день</p>
        </div>
        <Badge tone="danger">{items.length}</Badge>
      </div>

      {error && (
        <div className="mb-4 rounded bg-status-dangerBg p-3 text-sm text-status-danger">{error}</div>
      )}

      {items.length === 0 ? (
        <Card className="text-center text-ink-soft">Нет пакетов на модерации</Card>
      ) : (
        <div className="space-y-3">
          {items.map((p) => (
            <Card key={p.id}>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-[1fr_220px_auto]">
                <div>
                  <div className="mb-1 flex items-center gap-2">
                    <Badge tone="gold">📦 Пакет</Badge>
                    <Badge tone="info">{p.duration_days} кун</Badge>
                  </div>
                  <h3 className="font-display text-xl">{p.name}</h3>
                  <p className="text-sm text-ink-soft">
                    {p.route.join(" → ")} · {p.departures_count} вылетов
                  </p>
                  <p className="mt-1 text-xs text-ink-soft">
                    Партнёр: <b>{p.partner_brand}</b>
                  </p>
                </div>
                <div className="text-sm">
                  <div className="text-xs text-ink-soft">Отправлено</div>
                  <div>{p.submitted_at ? formatDateTime(p.submitted_at) : "—"}</div>
                  <div className="mt-2 text-xs text-ink-soft">DBL</div>
                  <div className="font-mono">{formatUzsCompact(p.price_dbl)}</div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="primary"
                    loading={busy === p.id}
                    onClick={() => decide(p.id, "approved")}
                  >
                    ✓ Одобрить
                  </Button>
                  <Button
                    variant="danger"
                    loading={busy === p.id}
                    onClick={() => decide(p.id, "rejected")}
                  >
                    ✕ Отклонить
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
