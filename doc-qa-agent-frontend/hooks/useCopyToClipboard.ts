"use client";

import { useCallback, useState } from "react";

/**
 * Copies text to the clipboard and exposes a transient `copied` flag,
 * so a "Copy" button can flip to "Copied!" for `resetDelayMs` and revert.
 */
export function useCopyToClipboard(resetDelayMs = 1500) {
  const [copied, setCopied] = useState(false);

  const copy = useCallback(
    async (text: string) => {
      try {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), resetDelayMs);
      } catch {
        setCopied(false);
      }
    },
    [resetDelayMs]
  );

  return { copied, copy };
}
