/**
 * Mirrors app/api/routes/chat.py's ChatRequest exactly.
 */
export interface ChatRequest {
  message: string;
  session_id: string | null;
}

/**
 * Mirrors app/api/routes/chat.py's SourceReference exactly.
 */
export interface ChatSource {
  source: string;
  chunk_id: string;
  score: number;
}

/**
 * Mirrors app/api/routes/chat.py's ChatResponse exactly.
 */
export interface ChatResponse {
  session_id: string;
  response: string;
  tool_used: boolean;
  sources: ChatSource[];
}

export type MessageRole = "user" | "assistant";

/**
 * Frontend-only view model for a single rendered chat bubble. Not a 1:1
 * mirror of any backend type -- this is what the UI needs to render one
 * turn, built from ChatResponse (assistant turns) or raw input (user turns).
 */
export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: number;
  toolUsed?: boolean;
  sources?: ChatSource[];
  isError?: boolean;
}

/**
 * Shape of the structured error body FastAPI's exception handlers return,
 * e.g. { "error": { "code": "vector_store_unavailable", "message": "..." } }
 */
export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
  };
}
