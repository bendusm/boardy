import type { Card } from "@/types";
import { cn } from "@/lib/utils";
import { Bot, User } from "lucide-react";

interface Props {
  card: Card;
  isDragging: boolean;
  onClick: () => void;
}

const PRIORITY_BADGE: Record<string, string> = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-blue-100 text-blue-700",
  high: "bg-orange-100 text-orange-700",
  critical: "bg-red-100 text-red-700",
};

const STATUS_BADGE: Record<string, string> = {
  open: "bg-landing-surface-container-low text-landing-secondary",
  in_progress: "bg-yellow-100 text-yellow-700",
  blocked: "bg-red-100 text-red-700",
  done: "bg-green-100 text-green-700",
};

export default function KanbanCard({ card, isDragging, onClick }: Props) {
  return (
    <div
      onClick={onClick}
      className={cn(
        "bg-landing-surface rounded-xl p-4 cursor-pointer border border-landing-outline-variant/20 hover:shadow-md hover:border-landing-primary/20 transition-all select-none",
        isDragging &&
          "shadow-xl rotate-2 scale-105 border-landing-primary/40 bg-white"
      )}
    >
      <p className="text-sm font-medium leading-snug text-landing-on-background">
        {card.title}
      </p>

      {card.description && (
        <p className="text-xs text-landing-secondary mt-2 line-clamp-2">
          {card.description}
        </p>
      )}

      <div className="flex items-center gap-2 mt-3 flex-wrap">
        <span
          className={cn(
            "text-xs rounded-full px-2.5 py-1 font-medium",
            PRIORITY_BADGE[card.priority]
          )}
        >
          {card.priority}
        </span>
        {card.status !== "open" && (
          <span
            className={cn(
              "text-xs rounded-full px-2.5 py-1 font-medium",
              STATUS_BADGE[card.status]
            )}
          >
            {card.status.replace("_", " ")}
          </span>
        )}
        <div
          className={cn(
            "ml-auto w-6 h-6 rounded-full flex items-center justify-center",
            card.created_by === "claude"
              ? "bg-landing-primary-fixed text-landing-primary"
              : "bg-landing-surface-container-low text-landing-secondary"
          )}
          title={
            card.created_by === "claude"
              ? "Created by AI"
              : "Created by user"
          }
        >
          {card.created_by === "claude" ? <Bot size={12} /> : <User size={12} />}
        </div>
      </div>
    </div>
  );
}
