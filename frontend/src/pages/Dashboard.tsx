import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, LogOut, LayoutDashboard, Loader2, LayoutGrid } from "lucide-react";
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
    <div className="min-h-screen bg-landing-background font-body">
      {/* Header */}
      <header className="w-full border-b border-landing-outline-variant/20 bg-white/70 backdrop-blur-md sticky top-0 z-50">
        <nav className="flex justify-between items-center max-w-7xl mx-auto px-6 md:px-12 py-5">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-landing-primary rounded-lg flex items-center justify-center">
              <LayoutDashboard className="w-5 h-5 text-white" />
            </div>
            <div className="font-headline italic text-2xl font-bold text-landing-on-background">
              Boardy
            </div>
          </Link>
          <div className="flex items-center gap-4">
            <span className="text-sm text-landing-secondary hidden sm:block">
              {user?.email}
            </span>
            <button
              onClick={() => {
                logout();
                navigate("/");
              }}
              className="flex items-center gap-2 px-4 py-2 rounded-full border border-landing-outline-variant hover:border-landing-primary/50 hover:text-landing-primary transition-all text-sm font-medium text-landing-secondary"
            >
              <LogOut size={16} />
              <span className="hidden sm:inline">Sign out</span>
            </button>
          </div>
        </nav>
      </header>

      {/* Main */}
      <main className="max-w-5xl mx-auto px-6 md:px-12 py-12">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-headline italic text-3xl md:text-4xl mb-2">
              Your boards
            </h1>
            <p className="text-landing-secondary">
              Manage your projects with AI assistance
            </p>
          </div>
          <button
            onClick={() => setCreating(true)}
            className="flex items-center gap-2 px-5 py-3 bg-landing-primary text-white rounded-full text-sm font-bold hover:shadow-lg hover:shadow-landing-primary/20 transition-all"
          >
            <Plus size={18} /> New board
          </button>
        </div>

        {/* New board form */}
        {creating && (
          <div className="mb-8 bg-white rounded-2xl shadow-startup border border-landing-outline-variant/10 p-6">
            <h3 className="font-semibold text-landing-on-background mb-4">
              Create new board
            </h3>
            <form onSubmit={handleCreate} className="flex gap-3">
              <input
                autoFocus
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Board name"
                className="flex-1 px-4 py-3 rounded-xl border border-landing-outline-variant/30 bg-landing-surface-container-low text-sm focus:outline-none focus:ring-2 focus:ring-landing-primary/30 focus:border-landing-primary transition-all"
              />
              <button
                type="submit"
                disabled={createMutation.isPending}
                className="px-6 py-3 bg-landing-primary text-white rounded-full text-sm font-bold disabled:opacity-50 hover:shadow-lg hover:shadow-landing-primary/20 transition-all flex items-center gap-2"
              >
                {createMutation.isPending ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  "Create"
                )}
              </button>
              <button
                type="button"
                onClick={() => setCreating(false)}
                className="px-5 py-3 rounded-full border border-landing-outline-variant text-sm font-medium text-landing-secondary hover:border-landing-primary/50 transition-all"
              >
                Cancel
              </button>
            </form>
          </div>
        )}

        {/* Boards grid */}
        {isLoading ? (
          <div className="flex justify-center py-20">
            <Loader2
              className="animate-spin text-landing-primary"
              size={32}
            />
          </div>
        ) : boards.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-20 h-20 rounded-2xl bg-landing-surface-container-low flex items-center justify-center mx-auto mb-6">
              <LayoutGrid size={40} className="text-landing-outline" />
            </div>
            <h3 className="font-headline italic text-2xl mb-2">No boards yet</h3>
            <p className="text-landing-secondary mb-6">
              Create your first board to get started
            </p>
            <button
              onClick={() => setCreating(true)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-landing-primary text-white rounded-full text-sm font-bold hover:shadow-lg hover:shadow-landing-primary/20 transition-all"
            >
              <Plus size={18} /> Create board
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {boards.map((board) => (
              <button
                key={board.id}
                onClick={() => navigate(`/boards/${board.id}`)}
                className="text-left p-6 bg-white rounded-2xl shadow-startup border border-landing-outline-variant/10 hover:shadow-startup-hover hover:border-landing-primary/20 transition-all group"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-landing-primary-fixed/50 flex items-center justify-center">
                    <LayoutGrid
                      size={20}
                      className="text-landing-primary"
                    />
                  </div>
                </div>
                <h3 className="font-semibold text-lg text-landing-on-background group-hover:text-landing-primary transition-colors mb-2">
                  {board.name}
                </h3>
                <p className="text-xs text-landing-secondary">
                  Created {new Date(board.created_at).toLocaleDateString()}
                </p>
              </button>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
