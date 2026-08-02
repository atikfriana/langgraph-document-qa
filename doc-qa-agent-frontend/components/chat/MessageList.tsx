"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { useAutoScroll } from "@/hooks/useAutoScroll";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import { EmptyState } from "./EmptyState";
import type { ChatMessage } from "@/types/chat";

interface MessageListProps {
  messages: ChatMessage[];
  isSending: boolean;
  hasFailedMessage: boolean;
  onRetry: () => void;
  onSelectPrompt: (prompt: string) => void;
}

export function MessageList({
  messages,
  isSending,
  hasFailedMessage,
  onRetry,
  onSelectPrompt,
}: MessageListProps) {
  const scrollRef = useAutoScroll(messages.length + (isSending ? 1 : 0));

  if (messages.length === 0 && !isSending) {
    return <EmptyState onSelectPrompt={onSelectPrompt} />;
  }

  const lastErrorId = [...messages].reverse().find((m) => m.isError)?.id;

  return (
    <ScrollArea className="h-full">
      <div ref={scrollRef} className="mx-auto flex max-w-3xl flex-col gap-5 px-4 py-6 sm:px-6">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            isLastFailedMessage={hasFailedMessage && message.id === lastErrorId}
            onRetry={onRetry}
          />
        ))}
        {isSending && <TypingIndicator />}
      </div>
    </ScrollArea>
  );
}
