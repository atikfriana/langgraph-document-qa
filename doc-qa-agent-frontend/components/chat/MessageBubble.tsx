"use client";

import { motion } from "framer-motion";
import { Bot, User, Copy, Check, RotateCcw, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useCopyToClipboard } from "@/hooks/useCopyToClipboard";
import { splitParagraphs } from "@/utils/text";
import { formatTime } from "@/utils/formatters";
import { ToolUsedBadge } from "./ToolUsedBadge";
import { SourcesPanel } from "./SourcesPanel";
import type { ChatMessage } from "@/types/chat";

interface MessageBubbleProps {
  message: ChatMessage;
  isLastFailedMessage: boolean;
  onRetry: () => void;
}

export function MessageBubble({
  message,
  isLastFailedMessage,
  onRetry,
}: MessageBubbleProps) {
  const { copied, copy } = useCopyToClipboard();
  const isUser = message.role === "user";
  const paragraphs = splitParagraphs(message.content);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className={cn("flex items-start gap-3", isUser && "flex-row-reverse")}
    >
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
          isUser
            ? "bg-secondary text-secondary-foreground"
            : message.isError
              ? "bg-destructive/15 text-destructive"
              : "bg-primary/15 text-primary"
        )}
      >
        {isUser ? (
          <User className="h-4 w-4" />
        ) : message.isError ? (
          <AlertCircle className="h-4 w-4" />
        ) : (
          <Bot className="h-4 w-4" />
        )}
      </div>

      <div className={cn("group max-w-[80%] sm:max-w-[70%]", isUser && "flex flex-col items-end")}>
        <div
          className={cn(
            "rounded-2xl border px-4 py-3 text-sm leading-relaxed shadow-sm",
            isUser
              ? "rounded-tr-sm border-primary/20 bg-primary text-primary-foreground"
              : message.isError
                ? "rounded-tl-sm border-destructive/30 bg-destructive/10 text-foreground"
                : "rounded-tl-sm border-border bg-card text-card-foreground"
          )}
        >
          {paragraphs.length > 0 ? (
            paragraphs.map((paragraph, idx) => (
              <p key={idx} className={idx > 0 ? "mt-2" : undefined}>
                {paragraph}
              </p>
            ))
          ) : (
            <p className="italic text-muted-foreground">(empty response)</p>
          )}

          {!isUser && !message.isError && message.sources && (
            <SourcesPanel sources={message.sources} />
          )}
        </div>

        <div
          className={cn(
            "mt-1.5 flex items-center gap-2 text-[11px] text-muted-foreground",
            isUser && "flex-row-reverse"
          )}
        >
          <span>{formatTime(message.createdAt)}</span>

          {!isUser && !message.isError && typeof message.toolUsed === "boolean" && (
            <ToolUsedBadge toolUsed={message.toolUsed} />
          )}

          {!isUser && !message.isError && (
            <button
              type="button"
              onClick={() => copy(message.content)}
              className="flex items-center gap-1 opacity-0 transition-opacity hover:text-foreground group-hover:opacity-100"
              aria-label="Copy response"
            >
              {copied ? (
                <Check className="h-3 w-3 text-success" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </button>
          )}

          {message.isError && isLastFailedMessage && (
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={onRetry}
              className="h-6 gap-1 px-2 text-[11px]"
            >
              <RotateCcw className="h-3 w-3" />
              Retry
            </Button>
          )}
        </div>
      </div>
    </motion.div>
  );
}
