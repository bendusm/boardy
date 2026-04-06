import { useState } from "react";
import { Droppable, Draggable } from "@hello-pangea/dnd";
import { Plus, Loader2 } from "lucide-react";
import type { Column, Card } from "@/types";
import KanbanCard from "./KanbanCard";

interface Props {
  column: Column & { cards: Card[] };
  boardId: string;
  onAddCard: (columnId: string, title: string) => Promise<void>;
  onCardClick: (card: Card) => void;
}

const PRIORITY_COLORS: Record<string, string> = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-blue-100 text-blue-700",
  high: "bg-orange-100 text-orange-700",
  critical: "bg-red-100 text-red-700",
};

export default function KanbanColumn({ column, boardId, onAddCard, onCardClick }: Props) {
  const [adding, setAdding] = useState(false);
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setLoading(true);
    await onAddCard(column.id, title.trim());
    setTitle("");
    setAdding(false);
    setLoading(false);
  }

  return (
    <div className="flex flex-col w-72 shrink-0 bg-muted/40 rounded-xl border">
      {/* Column header */}
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold text-sm">{column.name}</h3>
          <span className="text-xs text-muted-foreground bg-muted rounded-full px-2 py-0.5">
            {column.cards.length}
          </span>
        </div>
        <button
          onClick={() => setAdding(true)}
          className="text-muted-foreground hover:text-foreground transition-colors"
          title="Add card"
        >
          <Plus size={16} />
        </button>
      </div>

      {/* Cards */}
      <Droppable droppableId={column.id}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`flex-1 p-2 space-y-2 min-h-[60px] transition-colors ${
              snapshot.isDraggingOver ? "bg-primary/5" : ""
            }`}
          >
            {column.cards.map((card, index) => (
              <Draggable key={card.id} draggableId={card.id} index={index}>
                {(prov, snap) => (
                  <div
                    ref={prov.innerRef}
                    {...prov.draggableProps}
                    {...prov.dragHandleProps}
                  >
                    <KanbanCard
                      card={card}
                      isDragging={snap.isDragging}
                      onClick={() => onCardClick(card)}
                    />
                  </div>
                )}
              </Draggable>
            ))}
            {provided.placeholder}
          </div>
        )}
      </Droppable>

      {/* Add card form */}
      {adding ? (
        <form onSubmit={handleAdd} className="p-2 border-t space-y-2">
          <textarea
            autoFocus
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Card title…"
            rows={2}
            className="w-full px-2 py-1.5 rounded border bg-background text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-1.5 bg-primary text-primary-foreground rounded text-xs font-medium disabled:opacity-50"
            >
              {loading ? <Loader2 size={12} className="animate-spin mx-auto" /> : "Add card"}
            </button>
            <button
              type="button"
              onClick={() => { setAdding(false); setTitle(""); }}
              className="px-2 py-1.5 rounded border text-xs hover:bg-muted transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      ) : null}
    </div>
  );
}
