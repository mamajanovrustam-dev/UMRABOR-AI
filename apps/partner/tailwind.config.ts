import type { Config } from "tailwindcss";
import { umraborPreset } from "@umrabor/ui";

const config: Config = {
  presets: [umraborPreset as Config],
  content: [
    "./src/**/*.{ts,tsx}",
    "../../packages/ui/src/**/*.{ts,tsx}",
  ],
  plugins: [],
};

export default config;
