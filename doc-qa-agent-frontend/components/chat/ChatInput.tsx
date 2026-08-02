"use client";

import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { ArrowUp, Loader2 } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string) => void;
  isSending: boolean;
  disabled?: boolean;
  disabledReason?: string;
  externalValue?: string;
  onExternalValueConsumed?: () => void;
}

const MAX_TEXTAREA_HEIGHT_PX = 200;

export function ChatInput({
  onSend,
  isSending,
  disabled = false,
  disabledReason,
  externalValue,
  onExternalValueConsumed,
}: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  // Allows EmptyState's suggested-prompt buttons to populate the input.
  useEffect(() => {
    if (externalValue !== undefined) {
      setValue(externalValue);
      onExternalValueConsumed?.();
      textareaRef.current?.focus();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [externalValue]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, MAX_TEXTAREA_HEIGHT_PX)}px`;
  }, [value]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || isSending || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const isEmpty = value.trim().length === 0;

  return (
    <div className="border-t border-border bg-background/80 px-4 py-4 backdrop-blur-xl sm:px-6">
      <div className="mx-auto max-w-3xl">
        {disabled && disabledReason && (
          <p className="mb-2 text-center text-xs text-muted-foreground">
            {disabledReason}
          </p>
        )}
        <div
          className={cn(
            "flex items-end gap-2 rounded-2xl border border-border bg-card p-2 shadow-sm transition-colors focus-within:border-primary/50",
            disabled && "opacity-60"
          )}
        >
          <Textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about the document…"
            rows={1}
            disabled={disabled}
            className="max-h-[200px] min-h-[40px] flex-1 border-0 bg-transparent px-2 py-2 shadow-none focus-visible:ring-0"
          />
          <Button
            type="button"
            size="icon"
            onClick={handleSend}
            disabled={isEmpty || isSending || disabled}
            aria-label="Send message"
            className="mb-0.5 shrink-0 rounded-xl"
          >
            {isSending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <ArrowUp className="h-4 w-4" />
            )}
          </Button>
        </div>
        <p className="mt-2 text-center text-[11px] text-muted-foreground">
          Enter to send · Shift+Enter for a new line
        </p>
      </div>
    </div>
  );
}
