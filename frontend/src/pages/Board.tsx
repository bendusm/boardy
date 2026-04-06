import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { DragDropContext, type DropResult } from "@hello-pangea/dnd";
import { ArrowLeft, Loader2 } from "lucide-react";
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
    mutationFn: ({ cardId, columnId, position }: { cardId: string; columnId: string; position: number }) =>
      cardsApi.move(cardId, columnId, position),
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
    if (source.droppableId === destination.droppableId && source.index === destination.index) return;

    moveMutation.mutate({
      cardId: draggableId,
      columnId: destination.droppableId,
      position: destination.index,
    });
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="animate-spin text-muted-foreground" size={32} />
      </div>
    );
  }

  if (!board) return <div className="p-8 text-center text-muted-foreground">Board not found</div>;

  return (
    <div className="min-h-screen flex flex-col bg-muted/10">
      {/* Header */}
      <header className="bg-card border-b px-6 py-3 flex items-center gap-4">
        <button
          onClick={() => navigate("/")}
          className="text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft size={20} />
        </button>
        <h1 className="text-lg font-semibold">{board.name}</h1>
      </header>

      {/* Kanban Board */}
      <main className="flex-1 overflow-x-auto p-6">
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="flex gap-4 items-start h-full">
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

      {/* Card detail modal (minimal) */}
      {selectedCard && (
        <div
          className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedCard(null)}
        >
          <div
            className="bg-card rounded-xl border shadow-xl w-full max-w-lg p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-lg font-semibold mb-2">{selectedCard.title}</h2>
            {selectedCard.description && (
              <p className="text-sm text-muted-foreground mb-4">{selectedCard.description}</p>
            )}
            <div className="flex gap-2 text-xs">
              <span className="px-2 py-1 rounded-full bg-muted">{selectedCard.priority}</span>
              <span className="px-2 py-1 rounded-full bg-muted">{selectedCard.status}</span>
              <span className="px-2 py-1 rounded-full bg-muted">by {selectedCard.created_by}</span>
            </div>
            <button
              onClick={() => setSelectedCard(null)}
              className="mt-4 px-4 py-2 rounded-md border text-sm hover:bg-muted transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
