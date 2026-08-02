"use client";

import { useCallback, useEffect, useState } from "react";
import { SESSION_STORAGE_KEY } from "@/lib/constants";

/**
 * Persists the current session_id to localStorage so a page refresh
 * continues the same backend conversation thread instead of silently
 * starting a new one.
 *
 * `isHydrated` guards against a Next.js SSR/client mismatch: localStorage
 * doesn't exist on the server, so the initial render must not assume a
 * stored value is present until after the first client-side effect runs.
 */
export function useSessionId() {
  const [sessionId, setSessionIdState] = useState<string | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem(SESSION_STORAGE_KEY);
    setSessionIdState(stored);
    setIsHydrated(true);
  }, []);

  const setSessionId = useCallback((id: string | null) => {
    setSessionIdState(id);
    if (id) {
      window.localStorage.setItem(SESSION_STORAGE_KEY, id);
    } else {
      window.localStorage.removeItem(SESSION_STORAGE_KEY);
    }
  }, []);

  return { sessionId, setSessionId, isHydrated };
}
