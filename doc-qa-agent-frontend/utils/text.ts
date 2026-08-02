/**
 * Splits plain assistant text into paragraphs for lightweight rendering.
 * The backend returns plain text (not markdown), so this avoids pulling in
 * a full markdown renderer for what is effectively double-newline-separated
 * prose.
 */
export function splitParagraphs(text: string): string[] {
  return text
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter(Boolean);
}
