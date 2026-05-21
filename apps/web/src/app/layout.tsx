import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "UMRABOR · Умра турлари бронлаш платформаси",
  description:
    "UMRABOR — Узбекистон зиёратчилари учун умра турларини бронлаш платформаси.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <header className="sticky top-0 z-50 border-b border-line bg-bg/90 backdrop-blur-md">
          <div className="container-mx flex h-14 items-center justify-between">
            <Link href="/" className="flex items-center gap-2">
              <div className="grid h-8 w-8 place-items-center rounded bg-umGreen font-bold text-white">U</div>
              <span className="font-bold tracking-widest">UMRABOR</span>
            </Link>
            <nav className="flex items-center gap-1 text-sm">
              <Link href="/catalog" className="rounded px-3 py-1.5 text-white/80 hover:bg-card-2 hover:text-white">Каталог</Link>
              <Link href="/orders" className="rounded px-3 py-1.5 text-white/80 hover:bg-card-2 hover:text-white">Заказы</Link>
              <Link href="/partners-landing" className="rounded px-3 py-1.5 text-white/80 hover:bg-card-2 hover:text-white">Партнёрам</Link>
              <Link href="/login" className="ml-2 rounded bg-umGreen px-4 py-1.5 font-semibold text-white hover:bg-umGreen-dark">Кириш</Link>
            </nav>
          </div>
        </header>
        {children}
        <footer className="mt-20 border-t border-line bg-bg-2 py-8 text-center text-sm text-textmuted">
          <div>© 2026 UMRABOR LLC · Тошкент</div>
          <div className="mt-1 text-xs">Лицензия № UMR-001</div>
        </footer>
      </body>
    </html>
  );
}
