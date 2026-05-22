"use client";
import { createApiClient } from "@umrabor/shared";

const baseUrl =
  process.env.NEXT_PUBLIC_API_URL ??
  (typeof window !== "undefined" && window.location.hostname !== "localhost"
    ? `https://api.${window.location.hostname.replace(/^(www\.|umrabor\.)/, "")}`
    : "http://localhost:8000");

export const api = createApiClient({
  baseUrl,
  storageKey: "umrabor_web_auth",
});
