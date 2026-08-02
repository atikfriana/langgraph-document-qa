"use client";

import { useState } from "react";
import { ConnectionBanner } from "@/components/status/ConnectionBanner";
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";
import type { ChatMessage } from "@/types/chat";
import type { ConnectionStatus } from "@/types/health";

interface ChatWindowProps {
  messages: ChatMessage[];
  isSending: boolean;
  hasFailedMessage: boolean;
  connectionStatus: ConnectionStatus;
  onSend: (message: string) => void;
  onRetry: () => void;
}

export function ChatWindow({
  messages,
  isSending,
  hasFailedMessage,
  connectionStatus,
  onSend,
  onRetry,
}: ChatWindowProps) {
  const [pendingPrompt, setPendingPrompt] = useState<string | undefined>(undefined);

  const isOffline = connectionStatus === "offline";

  return (
    <div className="flex h-full min-h-0 flex-1 flex-col">
      <ConnectionBanner status={connectionStatus} />

      <div className="min-h-0 flex-1">
        <MessageList
          messages={messages}
          isSending={isSending}
          hasFailedMessage={hasFailedMessage}
          onRetry={onRetry}
          onSelectPrompt={setPendingPrompt}
        />
      </div>

      <ChatInput
        onSend={onSend}
        isSending={isSending}
        disabled={isOffline}
        disabledReason={
          isOffline
            ? "Backend unavailable — reconnecting automatically…"
            : undefined
        }
        externalValue={pendingPrompt}
        onExternalValueConsumed={() => setPendingPrompt(undefined)}
      />
    </div>
  );
}
