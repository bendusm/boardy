import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { DragDropContext, type DropResult } from "@hello-pangea/dnd";
import { ArrowLeft, Loader2, LayoutDashboard } from "lucide-react";
import { boardsApi, cardsApi } from "@/lib/api";
import type { BoardFull, Card } from "@/types";
import KanbanColumn from "@/components/kanban/KanbanColumn";

export default function BoardPage() {
  const { boardId } = useParams<{ boardId: string }>();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [selectedCard, setSelectedCard] = useState<Card | null>(null);

  const { data: board, isLoading } = useQuery<BoardFull>({
    queryKey: ["board", boardId],
    queryFn: async () => (await boardsApi.get(boardId!)).data,
    enabled: !!boardId,
  });

  const moveMutation = useMutation({
    mutationFn: ({
      cardId,
      columnId,
      position,
    }: {
      cardId: string;
      columnId: string;
      position: number;
    }) => cardsApi.move(cardId, columnId, position),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["board", boardId] }),
  });

  const createCardMutation = useMutation({
    mutationFn: ({ columnId, title }: { columnId: string; title: string }) =>
      cardsApi.create(boardId!, columnId, { title }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["board", boardId] }),
  });

  async function handleAddCard(columnId: string, title: string) {
    await createCardMutation.mutateAsync({ columnId, title });
  }

  function onDragEnd(result: DropResult) {
    const { source, destination, draggableId } = result;
    if (!destination) return;
    if (
      source.droppableId === destination.droppableId &&
      source.index === destination.index
    )
      return;

    moveMutation.mutate({
      cardId: draggableId,
      columnId: destination.droppableId,
      position: destination.index,
    });
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-landing-background">
        <Loader2 className="animate-spin text-landing-primary" size={32} />
      </div>
    );
  }

  if (!board)
    return (
      <div className="min-h-screen flex items-center justify-center bg-landing-background font-body">
        <div className="text-center">
          <h2 className="font-headline italic text-2xl mb-2">Board not found</h2>
          <p className="text-landing-secondary mb-6">
            The board you're looking for doesn't exist
          </p>
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 px-6 py-3 bg-landing-primary text-white rounded-full text-sm font-bold hover:shadow-lg hover:shadow-landing-primary/20 transition-all"
          >
            <ArrowLeft size={18} /> Back to dashboard
          </Link>
        </div>
      </div>
    );

  return (
    <div className="min-h-screen flex flex-col bg-landing-background font-body">
      {/* Header */}
      <header className="w-full border-b border-landing-outline-variant/20 bg-white/70 backdrop-blur-md sticky top-0 z-50">
        <nav className="flex items-center gap-4 max-w-full mx-auto px-6 md:px-12 py-5">
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-2 text-landing-secondary hover:text-landing-primary transition-colors"
          >
            <ArrowLeft size={20} />
          </button>
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-landing-primary rounded-lg flex items-center justify-center">
              <LayoutDashboard className="w-5 h-5 text-white" />
            </div>
            <div className="font-headline italic text-xl font-bold text-landing-on-background hidden sm:block">
              Boardy
            </div>
          </Link>
          <div className="h-6 w-px bg-landing-outline-variant/30 mx-2"></div>
          <h1 className="text-lg font-semibold text-landing-on-background truncate">
            {board.name}
          </h1>
        </nav>
      </header>

      {/* Kanban Board */}
      <main className="flex-1 overflow-x-auto p-6">
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="flex gap-5 items-start h-full min-h-[calc(100vh-120px)]">
            {board.columns
              .sort((a, b) => a.position - b.position)
              .map((col) => (
                <KanbanColumn
                  key={col.id}
                  column={col}
                  boardId={board.id}
                  onAddCard={handleAddCard}
                  onCardClick={setSelectedCard}
                />
              ))}
          </div>
        </DragDropContext>
      </main>

      {/* Card detail modal */}
      {selectedCard && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedCard(null)}
        >
          <div
            className="bg-white rounded-3xl shadow-2xl w-full max-w-lg p-8"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="font-headline italic text-2xl mb-4">
              {selectedCard.title}
            </h2>
            {selectedCard.description && (
              <p className="text-landing-secondary mb-6">
                {selectedCard.description}
              </p>
            )}
            <div className="flex flex-wrap gap-2 mb-6">
              <span className="px-3 py-1.5 rounded-full bg-landing-surface-container-low text-xs font-medium text-landing-secondary">
                {selectedCard.priority}
              </span>
              <span className="px-3 py-1.5 rounded-full bg-landing-surface-container-low text-xs font-medium text-landing-secondary">
                {selectedCard.status}
              </span>
              <span className="px-3 py-1.5 rounded-full bg-landing-primary-fixed text-xs font-medium text-landing-on-primary-fixed-variant">
                by {selectedCard.created_by}
              </span>
            </div>
            <button
              onClick={() => setSelectedCard(null)}
              className="w-full py-3 px-6 rounded-full border border-landing-outline-variant text-sm font-semibold text-landing-secondary hover:border-landing-primary/50 hover:text-landing-primary transition-all"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
