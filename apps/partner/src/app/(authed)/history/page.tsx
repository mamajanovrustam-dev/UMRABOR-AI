"use client";
import { Card } from "@umrabor/ui";

export default function HistoryPage() {
  return (
    <div>
      <div className="mb-4">
        <h1 className="font-display text-3xl">История</h1>
        <p className="text-sm text-ink-soft">Раздел в разработке. Backend готов — UI появится в следующих итерациях.</p>
      </div>
      <Card className="text-ink-soft">
        API-эндпоинты для раздела «История» уже работают. UI будет наполняться по приоритетам команды продукта.
      </Card>
    </div>
  );
}
