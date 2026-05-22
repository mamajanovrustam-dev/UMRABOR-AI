"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button, Card, CardTitle, Input } from "@umrabor/ui";
import type { PartnerUser, TokenPair } from "@umrabor/shared";
import { api } from "@/lib/api";

export default function PartnerLoginPage() {
  const router = useRouter();
  const [login, setLogin] = useState("ibrahim.r");
  const [password, setPassword] = useState("Demo-2026!");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const result = await api.postNoAuth<{ tokens: TokenPair; user: PartnerUser }>(
        "/api/v1/auth/partner/login",
        { login, password },
      );
      api.setAuth(result.tokens);
      router.replace(result.user.must_change_password ? "/change-password" : "/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка входа");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-navy p-6">
      <Card className="w-full max-w-md">
        <div className="mb-6 text-center">
          <div className="font-display text-3xl tracking-wider">
            UMRA<span className="text-gold">BOR</span>
          </div>
          <p className="mt-1 text-xs uppercase tracking-wider text-ink-soft">
            Кабинет тур-оператора
          </p>
        </div>
        <CardTitle className="mb-4 text-center">Вход</CardTitle>
        <form onSubmit={onSubmit} className="space-y-4">
          <Input
            label="Логин"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            required
          />
          <Input
            label="Пароль"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && (
            <div className="rounded bg-status-dangerBg p-3 text-sm text-status-danger">{error}</div>
          )}
          <Button type="submit" className="w-full" size="lg" loading={loading}>
            Войти
          </Button>
          <p className="text-center text-xs text-ink-soft">
            Демо-админ: <span className="font-mono">ibrahim.r / Demo-2026!</span>
            <br />
            Оператор: <span className="font-mono">dilfuza.t-rt / Demo-2026!</span>
          </p>
        </form>
      </Card>
    </main>
  );
}
