import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { CustomerUser, TokenPair } from "@umrabor/shared";
import { api } from "../lib/api";

export function LoginScreen() {
  const navigate = useNavigate();
  const [phone, setPhone] = useState("+998901234321");
  const [code, setCode] = useState("");
  const [step, setStep] = useState<"phone" | "code">("phone");
  const [error, setError] = useState<string | null>(null);
  const [debugCode, setDebugCode] = useState<string | null>(null);

  async function sendCode() {
    setError(null);
    try {
      const res = await api.postNoAuth<{ debug_code?: string }>(
        "/api/v1/auth/customer/otp/request",
        { phone },
      );
      setStep("code");
      if (res.debug_code) setDebugCode(res.debug_code);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function verify() {
    setError(null);
    try {
      const res = await api.postNoAuth<{ tokens: TokenPair; user: CustomerUser }>(
        "/api/v1/auth/customer/otp/verify",
        { phone, code },
      );
      api.setAuth(res.tokens);
      navigate("/orders");
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="px-5 py-8">
      <h2 className="text-xl font-bold">Кириш</h2>
      <p className="mt-1 text-sm text-textmuted">Тасдиқлаш коди телефонга юборилади</p>

      {step === "phone" ? (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendCode();
          }}
          className="mt-5 space-y-3"
        >
          <input
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+998 90 ..."
            className="w-full rounded-md border border-line bg-card-2 px-3 py-3 font-mono outline-none focus:border-umGreen"
            required
          />
          {error && <div className="rounded bg-red-500/20 p-2 text-sm text-red-300">{error}</div>}
          <button
            type="submit"
            className="w-full rounded-xl bg-umGreen py-3 font-semibold text-white"
          >
            Кодни юбориш
          </button>
        </form>
      ) : (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            verify();
          }}
          className="mt-5 space-y-3"
        >
          <div className="rounded bg-card-2 p-3 text-sm">
            Код юборилди: <b>{phone}</b>
            {debugCode && (
              <div className="mt-1 text-xs text-gold">Тестовый код: {debugCode}</div>
            )}
          </div>
          <input
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="0000"
            inputMode="numeric"
            maxLength={6}
            className="w-full rounded-md border border-line bg-card-2 px-3 py-3 text-center font-mono text-2xl outline-none focus:border-umGreen"
            required
          />
          {error && <div className="rounded bg-red-500/20 p-2 text-sm text-red-300">{error}</div>}
          <button
            type="submit"
            className="w-full rounded-xl bg-umGreen py-3 font-semibold text-white"
          >
            Кириш
          </button>
        </form>
      )}
    </div>
  );
}
