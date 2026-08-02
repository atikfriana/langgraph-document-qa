/**
 * Formats a 0-1 similarity score as a whole-number percentage, e.g. 0.813 -> "81%".
 */
export function formatScore(score: number): string {
  return `${Math.round(score * 100)}%`;
}

/**
 * Truncates a session id for compact display, e.g.
 * "a1b2c3d4-e5f6-..." -> "a1b2c3d4…".
 */
export function truncateId(id: string, visibleChars = 8): string {
  if (id.length <= visibleChars) return id;
  return `${id.slice(0, visibleChars)}…`;
}

/**
 * Formats a document source path down to just the filename, e.g.
 * "data/sample_document.pdf" -> "sample_document.pdf".
 */
export function formatSourceName(source: string): string {
  const segments = source.split(/[/\\]/);
  return segments[segments.length - 1] || source;
}

/**
 * Formats a millisecond timestamp as a short local time, e.g. "3:42 PM".
 */
export function formatTime(timestampMs: number): string {
  return new Date(timestampMs).toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  });
}
