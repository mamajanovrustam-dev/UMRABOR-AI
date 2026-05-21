/**
 * Лёгкая i18n-обёртка. 4 локали: uz-Cyrl (default), ru, en, uz-Latn.
 * Ключи плоские. Расширяется по мере необходимости.
 */

export type Locale = "uz-Cyrl" | "uz-Latn" | "ru" | "en";

export const DEFAULT_LOCALE: Locale = "uz-Cyrl";

type Dict = Record<string, string>;

const dictionaries: Record<Locale, Dict> = {
  "uz-Cyrl": {
    "nav.home": "Бош саҳифа",
    "nav.catalog": "Каталог",
    "nav.orders": "Буюртмалар",
    "nav.profile": "Профиль",
    "nav.partners": "Тур-операторларга",
    "auth.login": "Кириш",
    "auth.signup": "Рўйхатдан ўтиш",
    "auth.logout": "Чиқиш",
    "common.next": "Кейин",
    "common.back": "Орқага",
    "common.save": "Сақлаш",
    "common.cancel": "Бекор қилиш",
    "common.confirm": "Тасдиқлаш",
    "common.reject": "Рад этиш",
    "common.search": "Қидириш",
    "common.loading": "Юкланмоқда...",
    "common.empty": "Маълумот йўқ",
    "status.new": "Янги",
    "status.processing": "Жараёнда",
    "status.kabul": "Қабул",
    "status.completed": "Тугалланди",
    "status.cancelled": "Бекор",
  },
  ru: {
    "nav.home": "Главная",
    "nav.catalog": "Каталог",
    "nav.orders": "Заказы",
    "nav.profile": "Профиль",
    "nav.partners": "Тур-операторам",
    "auth.login": "Вход",
    "auth.signup": "Регистрация",
    "auth.logout": "Выйти",
    "common.next": "Далее",
    "common.back": "Назад",
    "common.save": "Сохранить",
    "common.cancel": "Отмена",
    "common.confirm": "Подтвердить",
    "common.reject": "Отказать",
    "common.search": "Поиск",
    "common.loading": "Загрузка...",
    "common.empty": "Нет данных",
    "status.new": "Новая",
    "status.processing": "В обработке",
    "status.kabul": "Принято",
    "status.completed": "Завершено",
    "status.cancelled": "Отменено",
  },
  en: {
    "nav.home": "Home",
    "nav.catalog": "Catalog",
    "nav.orders": "Orders",
    "nav.profile": "Profile",
    "nav.partners": "For Operators",
    "auth.login": "Sign in",
    "auth.signup": "Sign up",
    "auth.logout": "Sign out",
    "common.next": "Next",
    "common.back": "Back",
    "common.save": "Save",
    "common.cancel": "Cancel",
    "common.confirm": "Confirm",
    "common.reject": "Reject",
    "common.search": "Search",
    "common.loading": "Loading...",
    "common.empty": "No data",
    "status.new": "New",
    "status.processing": "Processing",
    "status.kabul": "Accepted",
    "status.completed": "Completed",
    "status.cancelled": "Cancelled",
  },
  "uz-Latn": {
    "nav.home": "Bosh sahifa",
    "nav.catalog": "Katalog",
    "nav.orders": "Buyurtmalar",
    "nav.profile": "Profil",
    "nav.partners": "Tur-operatorlarga",
    "auth.login": "Kirish",
    "auth.signup": "Roʻyxatdan oʻtish",
    "auth.logout": "Chiqish",
    "common.next": "Keyin",
    "common.back": "Orqaga",
    "common.save": "Saqlash",
    "common.cancel": "Bekor qilish",
    "common.confirm": "Tasdiqlash",
    "common.reject": "Rad etish",
    "common.search": "Qidirish",
    "common.loading": "Yuklanmoqda...",
    "common.empty": "Maʼlumot yoʻq",
    "status.new": "Yangi",
    "status.processing": "Jarayonda",
    "status.kabul": "Qabul",
    "status.completed": "Tugallandi",
    "status.cancelled": "Bekor",
  },
};

export function t(key: string, locale: Locale = DEFAULT_LOCALE): string {
  return dictionaries[locale]?.[key] ?? dictionaries[DEFAULT_LOCALE]?.[key] ?? key;
}

export function getLocales(): Locale[] {
  return ["uz-Cyrl", "uz-Latn", "ru", "en"];
}
