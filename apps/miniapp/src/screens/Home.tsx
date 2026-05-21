import { Link } from "react-router-dom";

export function HomeScreen() {
  return (
    <div>
      {/* Hero */}
      <div className="relative h-72 overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage:
              "url('https://images.pexels.com/photos/2675268/pexels-photo.jpeg?auto=compress&w=900')",
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/20 to-black/85" />
        <div className="absolute inset-x-4 bottom-4">
          <h1 className="text-2xl font-extrabold leading-tight">
            Юракнинг сезаси —<br />
            <span className="text-gold">умра</span>
          </h1>
          <ul className="mt-3 space-y-1 text-sm text-white/90">
            <li>✓ Лицензияланган тур-операторлар</li>
            <li>✓ Click орқали тўлов · 0,3% кэшбэк</li>
            <li>✓ Барча зиёратчилар учун ваучер</li>
          </ul>
        </div>
      </div>

      {/* Search card */}
      <div className="-mt-6 px-4">
        <div className="rounded-2xl border border-line bg-card p-4 shadow-2xl">
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <div className="mb-1 text-textmuted">Сафар санаси</div>
              <input
                type="date"
                className="w-full rounded bg-card-2 px-2 py-1.5 text-sm text-white outline-none"
              />
            </div>
            <div>
              <div className="mb-1 text-textmuted">Зиёратчилар сони</div>
              <input
                type="number"
                defaultValue={2}
                className="w-full rounded bg-card-2 px-2 py-1.5 text-sm text-white outline-none"
              />
            </div>
          </div>
          <Link
            to="/catalog"
            className="mt-3 block rounded-md bg-umGreen py-3 text-center font-semibold text-white"
          >
            🔍 Қидириш
          </Link>
        </div>
      </div>

      {/* Why UMRABOR */}
      <div className="mt-6 px-4">
        <div className="grid grid-cols-2 gap-2 text-xs">
          {[
            ["🛡", "Лицензияли тур-операторлар"],
            ["💳", "Click орқали хавфсиз тўлов"],
            ["📜", "Ваучер кафолати"],
            ["☎", "24/7 қўллаб-қувватлаш"],
          ].map(([icon, title]) => (
            <div key={title} className="rounded-xl bg-card p-3">
              <div className="text-umGreen text-lg">{icon}</div>
              <div className="mt-1 font-semibold">{title}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
