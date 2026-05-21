import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { formatUzsCompact } from "@umrabor/ui";
import type { Package, Paginated } from "@umrabor/shared";
import { api } from "../lib/api";

export function CatalogScreen() {
  const [items, setItems] = useState<Package[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getNoAuth<Paginated<Package>>("/api/v1/packages/public", { page_size: 50 })
      .then((d) => setItems(d.items))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="px-4 py-3">
      <h2 className="mb-3 text-lg font-extrabold">Умра пакетлари 2026</h2>
      {loading && <div className="text-textmuted">Юкланмоқда...</div>}
      <div className="space-y-3">
        {items.map((p) => (
          <Link
            key={p.id}
            to={`/package/${p.slug}`}
            className="block overflow-hidden rounded-2xl border border-line bg-card"
          >
            <div
              className="h-32 bg-cover bg-center"
              style={{
                backgroundImage: `url('${p.photos[0] ?? "https://images.pexels.com/photos/2675268/pexels-photo.jpeg?w=600"}')`,
              }}
            />
            <div className="p-3">
              <div className="flex items-center justify-between text-xs">
                <span className="rounded-full bg-gold/20 px-2 py-0.5 font-bold text-gold">
                  от {formatUzsCompact(p.price_quad ?? p.price_trpl ?? p.price_dbl)}
                </span>
                <span className="text-textmuted">{p.duration_days} кун</span>
              </div>
              <h3 className="mt-1 font-bold">{p.name}</h3>
              <p className="text-xs text-textmuted">{p.partner_brand}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
