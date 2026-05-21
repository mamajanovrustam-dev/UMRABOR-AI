"use client";

import { useEffect, useState } from "react";
import { Card, CardSub, CardTitle, formatUzsCompact } from "@umrabor/ui";
import { api } from "@/lib/api";

interface KpiPartner {
  sales_today: number;
  sales_7d: number;
  revenue_7d_uzs: number;
  new_bookings: number;
  confirm_rate_pct: number;
  cancel_rate_pct: number;
}

export default function PartnerDashboardPage() {
  const [kpi, setKpi] = useState<KpiPartner | null>(null);
  useEffect(() => {
    api.get<KpiPartner>("/api/v1/dashboard/partner").then(setKpi);
  }, []);

  return (
    <div>
      <div className="mb-4">
        <h1 className="font-display text-3xl">Дашборд</h1>
        <p className="text-sm text-ink-soft">Операционная сводка</p>
      </div>

      {kpi ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardSub>Продажи сегодня</CardSub>
            <CardTitle className="text-3xl">{kpi.sales_today}</CardTitle>
          </Card>
          <Card>
            <CardSub>За 7 дней</CardSub>
            <CardTitle className="text-3xl">{kpi.sales_7d}</CardTitle>
          </Card>
          <Card>
            <CardSub>Доход 7 дней</CardSub>
            <CardTitle className="text-3xl">{formatUzsCompact(kpi.revenue_7d_uzs)}</CardTitle>
          </Card>
          <Card>
            <CardSub>Новые заявки</CardSub>
            <CardTitle className="text-3xl text-status-info">{kpi.new_bookings}</CardTitle>
          </Card>
          <Card>
            <CardSub>% Подтверждения</CardSub>
            <CardTitle className="text-3xl">{kpi.confirm_rate_pct}%</CardTitle>
          </Card>
          <Card>
            <CardSub>% Отмен</CardSub>
            <CardTitle className="text-3xl">{kpi.cancel_rate_pct}%</CardTitle>
          </Card>
        </div>
      ) : (
        <div className="text-ink-soft">Загрузка...</div>
      )}
    </div>
  );
}
