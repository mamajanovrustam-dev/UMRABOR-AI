/** Простой className-merger без зависимостей (без clsx/tailwind-merge, чтобы избежать пакетного оверхеда)). */
export function cn(...inputs: Array<string | false | null | undefined>): string {
  return inputs.filter(Boolean).join(" ");
}

/** Форматирует UZS в красивый вид: 73 600 000 сум */
export function formatUzs(amount: number | null | undefined, withCurrency = true): string {
  if (amount == null) return "—";
  const formatted = amount.toLocaleString("ru-RU").replace(/,/g, " ");
  return withCurrency ? `${formatted} сум` : formatted;
}

/** Миллионы вида "73,6 млн" */
export function formatUzsCompact(amount: number | null | undefined): string {
  if (amount == null) return "—";
  if (amount >= 1_000_000_000) return `${(amount / 1_000_000_000).toFixed(2).replace(".", ",")} млрд`;
  if (amount >= 1_000_000) return `${(amount / 1_000_000).toFixed(1).replace(".", ",")} млн`;
  if (amount >= 1_000) return `${(amount / 1_000).toFixed(0)} тыс`;
  return amount.toString();
}

/** ISO-дата → "10.10.2026" */
export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("ru-RU");
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleString("ru-RU");
}

/** Инициалы из имени */
export function initials(name?: string | null): string {
  if (!name) return "??";
  const parts = name.trim().split(/\s+/);
  return ((parts[0]?.[0] ?? "") + (parts[1]?.[0] ?? "")).toUpperCase();
}
