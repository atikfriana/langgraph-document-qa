"use client";

import { AnimatePresence, motion } from "framer-motion";
import { WifiOff, AlertTriangle } from "lucide-react";
import type { ConnectionStatus } from "@/types/health";

interface ConnectionBannerProps {
  status: ConnectionStatus;
}

export function ConnectionBanner({ status }: ConnectionBannerProps) {
  const visible = status === "offline" || status === "degraded";

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.2 }}
          className="overflow-hidden"
        >
          <div
            className={
              status === "offline"
                ? "flex items-center gap-2 border-b border-destructive/30 bg-destructive/10 px-4 py-2 text-xs text-destructive"
                : "flex items-center gap-2 border-b border-amber-500/30 bg-amber-500/10 px-4 py-2 text-xs text-amber-500"
            }
          >
            {status === "offline" ? (
              <WifiOff className="h-3.5 w-3.5 shrink-0" />
            ) : (
              <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
            )}
            <span>
              {status === "offline"
                ? "Backend unavailable — unable to reach the API server. Retrying automatically…"
                : "Backend is starting up — the document index isn't ready yet. Answers may fail until it finishes loading."}
            </span>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
