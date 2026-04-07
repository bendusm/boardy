import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { DragDropContext, type DropResult } from "@hello-pangea/dnd";
import { ArrowLeft, Loader2, LayoutDashboard, Users, Settings, Plus } from "lucide-react";
import { boardsApi, cardsApi, columnsApi } from "@/lib/api";
import type { BoardFull, Card } from "@/types";
import KanbanColumn from "@/components/kanban/KanbanColumn";
import BoardMembersModal from "@/components/BoardMembersModal";
import CardEditModal from "@/components/CardEditModal";
import BoardSettingsModal from "@/components/BoardSettingsModal";

export default function BoardPage() {
  const { boardId } = useParams<{ boardId: string }>();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [selectedCard, setSelectedCard] = useState<Card | null>(null);
  const [showMembers, setShowMembers] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

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

  const createColumnMutation = useMutation({
    mutationFn: ({ name, position }: { name: string; position: number }) =>
      columnsApi.create(boardId!, name, position),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["board", boardId] }),
  });

  const renameColumnMutation = useMutation({
    mutationFn: ({ columnId, name }: { columnId: string; name: string }) =>
      columnsApi.rename(boardId!, columnId, name),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["board", boardId] }),
  });

  const deleteColumnMutation = useMutation({
    mutationFn: (columnId: string) => columnsApi.delete(boardId!, columnId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["board", boardId] }),
  });

  async function handleAddCard(columnId: string, title: string) {
    await createCardMutation.mutateAsync({ columnId, title });
  }

  async function handleAddColumn() {
    const name = prompt("Enter column name:");
    if (!name?.trim()) return;
    const position = board?.columns.length ?? 0;
    await createColumnMutation.mutateAsync({ name: name.trim(), position });
  }

  async function handleRenameColumn(columnId: string, name: string) {
    await renameColumnMutation.mutateAsync({ columnId, name });
  }

  async function handleDeleteColumn(columnId: string) {
    await deleteColumnMutation.mutateAsync(columnId);
  }

  const canEdit = board?.my_role === "owner" || board?.my_role === "editor";

  function onDragEnd(result: DropResult) {
    if (!canEdit) return; // Viewers can't move cards
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
          <div className="ml-auto flex items-center gap-2">
            <button
              onClick={() => setShowMembers(true)}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-landing-secondary hover:text-landing-primary hover:bg-landing-surface-container rounded-lg transition-colors"
            >
              <Users size={18} />
              <span className="hidden sm:inline">Share</span>
            </button>
            <button
              onClick={() => setShowSettings(true)}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-landing-secondary hover:text-landing-primary hover:bg-landing-surface-container rounded-lg transition-colors"
            >
              <Settings size={18} />
            </button>
          </div>
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
                  canEdit={canEdit}
                  onAddCard={handleAddCard}
                  onCardClick={setSelectedCard}
                  onRenameColumn={handleRenameColumn}
                  onDeleteColumn={handleDeleteColumn}
                />
              ))}
            {/* Add column button */}
            {canEdit && (
              <button
                onClick={handleAddColumn}
                className="flex flex-col items-center justify-center w-80 shrink-0 min-h-[200px] bg-white/50 hover:bg-white rounded-2xl border-2 border-dashed border-landing-outline-variant/30 hover:border-landing-primary/50 transition-all group"
              >
                <div className="w-12 h-12 rounded-full bg-landing-surface-container-low group-hover:bg-landing-primary-fixed flex items-center justify-center mb-3 transition-colors">
                  <Plus size={24} className="text-landing-secondary group-hover:text-landing-primary transition-colors" />
                </div>
                <span className="text-sm font-medium text-landing-secondary group-hover:text-landing-primary transition-colors">
                  Add column
                </span>
              </button>
            )}
          </div>
        </DragDropContext>
      </main>

      {/* Card edit modal */}
      {selectedCard && (
        <CardEditModal
          card={selectedCard}
          boardId={board.id}
          myRole={board.my_role || "viewer"}
          onClose={() => setSelectedCard(null)}
        />
      )}

      {/* Members modal */}
      {showMembers && (
        <BoardMembersModal
          boardId={board.id}
          boardName={board.name}
          isOwner={board.my_role === "owner"}
          onClose={() => setShowMembers(false)}
        />
      )}

      {/* Settings modal */}
      {showSettings && (
        <BoardSettingsModal
          boardId={board.id}
          boardName={board.name}
          isOwner={board.my_role === "owner"}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  );
}
