"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { healthService } from "@/services/health-service";
import { HEALTH_POLL_INTERVAL_MS } from "@/lib/constants";
import type { ConnectionStatus, HealthResponse } from "@/types/health";

/**
 * Polls the backend's readiness endpoint on an interval and exposes a
 * simplified connection status for the UI:
 *  - "online"   -> /health/ready succeeded and the vector store is loaded
 *  - "degraded" -> the process is up (/health works) but not fully ready
 *  - "offline"  -> neither endpoint responded (backend unreachable)
 *  - "checking" -> the very first check hasn't resolved yet
 */
export function useHealthStatus() {
  const [status, setStatus] = useState<ConnectionStatus>("checking");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const check = useCallback(async () => {
    try {
      const readiness = await healthService.getReadiness();
      setHealth(readiness);
      setStatus(readiness.vector_store_ready ? "online" : "degraded");
    } catch {
      try {
        const liveness = await healthService.getLiveness();
        setHealth(liveness);
        setStatus("degraded");
      } catch {
        setHealth(null);
        setStatus("offline");
      }
    }
  }, []);

  useEffect(() => {
    check();
    intervalRef.current = setInterval(check, HEALTH_POLL_INTERVAL_MS);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [check]);

  return { status, health, refresh: check };
}
