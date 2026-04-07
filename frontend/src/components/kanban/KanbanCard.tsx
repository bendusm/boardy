import type { Card, CardColor } from "@/types";
import { cn } from "@/lib/utils";
import { Bot, User, Calendar, Tag } from "lucide-react";

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

const COLOR_STRIPE: Record<CardColor, string> = {
  gray: "bg-gray-400",
  red: "bg-red-500",
  orange: "bg-orange-500",
  yellow: "bg-yellow-500",
  green: "bg-green-500",
  blue: "bg-blue-500",
  purple: "bg-purple-500",
  pink: "bg-pink-500",
};

export default function KanbanCard({ card, isDragging, onClick }: Props) {
  const formatDueDate = (date: string) => {
    const d = new Date(date);
    return d.toLocaleDateString("en-US", { day: "numeric", month: "short" });
  };

  return (
    <div
      onClick={onClick}
      className={cn(
        "bg-landing-surface rounded-xl cursor-pointer border border-landing-outline-variant/20 hover:shadow-md hover:border-landing-primary/20 transition-all select-none overflow-hidden",
        isDragging &&
          "shadow-xl rotate-2 scale-105 border-landing-primary/40 bg-white"
      )}
    >
      {/* Color stripe at top */}
      {card.color && card.color !== "gray" && (
        <div className={cn("h-1.5 w-full", COLOR_STRIPE[card.color])} />
      )}

      <div className="p-4">
        <p className="text-sm font-medium leading-snug text-landing-on-background">
          {card.title}
        </p>

        {card.description && (
          <p className="text-xs text-landing-secondary mt-2 line-clamp-2">
            {card.description}
          </p>
        )}

        {/* Labels */}
        {card.labels && card.labels.length > 0 && (
          <div className="flex items-center gap-1.5 mt-2 flex-wrap">
            {card.labels.slice(0, 3).map((label, i) => (
              <span
                key={i}
                className="text-[10px] bg-landing-surface-container-low text-landing-secondary px-2 py-0.5 rounded-full flex items-center gap-1"
              >
                <Tag size={8} />
                {label}
              </span>
            ))}
            {card.labels.length > 3 && (
              <span className="text-[10px] text-landing-secondary">
                +{card.labels.length - 3}
              </span>
            )}
          </div>
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

          {/* Due date */}
          {card.due_date && (
            <span className="text-[10px] text-landing-secondary flex items-center gap-1">
              <Calendar size={10} />
              {formatDueDate(card.due_date)}
            </span>
          )}

          <div className="ml-auto flex items-center gap-1.5">
            {/* Assignee */}
            {card.assignee_name && (
              <span
                className="text-[10px] text-landing-secondary truncate max-w-[60px]"
                title={card.assignee_name}
              >
                {card.assignee_name}
              </span>
            )}

            {/* Created by indicator */}
            <div
              className={cn(
                "w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0",
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
      </div>
    </div>
  );
}
