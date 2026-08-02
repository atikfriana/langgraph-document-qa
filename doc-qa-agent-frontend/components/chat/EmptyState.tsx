"use client";

import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import { APP_NAME, APP_TAGLINE, SUGGESTED_PROMPTS } from "@/lib/constants";

interface EmptyStateProps {
  onSelectPrompt: (prompt: string) => void;
}

export function EmptyState({ onSelectPrompt }: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex h-full flex-col items-center justify-center px-6 text-center"
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/15 text-primary">
        <Sparkles className="h-7 w-7" />
      </div>
      <h1 className="mt-5 text-xl font-semibold">{APP_NAME}</h1>
      <p className="mt-1.5 max-w-sm text-sm text-muted-foreground">
        {APP_TAGLINE} Ask a question below — I'll search the document and, if
        needed, the web.
      </p>

      <div className="mt-8 grid w-full max-w-lg grid-cols-1 gap-2 sm:grid-cols-2">
        {SUGGESTED_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => onSelectPrompt(prompt)}
            className="rounded-xl border border-border bg-card/60 px-4 py-3 text-left text-sm text-muted-foreground shadow-sm transition-colors hover:border-primary/40 hover:bg-card hover:text-foreground"
          >
            {prompt}
          </button>
        ))}
      </div>
    </motion.div>
  );
}
