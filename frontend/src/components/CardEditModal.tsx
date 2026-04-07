import { useState, useEffect, Fragment } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { X, Trash2, Calendar, User, Palette, Flag, Activity, Eye } from "lucide-react";
import { cardsApi, membersApi } from "@/lib/api";
import type { Card, CardColor, CardStatus, Priority, BoardMember, BoardRole } from "@/types";
import { cn } from "@/lib/utils";

function linkify(text: string) {
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  const parts = text.split(urlRegex);
  return parts.map((part, i) =>
    urlRegex.test(part) ? (
      <a key={i} href={part} target="_blank" rel="noopener noreferrer" className="text-landing-primary underline hover:text-landing-primary/80 break-all">{part}</a>
    ) : (
      <Fragment key={i}>{part}</Fragment>
    )
  );
}

interface Props {
  card: Card;
  boardId: string;
  myRole: BoardRole;
  onClose: () => void;
}

const COLORS: { value: CardColor; label: string; bg: string }[] = [
  { value: "gray", label: "Gray", bg: "bg-gray-400" },
  { value: "red", label: "Red", bg: "bg-red-500" },
  { value: "orange", label: "Orange", bg: "bg-orange-500" },
  { value: "yellow", label: "Yellow", bg: "bg-yellow-500" },
  { value: "green", label: "Green", bg: "bg-green-500" },
  { value: "blue", label: "Blue", bg: "bg-blue-500" },
  { value: "purple", label: "Purple", bg: "bg-purple-500" },
  { value: "pink", label: "Pink", bg: "bg-pink-500" },
];

const PRIORITIES: { value: Priority; label: string; color: string }[] = [
  { value: "low", label: "Low", color: "bg-slate-100 text-slate-600" },
  { value: "medium", label: "Medium", color: "bg-blue-100 text-blue-700" },
  { value: "high", label: "High", color: "bg-orange-100 text-orange-700" },
  { value: "critical", label: "Critical", color: "bg-red-100 text-red-700" },
];

const STATUSES: { value: CardStatus; label: string; color: string }[] = [
  { value: "open", label: "Open", color: "bg-gray-100 text-gray-700" },
  { value: "in_progress", label: "In Progress", color: "bg-yellow-100 text-yellow-700" },
  { value: "blocked", label: "Blocked", color: "bg-red-100 text-red-700" },
  { value: "done", label: "Done", color: "bg-green-100 text-green-700" },
];

