import Link from "next/link";

export default function HomePage() {
  return (
    <main>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-30"
          style={{
            backgroundImage:
              "url('https://images.pexels.com/photos/12777419/pexels-photo-12777419.jpeg?auto=compress&cs=tinysrgb&w=1600')",
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-br from-bg via-bg/70 to-transparent" />
        <div className="container-mx relative py-24 lg:py-32">
          <span className="inline-flex items-center gap-2 rounded-full border border-umGreen/40 bg-umGreen/15 px-3 py-1 text-xs font-bold uppercase tracking-wider text-umGreen">
            ● Тур-операторлар учун
          </span>
          <h1 className="mt-5 max-w-3xl text-5xl font-extrabold leading-tight tracking-tight lg:text-6xl">
            Умра сафари — <span className="text-umGreen">шаффоф</span> ва{" "}
            <span className="text-gold">осон</span> бронлаш
          </h1>
          <p className="mt-5 max-w-xl text-lg text-white/80">
            UMRABOR — Узбекистон зиёратчилари учун умра турларини бронлаш платформаси.
            Лицензияланган тур-операторлар, шаффоф нархлар, Click орқали хавфсиз тўлов.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/catalog" className="rounded-md bg-umGreen px-6 py-3 font-semibold text-white shadow-lg shadow-umGreen/30 hover:bg-umGreen-dark">
              Каталогни кўриш →
            </Link>
            <Link href="/partners-landing" className="rounded-md border border-white/25 bg-white/5 px-6 py-3 font-semibold text-white hover:bg-white/10 backdrop-blur">
              Тур-оператор бўлинг
            </Link>
          </div>
        </div>
      </section>

      {/* Why UMRABOR */}
      <section className="container-mx py-16">
        <h2 className="text-3xl font-extrabold">Нега UMRABOR?</h2>
        <p className="mt-2 text-textmuted">Минглаб зиёратчилар бизга ишонишади</p>
        <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[
            ["Лицензияланган операторлар", "Барча тур-операторлар Госкомтуризм лицензияси билан"],
            ["24/7 қўллаб-қувватлаш", "Сафар давомида ҳар қандай саволингизга жавоб берадиган жамоа"],
            ["Шаффоф нархлар", "Барча тарифлар очиқ кўрсатилади — фақат битта нарх"],
            ["Маҳрам логикаси", "Тизим оила алоқаларингизни ҳисобга олиб тўғри жойлашувни таклиф этади"],
            ["Click интеграцияси", "Узбекистон #1 тўлов тизими орқали хавфсиз тўлов · 0.3% кешбэк"],
            ["Auto-генерация ваучеров", "Ҳар бир зиёратчи учун алоҳида PDF ваучер"],
          ].map(([title, desc]) => (
            <div key={title} className="rounded-xl border border-line bg-card p-5">
              <h3 className="font-bold">{title}</h3>
              <p className="mt-2 text-sm text-textmuted">{desc}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
