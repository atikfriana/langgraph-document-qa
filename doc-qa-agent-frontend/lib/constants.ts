export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const SESSION_STORAGE_KEY = "doc-qa-session-id";
export const HEALTH_POLL_INTERVAL_MS = 30_000;
export const APP_NAME = "Document QA Assistant";
export const APP_TAGLINE = "Ask anything about your document.";

export const SUGGESTED_PROMPTS = [
  "What is this document about?",
  "Summarize the key points.",
  "What are the technical specifications mentioned?",
  "Is there any pricing information?",
] as const;
