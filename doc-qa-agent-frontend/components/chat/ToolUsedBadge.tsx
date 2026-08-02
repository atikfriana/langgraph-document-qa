import { Globe, BookOpenText } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface ToolUsedBadgeProps {
  toolUsed: boolean;
}

export function ToolUsedBadge({ toolUsed }: ToolUsedBadgeProps) {
  if (toolUsed) {
    return (
      <Badge variant="secondary" className="gap-1">
        <Globe className="h-3 w-3" />
        Web search used
      </Badge>
    );
  }

  return (
    <Badge variant="muted" className="gap-1">
      <BookOpenText className="h-3 w-3" />
      Answered from document
    </Badge>
  );
}
