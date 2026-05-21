"use client";

import { useEffect, useState } from "react";
import { Card } from "@umrabor/ui";
import type { Hotel, Airline, Paginated } from "@umrabor/shared";
import { api } from "@/lib/api";

const tabs = [
  { key: "hotels", label: "🏨 Отели" },
  { key: "airlines", label: "✈️ Авиакомпании" },
  { key: "services", label: "🛡 Услуги" },
  { key: "gifts", label: "🎁 Подарки" },
] as const;

type TabKey = (typeof tabs)[number]["key"];

interface DictItem {
  id: string;
  name: string;
  description?: string | null;
}

export default function DirectoriesPage() {
  const [tab, setTab] = useState<TabKey>("hotels");
  const [hotels, setHotels] = useState<Hotel[]>([]);
  const [airlines, setAirlines] = useState<Airline[]>([]);
  const [services, setServices] = useState<DictItem[]>([]);
  const [gifts, setGifts] = useState<DictItem[]>([]);

  useEffect(() => {
    api.get<Paginated<Hotel>>("/api/v1/directories/hotels", { page_size: 100 })
      .then((d) => setHotels(d.items));
    api.get<Airline[]>("/api/v1/directories/airlines").then(setAirlines);
    api.get<DictItem[]>("/api/v1/directories/services").then(setServices);
    api.get<DictItem[]>("/api/v1/directories/gifts").then(setGifts);
  }, []);

  return (
    <div>
      <div className="mb-4">
        <h1 className="font-display text-3xl">Справочники</h1>
        <p className="text-sm text-ink-soft">
          Глобальные справочники · единые для всех партнёров
        </p>
      </div>

      <div className="mb-4 flex gap-2">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`rounded-md border px-3 py-1.5 text-sm ${
              tab === t.key
                ? "border-gold bg-gold-soft text-gold-dark"
                : "border-cream bg-white text-navy"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "hotels" && (
        <Card className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {hotels.map((h) => (
            <div key={h.id} className="rounded-md border border-cream p-3">
              <div className="font-semibold">{h.name}</div>
              <div className="text-xs text-ink-soft">
                {h.city} · {"★".repeat(h.stars)} · {h.distance_value} м
              </div>
            </div>
          ))}
        </Card>
      )}
      {tab === "airlines" && (
        <Card className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {airlines.map((a) => (
            <div key={a.id} className="flex items-center gap-3 rounded-md border border-cream p-3">
              <div
                className="grid h-10 w-10 place-items-center rounded font-bold text-white"
                style={{ backgroundColor: a.logo_color ?? "#444" }}
              >
                {a.iata}
              </div>
              <div className="text-sm">{a.name}</div>
            </div>
          ))}
        </Card>
      )}
      {tab === "services" && (
        <Card className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {services.map((s) => (
            <div key={s.id} className="rounded-md border border-cream p-3 text-sm">
              <b>{s.name}</b>
              {s.description && <div className="text-xs text-ink-soft">{s.description}</div>}
            </div>
          ))}
        </Card>
      )}
      {tab === "gifts" && (
        <Card className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {gifts.map((g) => (
            <div key={g.id} className="rounded-md border border-cream p-3 text-sm">
              <b>{g.name}</b>
              {g.description && <div className="text-xs text-ink-soft">{g.description}</div>}
            </div>
          ))}
        </Card>
      )}
    </div>
  );
}
