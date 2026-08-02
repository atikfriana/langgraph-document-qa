"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sidebar } from "./Sidebar";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { useChat } from "@/hooks/useChat";
import { useHealthStatus } from "@/hooks/useHealthStatus";

export function MainLayout() {
  const chat = useChat();
  const { status: connectionStatus, health } = useHealthStatus();
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  return (
    <div className="flex h-dvh w-full overflow-hidden bg-background">
      {/* Desktop sidebar */}
      <div className="hidden sm:block">
        <Sidebar
          sessionId={chat.sessionId}
          connectionStatus={connectionStatus}
          health={health}
          onNewChat={chat.clearConversation}
        />
      </div>

      {/* Mobile sidebar (overlay drawer) */}
      <AnimatePresence>
        {isMobileSidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm sm:hidden"
              onClick={() => setIsMobileSidebarOpen(false)}
            />
            <motion.div
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "tween", duration: 0.2 }}
              className="fixed inset-y-0 left-0 z-50 sm:hidden"
            >
              <div className="relative h-full">
                <Sidebar
                  sessionId={chat.sessionId}
                  connectionStatus={connectionStatus}
                  health={health}
                  onNewChat={() => {
                    chat.clearConversation();
                    setIsMobileSidebarOpen(false);
                  }}
                />
                <Button
                  type="button"
                  size="icon"
                  variant="ghost"
                  className="absolute right-2 top-4"
                  onClick={() => setIsMobileSidebarOpen(false)}
                  aria-label="Close sidebar"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      <div className="relative flex min-h-0 min-w-0 flex-1 flex-col">
        <Button
          type="button"
          size="icon"
          variant="ghost"
          className="absolute left-3 top-3 z-30 sm:hidden"
          onClick={() => setIsMobileSidebarOpen(true)}
          aria-label="Open sidebar"
        >
          <Menu className="h-5 w-5" />
        </Button>

        <ChatWindow
          messages={chat.messages}
          isSending={chat.isSending}
          hasFailedMessage={chat.hasFailedMessage}
          connectionStatus={connectionStatus}
          onSend={chat.sendMessage}
          onRetry={chat.retryLastMessage}
        />
      </div>
    </div>
  );
}
