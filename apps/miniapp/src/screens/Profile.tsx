import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";

export function ProfileScreen() {
  const navigate = useNavigate();
  const authed = !!api.accessToken;

  function logout() {
    api.clearAuth();
    navigate("/home");
  }

  return (
    <div className="px-4 py-5">
      <h2 className="mb-4 text-lg font-extrabold">Профиль</h2>

      {!authed ? (
        <button
          onClick={() => navigate("/login")}
          className="w-full rounded-xl bg-umGreen py-3 font-semibold text-white"
        >
          Кириш
        </button>
      ) : (
        <div className="space-y-2">
          <div className="rounded-xl bg-card p-3 text-sm">🌐 Тил · Ўзбек</div>
          <div className="rounded-xl bg-card p-3 text-sm">🔔 Уведомления · Yoqilgan</div>
          <div className="rounded-xl bg-card p-3 text-sm">❓ Саволлар (FAQ)</div>
          <div className="rounded-xl bg-card p-3 text-sm">💬 Қўллаб-қувватлаш</div>
          <button
            onClick={logout}
            className="mt-4 w-full rounded-xl border border-red-500/40 bg-red-500/10 py-3 font-semibold text-red-300"
          >
            Чиқиш
          </button>
        </div>
      )}
    </div>
  );
}
