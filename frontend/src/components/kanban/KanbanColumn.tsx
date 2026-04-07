import { useState, useRef, useEffect } from "react";
import { Droppable, Draggable } from "@hello-pangea/dnd";
import { Plus, Loader2, MoreVertical, Pencil, Trash2 } from "lucide-react";
import type { Column, Card } from "@/types";
import KanbanCard from "./KanbanCard";

interface Props {
  column: Column & { cards: Card[] };
  boardId: string;
  canEdit: boolean;
  onAddCard: (columnId: string, title: string) => Promise<void>;
  onCardClick: (card: Card) => void;
  onRenameColumn: (columnId: string, name: string) => Promise<void>;
  onDeleteColumn: (columnId: string) => Promise<void>;
}

export default function KanbanColumn({
  column,
  canEdit,
  onAddCard,
  onCardClick,
  onRenameColumn,
  onDeleteColumn,
}: Props) {
  const [adding, setAdding] = useState(false);
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [renaming, setRenaming] = useState(false);
  const [newName, setNewName] = useState(column.name);
  const [renamingLoading, setRenamingLoading] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setShowMenu(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setLoading(true);
    await onAddCard(column.id, title.trim());
    setTitle("");
    setAdding(false);
    setLoading(false);
  }

  async function handleRename(e: React.FormEvent) {
    e.preventDefault();
    if (!newName.trim() || newName.trim() === column.name) {
      setRenaming(false);
      setNewName(column.name);
      return;
    }
    setRenamingLoading(true);
    await onRenameColumn(column.id, newName.trim());
    setRenaming(false);
    setRenamingLoading(false);
  }

  async function handleDelete() {
    if (!confirm(`Delete column "${column.name}" and all its cards?`)) return;
    setShowMenu(false);
    await onDeleteColumn(column.id);
  }

  return (
    <div className="flex flex-col w-80 shrink-0 bg-white rounded-2xl shadow-startup border border-landing-outline-variant/10">
      {/* Column header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-landing-outline-variant/20">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {renaming ? (
            <form onSubmit={handleRename} className="flex-1">
              <input
                autoFocus
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                onBlur={handleRename}
                disabled={renamingLoading}
                className="w-full px-2 py-1 font-semibold text-landing-on-background bg-landing-surface-container-low border border-landing-outline-variant/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-landing-primary/30"
              />
            </form>
          ) : (
            <h3 className="font-semibold text-landing-on-background truncate">
              {column.name}
            </h3>
          )}
          <span className="text-xs font-medium text-landing-secondary bg-landing-surface-container-low rounded-full px-2.5 py-1 shrink-0">
            {column.cards.length}
          </span>
        </div>
        {canEdit && (
          <div className="flex items-center gap-1 ml-2">
            <button
              onClick={() => setAdding(true)}
              className="w-8 h-8 rounded-lg flex items-center justify-center text-landing-secondary hover:bg-landing-primary-fixed hover:text-landing-primary transition-all"
              title="Add card"
            >
              <Plus size={18} />
            </button>
            <div className="relative" ref={menuRef}>
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-landing-secondary hover:bg-landing-surface-container transition-all"
                title="Column options"
              >
                <MoreVertical size={18} />
              </button>
              {showMenu && (
                <div className="absolute right-0 top-full mt-1 w-40 bg-white rounded-xl shadow-lg border border-landing-outline-variant/20 py-1 z-50">
                  <button
                    onClick={() => {
                      setShowMenu(false);
                      setRenaming(true);
                    }}
                    className="w-full flex items-center gap-2 px-4 py-2 text-sm text-landing-on-background hover:bg-landing-surface-container transition-colors"
                  >
                    <Pencil size={16} />
                    Rename
                  </button>
                  <button
                    onClick={handleDelete}
                    className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <Trash2 size={16} />
                    Delete
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
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
      {canEdit && adding ? (
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
