"use client";

import { useCallback, useState } from "react";
import { chatService } from "@/services/chat-service";
import { ApiError, NetworkError } from "@/services/api-client";
import { useSessionId } from "./useSessionId";
import type { ChatMessage } from "@/types/chat";

function createId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

/**
 * Maps a thrown error from the API layer into a human-readable message for
 * the chat bubble. Centralizing this here means every error state required
 * by the spec (connection lost, 502, 429 quota exceeded, generic backend
 * failure) is handled in exactly one place.
 */
function describeError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 429:
        return "Rate limit or quota exceeded. Please wait a moment and try again.";
      case 502:
        return "The agent failed to produce a response. Please retry.";
      case 503:
        return "The document index isn't ready yet. Please try again shortly.";
      default:
        return error.message;
    }
  }
  if (error instanceof NetworkError) {
    return error.message;
  }
  return "Something went wrong. Please try again.";
}

export function useChat() {
  const { sessionId, setSessionId, isHydrated } = useSessionId();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [lastFailedMessage, setLastFailedMessage] = useState<string | null>(null);

  const appendMessage = useCallback((message: ChatMessage) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isSending) return;

      setLastFailedMessage(null);

      appendMessage({
        id: createId(),
        role: "user",
        content: trimmed,
        createdAt: Date.now(),
      });
      setIsSending(true);

      try {
        const result = await chatService.sendMessage(trimmed, sessionId);
        setSessionId(result.session_id);
        appendMessage({
          id: createId(),
          role: "assistant",
          content: result.response,
          createdAt: Date.now(),
          toolUsed: result.tool_used,
          sources: result.sources,
        });
      } catch (error) {
        appendMessage({
          id: createId(),
          role: "assistant",
          content: describeError(error),
          createdAt: Date.now(),
          isError: true,
        });
        setLastFailedMessage(trimmed);
      } finally {
        setIsSending(false);
      }
    },
    [appendMessage, isSending, sessionId, setSessionId]
  );

  const retryLastMessage = useCallback(() => {
    if (!lastFailedMessage) return;

    // Drop the trailing error bubble before re-sending, so a retry doesn't
    // stack duplicate error messages in the transcript.
    setMessages((prev) => {
      const reversedIndex = [...prev].reverse().findIndex((m) => m.isError);
      if (reversedIndex === -1) return prev;
      const indexToRemove = prev.length - 1 - reversedIndex;
      return prev.filter((_, idx) => idx !== indexToRemove);
    });

    void sendMessage(lastFailedMessage);
  }, [lastFailedMessage, sendMessage]);

  const clearConversation = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setLastFailedMessage(null);
  }, [setSessionId]);

  return {
    messages,
    sendMessage,
    retryLastMessage,
    clearConversation,
    isSending,
    sessionId,
    isHydrated,
    hasFailedMessage: Boolean(lastFailedMessage),
  };
}
