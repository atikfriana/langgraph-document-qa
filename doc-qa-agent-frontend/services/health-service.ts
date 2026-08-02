import { apiClient } from "./api-client";
import type { HealthResponse } from "@/types/health";

/**
 * Health/readiness API calls, matching app/api/routes/health.py.
 */
export const healthService = {
  getLiveness(): Promise<HealthResponse> {
    return apiClient.get<HealthResponse>("/health", { timeoutMs: 8_000 });
  },
  getReadiness(): Promise<HealthResponse> {
    return apiClient.get<HealthResponse>("/health/ready", { timeoutMs: 8_000 });
  },
};
