"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { formatDate, formatUzsCompact } from "@umrabor/ui";
import type { Package } from "@umrabor/shared";
import { api } from "@/lib/api";

export default function PackageDetailPage() {
  const params = useParams<{ slug: string }>();
  const [pkg, setPkg] = useState<Package | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!params.slug) return;
    api
      .getNoAuth<Package>(`/api/v1/packages/public/${params.slug}`)
      .then(setPkg)
      .catch((e) => setError(e.message));
  }, [params.slug]);

  if (error) return <main className="container-mx py-12 text-red-400">{error}</main>;
  if (!pkg) return <main className="container-mx py-12 text-textmuted">Юкланмоқда...</main>;

  return (
    <main className="container-mx py-12">
      <div className="grid gap-8 lg:grid-cols-[1.4fr_1fr]">
        <div>
          <div
            className="aspect-video w-full rounded-2xl bg-cover bg-center"
            style={{
              backgroundImage: `url('${pkg.photos[0] ?? "https://images.pexels.com/photos/2675268/pexels-photo.jpeg"}')`,
            }}
          />
          <h1 className="mt-6 text-4xl font-extrabold">{pkg.name}</h1>
          <p className="mt-1 text-textmuted">{pkg.partner_brand}</p>
          <p className="mt-4 text-white/85">{pkg.description}</p>

          <h2 className="mt-8 text-xl font-bold">🏨 Гостиницы</h2>
          <div className="mt-3 space-y-2">
            {pkg.hotels.map((h) => (
              <div key={h.id} className="flex items-center justify-between rounded-xl border border-line bg-card p-4">
                <div>
                  <div className="font-semibold">
                    {h.hotel_name} {"★".repeat(h.hotel_stars)}
                  </div>
                  <div className="text-sm text-textmuted">{h.hotel_city}</div>
                </div>
                <div className="rounded bg-gold/15 px-3 py-1 text-sm font-bold text-gold">
                  {h.nights} кун
                </div>
              </div>
            ))}
          </div>

          <h2 className="mt-8 text-xl font-bold">✈ Вылеты</h2>
          <div className="mt-3 space-y-2">
            {pkg.departures?.map((d) => (
              <div key={d.id} className="rounded-xl border border-line bg-card p-4 text-sm">
                <div className="flex items-center justify-between">
                  <div>
                    <b>{formatDate(d.date_out)}</b> → {formatDate(d.date_in)}
                  </div>
                  <div className="text-textmuted">
                    {d.flight_out} / {d.flight_in}
                  </div>
                </div>
                <div className="mt-1 text-xs text-textmuted">
                  {d.aircraft} · {d.baggage} · мест:{" "}
                  {d.capacity_total - d.sold_total} из {d.capacity_total}
                </div>
              </div>
            ))}
          </div>
        </div>

        <aside className="space-y-3 lg:sticky lg:top-20 lg:self-start">
          <div className="rounded-2xl border border-umGreen/40 bg-umGreen/10 p-5">
            <div className="text-xs uppercase text-textmuted">1 кишидан</div>
            <div className="mt-1 text-4xl font-extrabold text-umGreen">
              {formatUzsCompact(pkg.price_quad ?? pkg.price_trpl ?? pkg.price_dbl)}
            </div>
            <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
              <div className="rounded-lg bg-card-2 p-3">
                <div className="text-textmuted">SGL</div>
                <div className="font-mono font-bold">{formatUzsCompact(pkg.price_sgl)}</div>
              </div>
              <div className="rounded-lg bg-card-2 p-3">
                <div className="text-textmuted">DBL</div>
                <div className="font-mono font-bold">{formatUzsCompact(pkg.price_dbl)}</div>
              </div>
              <div className="rounded-lg bg-card-2 p-3">
                <div className="text-textmuted">TRPL</div>
                <div className="font-mono font-bold">{formatUzsCompact(pkg.price_trpl)}</div>
              </div>
              <div className="rounded-lg bg-card-2 p-3">
                <div className="text-textmuted">QUAD</div>
                <div className="font-mono font-bold">{formatUzsCompact(pkg.price_quad)}</div>
              </div>
            </div>
            <button className="mt-5 w-full rounded-xl bg-umGreen py-3 font-semibold text-white hover:bg-umGreen-dark">
              Бронлаш →
            </button>
          </div>
        </aside>
      </div>
    </main>
  );
}
