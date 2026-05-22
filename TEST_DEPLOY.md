# UMRABOR — Тестовая среда без VPS + подключение домена

Бесплатный staging-деплой через **Render** (backend + Postgres) и **Vercel** (4 фронтенда).
Стоимость: **0 ₽/мес**. Время настройки: ~30 минут.

После этого подключаем ваш домен — инструкции в конце документа.

---

## Шаг 1. Деплой backend на Render

1. Заходим на https://render.com → **Sign in with GitHub**.
2. Авторизуем доступ к репозиторию `mamajanovrustam-dev/UMRABOR-AI`.
3. Жмём **New +** → **Blueprint**.
4. Выбираем репозиторий **UMRABOR-AI** → ветка **claude/umrachi-YZR5K**.
5. Render увидит файл `render.yaml` и предложит создать сразу 2 ресурса:
   - PostgreSQL `umrabor-db` (free)
   - Web Service `umrabor-api` (free)
6. Нажимаем **Apply** → ждём 5–10 минут (первая сборка контейнера).
7. После успеха получите URL вида `https://umrabor-api.onrender.com` — Swagger: `/docs`.

**Первая загрузка сидов (один раз).** Render Shell:
- В дашборде Render → `umrabor-api` → вкладка **Shell** → введите:
  ```
  python -m app.scripts.seed
  ```
  Должны увидеть: `✓ Сиды загружены. Демо-логины: ...`

> ⚠️ **Особенность Render free tier:** сервис «засыпает» после 15 минут неактивности. Первый запрос потом будет 30–60 сек. Для production переходите на платный план или VPS.

---

## Шаг 2. Деплой 4 фронтендов на Vercel

Vercel разворачивает Next.js / Vite приложения за минуты. Делаем **4 раза** (по одному на каждое приложение).

1. Заходим на https://vercel.com → **Sign up with GitHub**.
2. На дашборде **Add New → Project** → выбираем репо **UMRABOR-AI**.
3. Для **каждого** приложения создаём отдельный проект с такими настройками:

| # | Проект Vercel | Root Directory | Имя по умолчанию |
|---|---|---|---|
| 1 | `umrabor-web`      | `apps/web`       | umrabor-web.vercel.app |
| 2 | `umrabor-platform` | `apps/platform`  | umrabor-platform.vercel.app |
| 3 | `umrabor-partner`  | `apps/partner`   | umrabor-partner.vercel.app |
| 4 | `umrabor-miniapp`  | `apps/miniapp`   | umrabor-miniapp.vercel.app |

**Для каждого проекта:**
1. **Framework Preset:** Next.js (или Vite для miniapp) — Vercel определит автоматически.
2. **Root Directory:** установить как в таблице (через **Edit** в шаге Import).
3. **Build Command:** оставить из vercel.json (или ввести вручную, см. ниже).
4. **Environment Variables:** добавить одну:
   - Имя: `NEXT_PUBLIC_API_URL` (для miniapp — `VITE_API_URL`)
   - Значение: URL вашего Render-бэкенда, например `https://umrabor-api.onrender.com`
5. **Deploy** — ждём 2–4 минуты.

Если Vercel не подхватил `pnpm` автоматически — в **Settings → General** установить:
- **Install Command:** `corepack enable && pnpm install`
- **Build Command** (для каждого):
  - web:      `pnpm --filter @umrabor/web build`
  - platform: `pnpm --filter @umrabor/platform build`
  - partner:  `pnpm --filter @umrabor/partner build`
  - miniapp:  `pnpm --filter @umrabor/miniapp build`
- **Output Directory:** `apps/<name>/.next` (для miniapp — `apps/miniapp/dist`)

---

## Шаг 3. Обновить CORS в Render

После деплоя фронтов нужно сказать backend'у, что им можно стучаться.

В дашборде Render → `umrabor-api` → **Environment** → найти `CORS_ORIGINS`,
обновить значение (через запятую все ваши финальные URL):

```
https://umrabor-web.vercel.app,https://umrabor-platform.vercel.app,https://umrabor-partner.vercel.app,https://umrabor-miniapp.vercel.app
```

Нажмите **Save Changes** — сервис перезапустится автоматически.

---

## Шаг 4. Готово, можно тестировать

| URL | Назначение | Логин |
|---|---|---|
| `umrabor-platform.vercel.app/login` | АРМ Платформы | `yulia.m` / `Demo-2026!` |
| `umrabor-partner.vercel.app/login` | АРМ Партнёра | `ibrahim.r` / `Demo-2026!` |
| `umrabor-web.vercel.app` | Публичный сайт | OTP `0000` для login |
| `umrabor-miniapp.vercel.app` | Mini App | OTP `0000` для login |
| `umrabor-api.onrender.com/docs` | Swagger | — |