export default function CardEditModal({ card, boardId, myRole, onClose }: Props) {
  const qc = useQueryClient();
  const [title, setTitle] = useState(card.title);
  const [description, setDescription] = useState(card.description || "");
  const [isEditing, setIsEditing] = useState(false);
  const [color, setColor] = useState<CardColor>(card.color);
  const [priority, setPriority] = useState<Priority>(card.priority);
  const [status, setStatus] = useState<CardStatus>(card.status);
  const [assigneeId, setAssigneeId] = useState<string>(card.assignee_id || "");
  const [dueDate, setDueDate] = useState(card.due_date?.split("T")[0] || "");
  const [confirmDelete, setConfirmDelete] = useState(false);

  const canEdit = myRole === "owner" || myRole === "editor";

  const { data: members = [] } = useQuery<BoardMember[]>({
    queryKey: ["board-members", boardId],
    queryFn: async () => (await membersApi.list(boardId)).data,
  });

  const updateMutation = useMutation({
    mutationFn: (data: object) => cardsApi.update(card.id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["board", boardId] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => cardsApi.delete(card.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["board", boardId] });
      onClose();
    },
  });

  function handleSave() {
    updateMutation.mutate({
      title,
      description: description || null,
      color,
      priority,
      status,
      assignee_id: assigneeId || null,
      due_date: dueDate ? `${dueDate}T00:00:00Z` : null,
    });
  }

  // Auto-save on changes (debounced effect) - only for editors/owners
  useEffect(() => {
    if (!canEdit) return;
    const timer = setTimeout(() => {
      if (
        title !== card.title ||
        description !== (card.description || "") ||
        color !== card.color ||
        priority !== card.priority ||
        status !== card.status ||
        assigneeId !== (card.assignee_id || "") ||
        dueDate !== (card.due_date?.split("T")[0] || "")
      ) {
        handleSave();
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [title, description, color, priority, status, assigneeId, dueDate, canEdit]);

  return (
    <div
      className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-3xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Color stripe */}
        {color !== "gray" && (
          <div className={cn("h-2 w-full rounded-t-3xl", COLORS.find(c => c.value === color)?.bg)} />
        )}

        <div className="p-6">
          {/* Viewer notice */}
          {!canEdit && (
            <div className="mb-4 flex items-center gap-2 px-4 py-3 bg-gray-100 rounded-xl text-sm text-gray-600">
              <Eye size={16} />
              You have view-only access to this board
            </div>
          )}

          {/* Header */}
          <div className="flex items-start justify-between mb-6">
            <input
              type="text"
              value={title}
              onChange={(e) => canEdit && setTitle(e.target.value)}
              readOnly={!canEdit}
              className={cn(
                "font-headline italic text-2xl w-full bg-transparent border-none outline-none focus:ring-0",
                !canEdit && "cursor-default"
              )}
              placeholder="Card title"
            />
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors ml-2"
            >
              <X size={20} />
            </button>
          </div>

          {/* Description */}
          <div className="mb-6">
            <label className="text-sm font-medium text-gray-500 mb-2 block">Description</label>
            {canEdit || isEditing ? (
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                onFocus={() => setIsEditing(true)}
                onBlur={() => setIsEditing(false)}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-landing-primary/30 focus:border-landing-primary"
                rows={9}
                placeholder="Add a description..."
              />
            ) : (
              <div
                className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-sm min-h-[180px] whitespace-pre-wrap break-words"
              >
                {description ? linkify(description) : <span className="text-gray-400">No description</span>}
              </div>
            )}
          </div>

          {/* Color picker */}
          <div className="mb-6">
            <label className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-2">
              <Palette size={16} /> Color
            </label>
            <div className="flex gap-2">
              {COLORS.map((c) => (
                <button
                  key={c.value}
                  onClick={() => canEdit && setColor(c.value)}
                  disabled={!canEdit}
                  className={cn(
                    "w-8 h-8 rounded-full transition-all",
                    c.bg,
                    color === c.value ? "ring-2 ring-offset-2 ring-gray-400 scale-110" : canEdit && "hover:scale-105",
                    !canEdit && "cursor-default opacity-70"
                  )}
                  title={c.label}
                />
              ))}
            </div>
          </div>

          {/* Priority */}
          <div className="mb-6">
            <label className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-2">
              <Flag size={16} /> Priority
            </label>
            <div className="flex flex-wrap gap-2">
              {PRIORITIES.map((p) => (
                <button
                  key={p.value}
                  onClick={() => canEdit && setPriority(p.value)}
                  disabled={!canEdit}
                  className={cn(
                    "px-4 py-2 rounded-full text-sm font-medium transition-all",
                    p.color,
                    priority === p.value ? "ring-2 ring-offset-1 ring-gray-400" : canEdit ? "opacity-60 hover:opacity-100" : "opacity-40",
                    !canEdit && "cursor-default"
                  )}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Status */}
          <div className="mb-6">
            <label className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-2">
              <Activity size={16} /> Status
            </label>
            <div className="flex flex-wrap gap-2">
              {STATUSES.map((s) => (
                <button
                  key={s.value}
                  onClick={() => canEdit && setStatus(s.value)}
                  disabled={!canEdit}
                  className={cn(
                    "px-4 py-2 rounded-full text-sm font-medium transition-all",
                    s.color,
                    status === s.value ? "ring-2 ring-offset-1 ring-gray-400" : canEdit ? "opacity-60 hover:opacity-100" : "opacity-40",
                    !canEdit && "cursor-default"
                  )}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          {/* Assignee */}
          <div className="mb-6">
            <label className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-2">
              <User size={16} /> Assignee
            </label>
            <select
              value={assigneeId}
              onChange={(e) => canEdit && setAssigneeId(e.target.value)}
              disabled={!canEdit}
              className={cn(
                "w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-landing-primary/30 focus:border-landing-primary",
                !canEdit && "cursor-default opacity-70"
              )}
            >
              <option value="">Unassigned</option>
              {members.map((m) => (
                <option key={m.user_id} value={m.user_id}>
                  {m.user_email}
                </option>
              ))}
            </select>
          </div>

          {/* Due date */}
          <div className="mb-6">
            <label className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-2">
              <Calendar size={16} /> Due Date
            </label>
            <input
              type="date"
              value={dueDate}
              onChange={(e) => canEdit && setDueDate(e.target.value)}
              disabled={!canEdit}
              className={cn(
                "w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-landing-primary/30 focus:border-landing-primary",
                !canEdit && "cursor-default opacity-70"
              )}
            />
          </div>

          {/* Meta info */}
          <div className="text-xs text-gray-400 mb-6 space-y-1">
            <p>Created by: {card.created_by === "claude" ? "AI Assistant" : "User"}</p>
            <p>Created: {new Date(card.created_at).toLocaleDateString("en-US", { dateStyle: "medium" })}</p>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
            {canEdit ? (
              !confirmDelete ? (
                <button
                  onClick={() => setConfirmDelete(true)}
                  className="flex items-center gap-2 px-4 py-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors text-sm"
                >
                  <Trash2 size={16} />
                  Delete
                </button>
              ) : (
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => deleteMutation.mutate()}
                    disabled={deleteMutation.isPending}
                    className="px-4 py-2 bg-red-500 text-white rounded-lg text-sm font-medium hover:bg-red-600 disabled:opacity-50"
                  >
                    Confirm Delete
                  </button>
                  <button
                    onClick={() => setConfirmDelete(false)}
                    className="px-4 py-2 text-gray-500 hover:bg-gray-100 rounded-lg text-sm"
                  >
                    Cancel
                  </button>
                </div>
              )
            ) : (
              <div />
            )}
            <button
              onClick={onClose}
              className="px-6 py-2 bg-landing-primary text-white rounded-full text-sm font-semibold hover:shadow-lg transition-all"
            >
              {canEdit ? "Done" : "Close"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
