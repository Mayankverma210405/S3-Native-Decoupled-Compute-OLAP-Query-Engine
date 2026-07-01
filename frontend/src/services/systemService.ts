import { apiGet } from "../api/client";
import type { SystemOverview } from "../types/system";

export function getSystemOverview(): Promise<SystemOverview> {
  return apiGet<SystemOverview>("/api/v1/system/overview");
}