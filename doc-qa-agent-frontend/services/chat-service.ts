import { apiClient } from "./api-client";
import type { ChatRequest, ChatResponse } from "@/types/chat";

/**
 * Chat domain API calls. Components/hooks call these, never `fetch`
 * directly -- this is the single seam that knows the /chat request/response
 * shape from app/api/routes/chat.py.
 */
export const chatService = {
  sendMessage(message: string, sessionId: string | null): Promise<ChatResponse> {
    const payload: ChatRequest = { message, session_id: sessionId };
    // Generation can involve a tool round-trip (web search) plus retrieval,
    // so this gets a longer timeout than the default.
    return apiClient.post<ChatResponse>("/chat", payload, { timeoutMs: 60_000 });
  },
};
