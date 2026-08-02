"use client";

import { MessageSquarePlus, Copy, Check, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { HealthBadge } from "@/components/status/HealthBadge";
import { useCopyToClipboard } from "@/hooks/useCopyToClipboard";
import { truncateId } from "@/utils/formatters";
import { APP_NAME } from "@/lib/constants";
import type { ConnectionStatus, HealthResponse } from "@/types/health";

interface SidebarProps {
  sessionId: string | null;
  connectionStatus: ConnectionStatus;
  health: HealthResponse | null;
  onNewChat: () => void;
}

export function Sidebar({
  sessionId,
  connectionStatus,
  health,
  onNewChat,
}: SidebarProps) {
  const { copied, copy } = useCopyToClipboard();

  return (
    <aside className="flex h-dvh w-full flex-col border-r border-border bg-secondary/20 sm:w-72">
      <div className="flex items-center gap-2 px-4 py-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/15 text-primary">
          <Sparkles className="h-4 w-4" />
        </div>
        <span className="font-semibold tracking-tight">{APP_NAME}</span>
      </div>

      <div className="px-3">
        <Button
          type="button"
          variant="outline"
          className="w-full justify-start gap-2 rounded-xl border-dashed"
          onClick={onNewChat}
        >
          <MessageSquarePlus className="h-4 w-4" />
          New chat
        </Button>
      </div>

      <Separator className="my-4" />

      <div className="flex-1 px-4">
        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Current session
        </p>
        {sessionId ? (
          <button
            type="button"
            onClick={() => copy(sessionId)}
            className="group flex w-full items-center justify-between gap-2 rounded-lg border border-border bg-card/60 px-3 py-2 text-left text-xs transition-colors hover:border-primary/40"
            title="Copy full session id"
          >
            <span className="truncate font-mono text-muted-foreground group-hover:text-foreground">
              {truncateId(sessionId, 20)}
            </span>
            {copied ? (
              <Check className="h-3.5 w-3.5 shrink-0 text-success" />
            ) : (
              <Copy className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
            )}
          </button>
        ) : (
          <p className="rounded-lg border border-dashed border-border px-3 py-2 text-xs text-muted-foreground">
            No active session yet — send a message to start one.
          </p>
        )}
      </div>

      <div className="mt-auto border-t border-border px-4 py-4">
        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Backend status
        </p>
        <HealthBadge
          status={connectionStatus}
          health={health}
          className="w-full justify-start"
        />
      </div>
    </aside>
  );
}
