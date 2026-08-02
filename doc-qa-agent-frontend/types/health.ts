/**
 * Mirrors app/api/routes/health.py's HealthResponse exactly.
 */
export interface HealthResponse {
  status: string;
  environment: string;
  vector_store_ready: boolean;
}

/**
 * Frontend-only connection state derived from polling /health and
 * /health/ready. Not returned by the backend directly.
 */
export type ConnectionStatus = "checking" | "online" | "degraded" | "offline";
