"use client";

import { Card } from "@umrabor/ui";

export default function TeamPage() {
  return (
    <div>
      <div className="mb-4">
        <h1 className="font-display text-3xl">Пользователи</h1>
        <p className="text-sm text-ink-soft">Сотрудники платформы UMRABOR — управление доступом</p>
      </div>
      <Card className="text-ink-soft">
        Управление сотрудниками UMRABOR появится в следующих итерациях.
        Сейчас используйте seed-данные:
        <ul className="mt-2 list-disc pl-5 text-sm">
          <li>yulia.m — Super-admin</li>
          <li>anvar.q, dilfuza.t, sherali.a — Админы</li>
        </ul>
      </Card>
    </div>
  );
}
