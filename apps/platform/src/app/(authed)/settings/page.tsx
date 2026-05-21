"use client";

import { Card } from "@umrabor/ui";

export default function SettingsPage() {
  return (
    <div>
      <div className="mb-4">
        <h1 className="font-display text-3xl">Настройки</h1>
        <p className="text-sm text-ink-soft">Роли, шаблоны уведомлений, параметры платформы</p>
      </div>
      <Card className="text-ink-soft">
        Раздел в разработке. Backend поддерживает шаблоны уведомлений (push/sms) и матрицу ролей —
        UI появится в следующей итерации.
      </Card>
    </div>
  );
}
