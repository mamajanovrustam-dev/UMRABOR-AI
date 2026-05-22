"use client";

import { useEffect, useState } from "react";
import { Card } from "@umrabor/ui";
import type { Partner } from "@umrabor/shared";
import { api } from "@/lib/api";

export default function ProfilePage() {
  const [p, setP] = useState<Partner | null>(null);
  useEffect(() => {
    api.get<Partner>("/api/v1/partners/me/profile").then(setP);
  }, []);
  if (!p) return <div className="text-ink-soft">Загрузка...</div>;
  return (
    <div>
      <div className="mb-4">
        <h1 className="font-display text-3xl">Профиль партнёра</h1>
        <p className="text-sm text-ink-soft">
          Карточка партнёра по данным платформы UMRABOR. Для изменений обращайтесь в поддержку.
        </p>
      </div>
      <Card className="grid grid-cols-2 gap-4 text-sm">
        <div><b>Юр. название:</b> {p.legal_name}</div>
        <div><b>Бренд:</b> {p.brand}</div>
        <div><b>Город:</b> {p.city}</div>
        <div><b>ИНН:</b> <span className="font-mono">{p.inn}</span></div>
        <div><b>Лицензия:</b> № {p.license_no}</div>
        <div><b>Действует до:</b> {p.license_until}</div>
        <div><b>Контакт:</b> {p.contact_phone}</div>
        <div><b>Email:</b> {p.contact_email}</div>
      </Card>
    </div>
  );
}
