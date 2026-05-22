import { createApiClient } from "@umrabor/shared";

const baseUrl =
  (import.meta as unknown as { env: { VITE_API_URL?: string } }).env?.VITE_API_URL ??
  "http://localhost:8000";

export const api = createApiClient({
  baseUrl,
  storageKey: "umrabor_miniapp_auth",
});
