"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button, Card, CardTitle, Input } from "@umrabor/ui";
import type { TokenPair, UmraborUser } from "@umrabor/shared";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [login, setLogin] = useState("yulia.m");
  const [password, setPassword] = useState("Demo-2026!");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const result = await api.postNoAuth<{ tokens: TokenPair; user: UmraborUser }>(
        "/api/v1/auth/umrabor/login",
        { login, password },
      );
      api.setAuth(result.tokens);
      router.replace("/dashboard");
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
            Платформа · Вход для сотрудников
          </p>
        </div>
        <CardTitle className="mb-4 text-center">Авторизация</CardTitle>
        <form onSubmit={onSubmit} className="space-y-4">
          <Input
            label="Логин"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            autoComplete="username"
            required
          />
          <Input
            label="Пароль"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
          {error && (
            <div className="rounded bg-status-dangerBg p-3 text-sm text-status-danger">
              {error}
            </div>
          )}
          <Button type="submit" className="w-full" size="lg" loading={loading}>
            Войти
          </Button>
          <p className="text-center text-xs text-ink-soft">
            Демо: <span className="font-mono">yulia.m / Demo-2026!</span>
          </p>
        </form>
      </Card>
    </main>
  );
}
