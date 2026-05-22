import type { Config } from "tailwindcss";

/**
 * Общий Tailwind-пресет UMRABOR. Подключается в каждом приложении через `presets: [umraborPreset]`.
 * Цветовая палитра восстановлена из CSS-переменных оригинальных HTML-прототипов.
 */
export const umraborPreset: Partial<Config> = {
  theme: {
    extend: {
      colors: {
        navy: { DEFAULT: "#0F1226", 2: "#1B1F3A" },
        gold: {
          DEFAULT: "#C9A84C",
          soft: "#FBF5E6",
          dark: "#8A6E2B",
        },
        cream: "#F8F6F1",
        ink: { DEFAULT: "#1A1A2E", soft: "#7A7A8C" },
        // Mini App / web dark theme
        bg: { DEFAULT: "#0B0C0E", 2: "#15171B" },
        card: { DEFAULT: "#1A1C20", 2: "#22252A", 3: "#2A2D33" },
        line: { DEFAULT: "rgba(255,255,255,0.08)", 2: "rgba(255,255,255,0.14)" },
        textmuted: "#8A8E96",
        // brand greens (Mini App)
        umGreen: { DEFAULT: "#1FAF6A", dark: "#178A53" },
        // statuses
        status: {
          active: "#2D7A4F",
          activeBg: "#E6F3EC",
          warn: "#C97E2C",
          warnBg: "#FAEEDA",
          danger: "#A32D2D",
          dangerBg: "#FCEBEB",
          info: "#185FA5",
          infoBg: "#E6F1FB",
          archived: "#F1EFE8",
          archivedFg: "#5F5E5A",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Cormorant Garamond", "serif"],
        mono: ["JetBrains Mono", "monospace"],
        dm: ["DM Sans", "sans-serif"],
      },
      borderRadius: {
        DEFAULT: "9px",
        lg: "12px",
      },
      boxShadow: {
        soft: "0 4px 14px rgba(0,0,0,0.08)",
        umheavy: "0 25px 60px rgba(0,0,0,0.45)",
      },
    },
  },
};

export default umraborPreset;
