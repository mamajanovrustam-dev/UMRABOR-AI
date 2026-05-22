import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "UMRABOR · Партнёр",
  description: "АРМ Партнёра UMRABOR — кабинет тур-оператора",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
