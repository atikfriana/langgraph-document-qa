"use client";

import { useState } from "react";
import { ChevronDown, Library } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { SourceCard } from "./SourceCard";
import type { ChatSource } from "@/types/chat";

interface SourcesPanelProps {
  sources: ChatSource[];
}

export function SourcesPanel({ sources }: SourcesPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (sources.length === 0) return null;

  return (
    <div className="mt-3 border-t border-border/60 pt-3">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground"
      >
        <Library className="h-3.5 w-3.5" />
        <span>
          {sources.length} source{sources.length === 1 ? "" : "s"} from the document
        </span>
        <ChevronDown
          className={cn(
            "h-3.5 w-3.5 transition-transform",
            isOpen && "rotate-180"
          )}
        />
      </button>

      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="mt-2 flex flex-wrap gap-2">
              {sources.map((source) => (
                <SourceCard
                  key={`${source.source}-${source.chunk_id}`}
                  source={source}
                />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
