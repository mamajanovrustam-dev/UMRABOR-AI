"use client";

import { useEffect, useState } from "react";
import { Card, CardSub, CardTitle, formatUzsCompact } from "@umrabor/ui";
import { api } from "@/lib/api";

interface KpiPlatform {
  gmv_7d_uzs: number;
  active_partners: number;
  published_packages: number;
  total_packages: number;
  bookings_7d: number;
  confirm_rate_pct: number;
  payments_7d_uzs: number;
}

export default function DashboardPage() {
  const [kpi, setKpi] = useState<KpiPlatform | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<KpiPlatform>("/api/v1/dashboard/platform")
      .then(setKpi)
      .catch((e) => setError(e.message ?? "Ошибка"));
  }, []);

  return (
    <div>
      <div className="mb-4 flex items-end justify-between">
        <div>
          <h1 className="font-display text-3xl">Дашборд</h1>
          <p className="text-sm text-ink-soft">Обзор платформы UMRABOR · сегодня</p>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded bg-status-dangerBg p-3 text-sm text-status-danger">{error}</div>
      )}

      {!kpi ? (
        <div className="text-ink-soft">Загрузка...</div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardSub>GMV · 7 дней</CardSub>
            <CardTitle className="text-3xl">{formatUzsCompact(kpi.gmv_7d_uzs)}</CardTitle>
          </Card>
          <Card>
            <CardSub>Активные партнёры</CardSub>
            <CardTitle className="text-3xl">{kpi.active_partners}</CardTitle>
          </Card>
          <Card>
            <CardSub>Опубликовано пакетов</CardSub>
            <CardTitle className="text-3xl">
              {kpi.published_packages}{" "}
              <span className="text-base text-ink-soft">из {kpi.total_packages}</span>
            </CardTitle>
          </Card>
          <Card>
            <CardSub>Заявок · 7 дней</CardSub>
            <CardTitle className="text-3xl">{kpi.bookings_7d}</CardTitle>
          </Card>
          <Card>
            <CardSub>% Подтверждения</CardSub>
            <CardTitle className="text-3xl">{kpi.confirm_rate_pct}%</CardTitle>
          </Card>
          <Card>
            <CardSub>Платежи · 7 дней</CardSub>
            <CardTitle className="text-3xl">{formatUzsCompact(kpi.payments_7d_uzs)}</CardTitle>
          </Card>
        </div>
      )}
    </div>
  );
}
