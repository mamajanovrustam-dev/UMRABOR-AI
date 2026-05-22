import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { formatDate, formatUzsCompact } from "@umrabor/ui";
import type { Booking, BookingStatus, Paginated } from "@umrabor/shared";
import { api } from "../lib/api";

const tones: Record<BookingStatus, string> = {
  new: "bg-blue-500/20 text-blue-300",
  processing: "bg-orange-500/20 text-orange-300",
  kabul: "bg-umGreen/20 text-umGreen",
  completed: "bg-white/10 text-white/60",
  cancelled: "bg-red-500/20 text-red-300",
};
const labels: Record<BookingStatus, string> = {
  new: "Янги",
  processing: "Жараёнда",
  kabul: "Қабул",
  completed: "Тугалланди",
  cancelled: "Бекор",
};

export function OrdersScreen() {
  const navigate = useNavigate();
  const [items, setItems] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!api.accessToken) {
      navigate("/login");
      return;
    }
    api
      .get<Paginated<Booking>>("/api/v1/bookings/me", { page_size: 50 })
      .then((d) => setItems(d.items))
      .catch(() => navigate("/login"))
      .finally(() => setLoading(false));
  }, [navigate]);

  return (
    <div className="px-4 py-4">
      <h2 className="mb-3 text-lg font-extrabold">Буюртмалар</h2>
      {loading ? (
        <div className="text-textmuted">Юкланмоқда...</div>
      ) : items.length === 0 ? (
        <div className="rounded-xl border border-line bg-card p-6 text-center text-textmuted">
          Буюртмаларингиз йўқ
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((b) => (
            <div key={b.id} className="rounded-xl border border-line bg-card p-4">
              <div className="flex items-center justify-between">
                <div className="font-mono text-xs text-textmuted">{b.code}</div>
                <span className={`rounded px-2 py-1 text-[10px] font-bold ${tones[b.status]}`}>
                  {labels[b.status]}
                </span>
              </div>
              <h3 className="mt-1 text-sm font-bold">{b.package_name}</h3>
              <p className="text-xs text-textmuted">
                {formatDate(b.departure_date_out)} → {formatDate(b.departure_date_in)}
              </p>
              <div className="mt-2 font-mono text-sm font-bold text-umGreen">
                {formatUzsCompact(b.total_uzs)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
