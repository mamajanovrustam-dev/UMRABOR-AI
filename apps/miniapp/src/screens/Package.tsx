import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { formatDate, formatUzsCompact } from "@umrabor/ui";
import type { Package } from "@umrabor/shared";
import { api } from "../lib/api";

export function PackageScreen() {
  const { slug } = useParams<{ slug: string }>();
  const [pkg, setPkg] = useState<Package | null>(null);

  useEffect(() => {
    if (!slug) return;
    api.getNoAuth<Package>(`/api/v1/packages/public/${slug}`).then(setPkg);
  }, [slug]);

  if (!pkg) return <div className="p-4 text-textmuted">Юкланмоқда...</div>;

  return (
    <div>
      <div
        className="h-56 bg-cover bg-center"
        style={{
          backgroundImage: `url('${pkg.photos[0] ?? "https://images.pexels.com/photos/2675268/pexels-photo.jpeg?w=900"}')`,
        }}
      />
      <div className="px-4 py-4">
        <Link to="/catalog" className="text-sm text-textmuted">
          ← Каталог
        </Link>
        <h1 className="mt-2 text-xl font-extrabold">{pkg.name}</h1>
        <p className="text-sm text-textmuted">{pkg.partner_brand}</p>
        <p className="mt-3 text-sm text-white/85">{pkg.description}</p>

        <h3 className="mt-5 font-bold">🏨 Гостиницы</h3>
        <div className="mt-2 space-y-2">
          {pkg.hotels.map((h) => (
            <div
              key={h.id}
              className="flex items-center justify-between rounded-xl border border-line bg-card p-3 text-sm"
            >
              <div>
                <div className="font-semibold">
                  {h.hotel_name} {"★".repeat(h.hotel_stars)}
                </div>
                <div className="text-xs text-textmuted">{h.hotel_city}</div>
              </div>
              <div className="rounded bg-gold/15 px-2 py-1 text-xs font-bold text-gold">
                {h.nights} кун
              </div>
            </div>
          ))}
        </div>

        <h3 className="mt-5 font-bold">✈ Вылеты</h3>
        <div className="mt-2 space-y-2">
          {pkg.departures?.map((d) => (
            <div
              key={d.id}
              className="rounded-xl border border-line bg-card p-3 text-sm"
            >
              <div className="font-mono">
                {formatDate(d.date_out)} → {formatDate(d.date_in)}
              </div>
              <div className="text-xs text-textmuted">
                {d.flight_out} / {d.flight_in} · мест{" "}
                {d.capacity_total - d.sold_total}/{d.capacity_total}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Sticky CTA */}
      <div className="sticky bottom-0 z-30 border-t border-line bg-bg/95 p-3 backdrop-blur">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-[10px] uppercase text-textmuted">от</div>
            <div className="font-bold text-umGreen">
              {formatUzsCompact(pkg.price_quad ?? pkg.price_trpl ?? pkg.price_dbl)}
            </div>
          </div>
          <Link
            to="/login"
            className="rounded-xl bg-umGreen px-5 py-3 font-semibold text-white"
          >
            Кейин →
          </Link>
        </div>
      </div>
    </div>
  );
}
