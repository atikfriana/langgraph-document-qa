"use client";

import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import type { ConnectionStatus, HealthResponse } from "@/types/health";

interface HealthBadgeProps {
  status: ConnectionStatus;
  health: HealthResponse | null;
  className?: string;
}

const STATUS_CONFIG: Record<
  ConnectionStatus,
  { label: string; dotClass: string; description: string }
> = {
  checking: {
    label: "Checking…",
    dotClass: "bg-muted-foreground animate-pulse-dot",
    description: "Checking connection to the backend…",
  },
  online: {
    label: "Online",
    dotClass: "bg-success",
    description: "Backend is reachable and the document index is ready.",
  },
  degraded: {
    label: "Degraded",
    dotClass: "bg-amber-500",
    description:
      "Backend is reachable, but the document index isn't fully ready yet.",
  },
  offline: {
    label: "Offline",
    dotClass: "bg-destructive",
    description: "Backend is unreachable. Check that the API server is running.",
  },
};

export function HealthBadge({ status, health, className }: HealthBadgeProps) {
  const config = STATUS_CONFIG[status];

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div
          className={cn(
            "flex items-center gap-2 rounded-full border border-border bg-secondary/60 px-3 py-1.5 text-xs font-medium",
            className
          )}
        >
          <span className={cn("h-2 w-2 shrink-0 rounded-full", config.dotClass)} />
          <span className="text-muted-foreground">{config.label}</span>
        </div>
      </TooltipTrigger>
      <TooltipContent side="right" className="max-w-[220px]">
        <p>{config.description}</p>
        {health && (
          <p className="mt-1 text-muted-foreground">
            env: {health.environment} · index ready:{" "}
            {health.vector_store_ready ? "yes" : "no"}
          </p>
        )}
      </TooltipContent>
    </Tooltip>
  );
}
