import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, LogOut, LayoutGrid, Loader2 } from "lucide-react";
import { boardsApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import type { Board } from "@/types";

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const qc = useQueryClient();
  const [newName, setNewName] = useState("");
  const [creating, setCreating] = useState(false);

  const { data: boards = [], isLoading } = useQuery<Board[]>({
    queryKey: ["boards"],
    queryFn: async () => (await boardsApi.list()).data,
  });

  const createMutation = useMutation({
    mutationFn: (name: string) => boardsApi.create(name),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["boards"] });
      setNewName("");
      setCreating(false);
    },
  });

  function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (newName.trim()) createMutation.mutate(newName.trim());
  }

  return (
    <div className="min-h-screen bg-muted/20">
      {/* Header */}
      <header className="bg-card border-b px-6 py-3 flex items-center justify-between">
        <h1 className="text-xl font-bold text-primary">Boardy</h1>
        <div className="flex items-center gap-3">
          <span className="text-sm text-muted-foreground">{user?.email}</span>
          <button
            onClick={() => { logout(); navigate("/login"); }}
            className="p-1.5 rounded hover:bg-muted transition-colors text-muted-foreground"
            title="Sign out"
          >
            <LogOut size={16} />
          </button>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold">Your boards</h2>
          <button
            onClick={() => setCreating(true)}
            className="flex items-center gap-2 px-3 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
          >
            <Plus size={16} /> New board
          </button>
        </div>

        {/* New board form */}
        {creating && (
          <form onSubmit={handleCreate} className="mb-4 flex gap-2">
            <input
              autoFocus
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Board name"
              className="flex-1 px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium disabled:opacity-50"
            >
              {createMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : "Create"}
            </button>
            <button
              type="button"
              onClick={() => setCreating(false)}
              className="px-3 py-2 rounded-md border text-sm hover:bg-muted transition-colors"
            >
              Cancel
            </button>
          </form>
        )}

        {/* Boards grid */}
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="animate-spin text-muted-foreground" size={24} />
          </div>
        ) : boards.length === 0 ? (
          <div className="text-center py-16 text-muted-foreground">
            <LayoutGrid size={40} className="mx-auto mb-3 opacity-30" />
            <p className="text-lg">No boards yet</p>
            <p className="text-sm mt-1">Create one to get started</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {boards.map((board) => (
              <button
                key={board.id}
                onClick={() => navigate(`/boards/${board.id}`)}
                className="text-left p-5 bg-card border rounded-xl hover:shadow-md hover:border-primary/30 transition-all group"
              >
                <div className="flex items-start justify-between">
                  <h3 className="font-semibold group-hover:text-primary transition-colors">
                    {board.name}
                  </h3>
                  <LayoutGrid size={16} className="text-muted-foreground mt-0.5" />
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  {new Date(board.created_at).toLocaleDateString()}
                </p>
              </button>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
