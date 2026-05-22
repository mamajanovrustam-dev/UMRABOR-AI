"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { formatUzsCompact } from "@umrabor/ui";
import type { Package, Paginated } from "@umrabor/shared";
import { api } from "@/lib/api";

export default function CatalogPage() {
  const [items, setItems] = useState<Package[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getNoAuth<Paginated<Package>>("/api/v1/packages/public", { page_size: 50 })
      .then((d) => setItems(d.items))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="container-mx py-12">
      <h1 className="text-4xl font-extrabold">Умра пакетлари 2026</h1>
      <p className="mt-2 text-textmuted">{items.length} турдан мос келганини танланг</p>

      {loading ? (
        <div className="mt-8 text-textmuted">Юкланмоқда...</div>
      ) : (
        <div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {items.map((p) => (
            <Link
              key={p.id}
              href={`/packages/${p.slug}`}
              className="group overflow-hidden rounded-2xl border border-line bg-card transition hover:border-umGreen/40 hover:shadow-2xl"
            >
              <div
                className="h-44 bg-cover bg-center"
                style={{
                  backgroundImage: `url('${p.photos[0] ?? "https://images.pexels.com/photos/2675268/pexels-photo.jpeg"}')`,
                }}
              />
              <div className="p-4">
                <div className="flex items-center justify-between text-xs">
                  <span className="rounded-full bg-gold/20 px-2 py-0.5 font-bold uppercase tracking-wider text-gold">
                    от {formatUzsCompact(p.price_quad ?? p.price_trpl ?? p.price_dbl)}
                  </span>
                  <span className="text-textmuted">{p.duration_days} кун</span>
                </div>
                <h3 className="mt-2 font-bold">{p.name}</h3>
                <p className="mt-1 text-xs text-textmuted">{p.partner_brand}</p>
                <p className="mt-2 text-sm text-white/80">{p.route.join(" → ")}</p>
                <div className="mt-3 grid grid-cols-4 gap-1 text-center text-xs">
                  <div><div className="text-textmuted">SGL</div><div className="font-mono">{formatUzsCompact(p.price_sgl)}</div></div>
                  <div><div className="text-textmuted">DBL</div><div className="font-mono">{formatUzsCompact(p.price_dbl)}</div></div>
                  <div><div className="text-textmuted">TRPL</div><div className="font-mono">{formatUzsCompact(p.price_trpl)}</div></div>
                  <div><div className="text-textmuted">QUAD</div><div className="font-mono">{formatUzsCompact(p.price_quad)}</div></div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
