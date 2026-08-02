"use client";

import { useEffect, useRef } from "react";

/**
 * Returns a ref to attach to a scrollable container. Whenever `dependency`
 * changes (e.g. the messages array grows), the container smoothly scrolls
 * to the bottom.
 */
export function useAutoScroll<T>(dependency: T) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [dependency]);

  return containerRef;
}
