"use client";
import { createApiClient } from "@umrabor/shared";

const baseUrl =
  process.env.NEXT_PUBLIC_API_URL ??
  (typeof window !== "undefined" ? window.location.origin.replace(/^https?:\/\/admin\./, "https://api.") : "http://localhost:8000");

export const api = createApiClient({
  baseUrl,
  storageKey: "umrabor_platform_auth",
  onUnauthorized: () => {
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  },
});
