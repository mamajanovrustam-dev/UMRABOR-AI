"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { CustomerUser, TokenPair } from "@umrabor/shared";
import { api } from "@/lib/api";

export default function WebLoginPage() {
  const router = useRouter();
  const [phone, setPhone] = useState("+998901234321");
  const [code, setCode] = useState("");
  const [step, setStep] = useState<"phone" | "code">("phone");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [hint, setHint] = useState<string | null>(null);

  async function sendCode() {
    setError(null);
    setLoading(true);
    try {
      const res = await api.postNoAuth<{ sent: boolean; debug_code?: string }>(
        "/api/v1/auth/customer/otp/request",
        { phone },
      );
      if (res.debug_code) setHint(`Тестовый код: ${res.debug_code}`);
      setStep("code");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function verifyCode() {
    setError(null);
    setLoading(true);
    try {
      const res = await api.postNoAuth<{ tokens: TokenPair; user: CustomerUser }>(
        "/api/v1/auth/customer/otp/verify",
        { phone, code },
      );
      api.setAuth(res.tokens);
      router.replace("/orders");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container-mx flex min-h-[70vh] items-center justify-center py-12">
      <div className="w-full max-w-md rounded-2xl border border-line bg-card p-8">
        <h1 className="text-2xl font-bold">Кириш</h1>
        <p className="mt-1 text-sm text-textmuted">Авторизация по номеру телефона</p>

        {step === "phone" ? (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              sendCode();
            }}
            className="mt-6 space-y-4"
          >
            <div>
              <label className="text-xs uppercase text-textmuted">Телефон</label>
              <input
                className="mt-1 w-full rounded-md border border-line bg-card-2 px-3 py-2 font-mono text-white outline-none focus:border-umGreen"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+998 90 ..."
                required
              />
            </div>
            {error && <div className="rounded bg-red-500/15 p-3 text-sm text-red-400">{error}</div>}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-umGreen py-3 font-semibold text-white hover:bg-umGreen-dark disabled:opacity-50"
            >
              {loading ? "Отправка..." : "Получить код"}
            </button>
          </form>
        ) : (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              verifyCode();
            }}
            className="mt-6 space-y-4"
          >
            <div className="rounded bg-card-2 p-3 text-sm text-textmuted">
              Код отправлен на <b className="text-white">{phone}</b>
              {hint && <div className="mt-1 text-xs text-gold">{hint}</div>}
            </div>
            <div>
              <label className="text-xs uppercase text-textmuted">Код</label>
              <input
                className="mt-1 w-full rounded-md border border-line bg-card-2 px-3 py-2 font-mono text-white outline-none focus:border-umGreen"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="0000"
                inputMode="numeric"
                maxLength={6}
                required
              />
            </div>
            {error && <div className="rounded bg-red-500/15 p-3 text-sm text-red-400">{error}</div>}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-umGreen py-3 font-semibold text-white hover:bg-umGreen-dark disabled:opacity-50"
            >
              {loading ? "Проверка..." : "Войти"}
            </button>
            <button
              type="button"
              onClick={() => setStep("phone")}
              className="w-full text-xs text-textmuted hover:text-white"
            >
              ← Изменить номер
            </button>
          </form>
        )}
      </div>
    </main>
  );
}
