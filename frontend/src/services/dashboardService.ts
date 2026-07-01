import { apiGet } from "../api/client";
import type { DashboardSummary } from "../types/dashboard";

export function getDashboardSummary(): Promise<DashboardSummary> {
  return apiGet<DashboardSummary>("/api/v1/dashboard/summary");
}
