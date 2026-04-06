import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { X, UserPlus, Trash2, Clock } from "lucide-react";
import { membersApi, invitesApi } from "@/lib/api";
import type { BoardMember, BoardInvite, BoardRole } from "@/types";

interface Props {
  boardId: string;
  boardName: string;
  isOwner: boolean;
  onClose: () => void;
}

const ROLE_LABELS: Record<BoardRole, string> = {
  owner: "Owner",
  editor: "Editor",
  viewer: "Viewer",
};

const ROLE_COLORS: Record<BoardRole, string> = {
  owner: "bg-purple-100 text-purple-700",
  editor: "bg-blue-100 text-blue-700",
  viewer: "bg-gray-100 text-gray-700",
};

export default function BoardMembersModal({ boardId, boardName, isOwner, onClose }: Props) {
  const queryClient = useQueryClient();
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<BoardRole>("viewer");
  const [error, setError] = useState("");

  const { data: members = [] } = useQuery<BoardMember[]>({
    queryKey: ["board-members", boardId],
    queryFn: () => membersApi.list(boardId).then((r) => r.data),
  });

  const { data: invites = [] } = useQuery<BoardInvite[]>({
    queryKey: ["board-invites", boardId],
    queryFn: () => invitesApi.listPending(boardId).then((r) => r.data),
    enabled: isOwner,
  });

  const inviteMutation = useMutation({
    mutationFn: () => invitesApi.create(boardId, email, role),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["board-invites", boardId] });
      setEmail("");
      setError("");
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || "Failed to send invite");
    },
  });

  const updateRoleMutation = useMutation({
    mutationFn: ({ memberId, newRole }: { memberId: string; newRole: BoardRole }) =>
      membersApi.updateRole(boardId, memberId, newRole),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["board-members", boardId] });
    },
  });

  const removeMemberMutation = useMutation({
    mutationFn: (memberId: string) => membersApi.remove(boardId, memberId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["board-members", boardId] });
    },
  });

  const cancelInviteMutation = useMutation({
    mutationFn: (inviteId: string) => invitesApi.cancel(boardId, inviteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["board-invites", boardId] });
    },
  });

  const handleInvite = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    inviteMutation.mutate();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-landing-surface rounded-2xl w-full max-w-lg mx-4 overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-landing-outline-variant/20">
          <div>
            <h2 className="text-lg font-semibold text-landing-on-surface">Share Board</h2>
            <p className="text-sm text-landing-secondary">{boardName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-landing-surface-container rounded-lg transition-colors"
          >
            <X size={20} className="text-landing-secondary" />
          </button>
        </div>

        <div className="p-4 space-y-6 max-h-[70vh] overflow-y-auto">
          {/* Invite form (owner only) */}
          {isOwner && (
            <form onSubmit={handleInvite} className="space-y-3">
              <div className="flex gap-2">
                <input
                  type="email"
                  placeholder="Email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="flex-1 px-3 py-2 bg-landing-surface-container border border-landing-outline-variant/30 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-landing-primary/50"
                />
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value as BoardRole)}
                  className="px-3 py-2 bg-landing-surface-container border border-landing-outline-variant/30 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-landing-primary/50"
                >
                  <option value="viewer">Viewer</option>
                  <option value="editor">Editor</option>
                </select>
              </div>
              <button
                type="submit"
                disabled={inviteMutation.isPending || !email.trim()}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-landing-primary text-white rounded-lg hover:bg-landing-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <UserPlus size={18} />
                {inviteMutation.isPending ? "Sending..." : "Send Invite"}
              </button>
              {error && (
                <p className="text-sm text-red-500">{error}</p>
              )}
            </form>
          )}

          {/* Pending invites (owner only) */}
          {isOwner && invites.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-landing-secondary mb-2 flex items-center gap-2">
                <Clock size={16} />
                Pending Invites
              </h3>
              <div className="space-y-2">
                {invites.map((invite) => (
                  <div
                    key={invite.id}
                    className="flex items-center justify-between p-3 bg-landing-surface-container rounded-lg"
                  >
                    <div>
                      <p className="text-sm font-medium text-landing-on-surface">{invite.email}</p>
                      <span className={`inline-block px-2 py-0.5 rounded text-xs ${ROLE_COLORS[invite.role]}`}>
                        {ROLE_LABELS[invite.role]}
                      </span>
                    </div>
                    <button
                      onClick={() => cancelInviteMutation.mutate(invite.id)}
                      className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                      title="Cancel invite"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Members list */}
          <div>
            <h3 className="text-sm font-medium text-landing-secondary mb-2">
              Members ({members.length})
            </h3>
            <div className="space-y-2">
              {members.map((member) => (
                <div
                  key={member.id}
                  className="flex items-center justify-between p-3 bg-landing-surface-container rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-landing-primary/10 flex items-center justify-center text-landing-primary font-medium text-sm">
                      {member.user_email[0].toUpperCase()}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-landing-on-surface">
                        {member.user_email}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {isOwner && member.role !== "owner" ? (
                      <select
                        value={member.role}
                        onChange={(e) =>
                          updateRoleMutation.mutate({
                            memberId: member.id,
                            newRole: e.target.value as BoardRole,
                          })
                        }
                        className="px-2 py-1 bg-landing-surface border border-landing-outline-variant/30 rounded text-sm focus:outline-none"
                      >
                        <option value="viewer">Viewer</option>
                        <option value="editor">Editor</option>
                      </select>
                    ) : (
                      <span className={`px-2 py-1 rounded text-xs ${ROLE_COLORS[member.role]}`}>
                        {ROLE_LABELS[member.role]}
                      </span>
                    )}
                    {isOwner && member.role !== "owner" && (
                      <button
                        onClick={() => removeMemberMutation.mutate(member.id)}
                        className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                        title="Remove member"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
