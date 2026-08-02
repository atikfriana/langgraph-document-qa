import { FileText } from "lucide-react";
import { formatScore, formatSourceName } from "@/utils/formatters";
import type { ChatSource } from "@/types/chat";

interface SourceCardProps {
  source: ChatSource;
}

export function SourceCard({ source }: SourceCardProps) {
  const scorePercent = Math.max(0, Math.min(1, source.score)) * 100;

  return (
    <div className="min-w-[200px] flex-1 rounded-lg border border-border bg-secondary/40 p-3">
      <div className="flex items-start gap-2">
        <FileText className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" />
        <div className="min-w-0 flex-1">
          <p className="truncate text-xs font-medium" title={source.source}>
            {formatSourceName(source.source)}
          </p>
          <p className="text-[11px] text-muted-foreground">
            Chunk #{source.chunk_id}
          </p>
        </div>
      </div>

      <div className="mt-2">
        <div className="flex items-center justify-between text-[11px] text-muted-foreground">
          <span>Relevance</span>
          <span className="font-medium text-foreground">
            {formatScore(source.score)}
          </span>
        </div>
        <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-primary transition-all"
            style={{ width: `${scorePercent}%` }}
          />
        </div>
      </div>
    </div>
  );
}
