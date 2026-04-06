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

export default function KanbanColumn({
  column,
  onAddCard,
  onCardClick,
}: Props) {
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
    <div className="flex flex-col w-80 shrink-0 bg-white rounded-2xl shadow-startup border border-landing-outline-variant/10">
      {/* Column header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-landing-outline-variant/20">
        <div className="flex items-center gap-3">
          <h3 className="font-semibold text-landing-on-background">
            {column.name}
          </h3>
          <span className="text-xs font-medium text-landing-secondary bg-landing-surface-container-low rounded-full px-2.5 py-1">
            {column.cards.length}
          </span>
        </div>
        <button
          onClick={() => setAdding(true)}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-landing-secondary hover:bg-landing-primary-fixed hover:text-landing-primary transition-all"
          title="Add card"
        >
          <Plus size={18} />
        </button>
      </div>

      {/* Cards */}
      <Droppable droppableId={column.id}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`flex-1 p-3 space-y-3 min-h-[100px] transition-colors rounded-b-2xl ${
              snapshot.isDraggingOver ? "bg-landing-primary-fixed/30" : ""
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
        <form
          onSubmit={handleAdd}
          className="p-3 border-t border-landing-outline-variant/20 space-y-3"
        >
          <textarea
            autoFocus
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Card title..."
            rows={2}
            className="w-full px-4 py-3 rounded-xl border border-landing-outline-variant/30 bg-landing-surface-container-low text-sm resize-none focus:outline-none focus:ring-2 focus:ring-landing-primary/30 focus:border-landing-primary transition-all"
          />
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-2.5 bg-landing-primary text-white rounded-full text-sm font-semibold disabled:opacity-50 hover:shadow-lg hover:shadow-landing-primary/20 transition-all flex items-center justify-center"
            >
              {loading ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                "Add card"
              )}
            </button>
            <button
              type="button"
              onClick={() => {
                setAdding(false);
                setTitle("");
              }}
              className="px-4 py-2.5 rounded-full border border-landing-outline-variant text-sm font-medium text-landing-secondary hover:border-landing-primary/50 transition-all"
            >
              Cancel
            </button>
          </div>
        </form>
      ) : null}
    </div>
  );
}
