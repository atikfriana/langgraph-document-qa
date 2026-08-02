import { Bot } from "lucide-react";

export function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 animate-fade-in">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/15 text-primary">
        <Bot className="h-4 w-4" />
      </div>
      <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-sm border border-border bg-card px-4 py-3">
        <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground/70 animate-pulse-dot [animation-delay:0ms]" />
        <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground/70 animate-pulse-dot [animation-delay:200ms]" />
        <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground/70 animate-pulse-dot [animation-delay:400ms]" />
      </div>
    </div>
  );
}
