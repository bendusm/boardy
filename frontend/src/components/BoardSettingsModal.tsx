import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { X, Trash2, Loader2 } from "lucide-react";
import { boardsApi } from "@/lib/api";

interface Props {
  boardId: string;
  boardName: string;
  isOwner: boolean;
  onClose: () => void;
}

export default function BoardSettingsModal({ boardId, boardName, isOwner, onClose }: Props) {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [name, setName] = useState(boardName);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState("");

  const renameMutation = useMutation({
    mutationFn: (newName: string) => boardsApi.rename(boardId, newName),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["board", boardId] });
      qc.invalidateQueries({ queryKey: ["boards"] });
      onClose();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => boardsApi.delete(boardId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["boards"] });
      navigate("/dashboard");
    },
  });

  function handleRename(e: React.FormEvent) {
    e.preventDefault();
    if (name.trim() && name !== boardName) {
      renameMutation.mutate(name.trim());
    }
  }

  function handleDelete() {
    if (deleteConfirmText === boardName) {
      deleteMutation.mutate();
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-3xl shadow-2xl w-full max-w-md"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-headline italic text-2xl">Board Settings</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          {/* Rename section */}
          {isOwner && (
            <div className="mb-8">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Board Name</h3>
              <form onSubmit={handleRename} className="flex gap-2">
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="flex-1 px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-landing-primary/30 focus:border-landing-primary"
                  placeholder="Board name"
                />
                <button
                  type="submit"
                  disabled={!name.trim() || name === boardName || renameMutation.isPending}
                  className="px-5 py-3 bg-landing-primary text-white rounded-xl text-sm font-medium disabled:opacity-50 hover:shadow-lg transition-all"
                >
                  {renameMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : "Save"}
                </button>
              </form>
            </div>
          )}

          {/* Delete section - only for owners */}
          {isOwner && (
            <div className="pt-6 border-t border-gray-100">
              <h3 className="text-sm font-medium text-red-600 mb-3 flex items-center gap-2">
                <Trash2 size={16} />
                Danger Zone
              </h3>

              {!confirmDelete ? (
                <button
                  onClick={() => setConfirmDelete(true)}
                  className="w-full px-4 py-3 border-2 border-red-200 text-red-600 rounded-xl text-sm font-medium hover:bg-red-50 transition-colors"
                >
                  Delete this board
                </button>
              ) : (
                <div className="bg-red-50 rounded-xl p-4 border border-red-200">
                  <p className="text-sm text-red-700 mb-3">
                    This will permanently delete <strong>{boardName}</strong> and all its cards.
                    Type the board name to confirm:
                  </p>
                  <input
                    type="text"
                    value={deleteConfirmText}
                    onChange={(e) => setDeleteConfirmText(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-red-300 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-red-500/30"
                    placeholder={boardName}
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={handleDelete}
                      disabled={deleteConfirmText !== boardName || deleteMutation.isPending}
                      className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium disabled:opacity-50 hover:bg-red-700 transition-colors flex items-center justify-center gap-2"
                    >
                      {deleteMutation.isPending && <Loader2 size={14} className="animate-spin" />}
                      Delete Board
                    </button>
                    <button
                      onClick={() => {
                        setConfirmDelete(false);
                        setDeleteConfirmText("");
                      }}
                      className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg text-sm"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {!isOwner && (
            <p className="text-sm text-gray-500 text-center py-4">
              Only board owners can modify settings
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
