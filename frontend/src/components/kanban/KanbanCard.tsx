import type { Card } from "@/types";
import { cn } from "@/lib/utils";
import { Bot, User } from "lucide-react";

interface Props {
  card: Card;
  isDragging: boolean;
  onClick: () => void;
}

const PRIORITY_BADGE: Record<string, string> = {
  low: "bg-slate-100 text-slate-500",
  medium: "bg-blue-100 text-blue-600",
  high: "bg-orange-100 text-orange-600",
  critical: "bg-red-100 text-red-600",
};

const STATUS_BADGE: Record<string, string> = {
  open: "bg-gray-100 text-gray-500",
  in_progress: "bg-yellow-100 text-yellow-700",
  blocked: "bg-red-100 text-red-600",
  done: "bg-green-100 text-green-700",
};

export default function KanbanCard({ card, isDragging, onClick }: Props) {
  return (
    <div
      onClick={onClick}
      className={cn(
        "bg-card border rounded-lg p-3 cursor-pointer hover:shadow-sm transition-all select-none",
        isDragging && "shadow-lg rotate-1 scale-105 border-primary/40"
      )}
    >
      <p className="text-sm font-medium leading-snug">{card.title}</p>

      {card.description && (
        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{card.description}</p>
      )}

      <div className="flex items-center gap-1.5 mt-2 flex-wrap">
        <span className={cn("text-xs rounded-full px-2 py-0.5 font-medium", PRIORITY_BADGE[card.priority])}>
          {card.priority}
        </span>
        {card.status !== "open" && (
          <span className={cn("text-xs rounded-full px-2 py-0.5 font-medium", STATUS_BADGE[card.status])}>
            {card.status.replace("_", " ")}
          </span>
        )}
        <div className="ml-auto text-muted-foreground" title={card.created_by === "claude" ? "Created by Claude" : "Created by user"}>
          {card.created_by === "claude" ? <Bot size={12} /> : <User size={12} />}
        </div>
      </div>
    </div>
  );
}