---

# 🌐 Подключение своего домена

Vercel и Render оба поддерживают custom domains бесплатно, включая SSL.
Например, если у вас домен `umrabor.uz`, распределим поддомены так:

| Поддомен | Куда указывает |
|---|---|
| `umrabor.uz` (+ www) | umrabor-web (Vercel) |
| `admin.umrabor.uz`   | umrabor-platform (Vercel) |
| `partner.umrabor.uz` | umrabor-partner (Vercel) |
| `miniapp.umrabor.uz` | umrabor-miniapp (Vercel) |
| `api.umrabor.uz`     | umrabor-api (Render) |

## A. Добавляем домены в Vercel/Render

**Vercel** (для web, platform, partner, miniapp):
1. Открываем проект в Vercel.
2. **Settings** → **Domains** → **Add**.
3. Вводим нужный поддомен (например `admin.umrabor.uz`).
4. Vercel покажет какие DNS-записи нужно добавить:
   - Обычно: тип **CNAME**, значение `cname.vercel-dns.com`
   - Для корневого домена (apex `umrabor.uz`): тип **A**, значение `76.76.21.21`

**Render** (для api):
1. Открываем сервис `umrabor-api` в Render.
2. **Settings** → **Custom Domains** → **Add Custom Domain**.
3. Вводим `api.umrabor.uz`.
4. Render покажет CNAME-запись: тип **CNAME**, значение `umrabor-api.onrender.com`.

## B. Прописываем DNS-записи у регистратора

Что нужно сделать у вашего регистратора домена (там где вы купили `umrabor.uz`):

| Запись | Тип | Имя | Значение |
|---|---|---|---|
| Корень umrabor.uz | A | `@` (или пусто) | `76.76.21.21` |
| www | CNAME | `www` | `cname.vercel-dns.com` |
| admin | CNAME | `admin` | `cname.vercel-dns.com` |
| partner | CNAME | `partner` | `cname.vercel-dns.com` |
| miniapp | CNAME | `miniapp` | `cname.vercel-dns.com` |
| api | CNAME | `api` | `umrabor-api.onrender.com` |

> **Где это сделать?** Зависит от регистратора:
> - **uznic.uz** — личный кабинет → «Управление зоной DNS»
> - **Cloudflare** — DNS → Records → Add Record
> - **Namecheap** — Domain List → Manage → Advanced DNS
> - **GoDaddy** — DNS Management
>
> Если не понятно как — напишите мне название регистратора, дам точную инструкцию.

## C. Ждём DNS-распространение (5–60 минут)

После добавления DNS-записей подождите. Проверить можно через:
```
https://www.whatsmydns.net/#A/umrabor.uz
```

Когда увидите свой IP во всех зонах — Vercel и Render автоматически выпустят SSL-сертификаты и всё начнёт работать по HTTPS.

## D. Обновляем CORS и переменные окружения

Когда домены заработают, нужно обновить env-переменные:

**В Render (бэкенд):**
- `CORS_ORIGINS` →
  ```
  https://umrabor.uz,https://www.umrabor.uz,https://admin.umrabor.uz,https://partner.umrabor.uz,https://miniapp.umrabor.uz
  ```

**В Vercel (каждый из 4 проектов):**
- `NEXT_PUBLIC_API_URL` → `https://api.umrabor.uz` (для miniapp — `VITE_API_URL`)
- После сохранения — **Deployments → Redeploy** для применения.

## E. Готово ✓

После этого:
- https://umrabor.uz — сайт
- https://admin.umrabor.uz — Платформа
- https://partner.umrabor.uz — Партнёр
- https://miniapp.umrabor.uz — Mini App
- https://api.umrabor.uz/docs — Swagger

Всё под HTTPS, бесплатно, с автоматическим SSL.

---

## Когда переходить на VPS?

Render free tier хорош для теста, но имеет ограничения:
- Засыпание после 15 мин неактивности (cold start 30–60 сек)
- Бесплатный Postgres удаляется через 90 дней
- 750 часов/месяц (хватает на 1 сервис 24/7)

Когда будете готовы к production — следуйте `DEPLOYMENT.md` (Hetzner CX22 + Nginx + Certbot). Домен можно переключить за 5 минут через смену DNS A-записей.
