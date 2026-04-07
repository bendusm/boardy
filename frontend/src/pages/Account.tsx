import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, LayoutDashboard, Trash2, Loader2, AlertTriangle, Download } from "lucide-react";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

export default function AccountPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { user, logout } = useAuthStore();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [password, setPassword] = useState("");
  const [confirmText, setConfirmText] = useState("");
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState(false);

  const deleteMutation = useMutation({
    mutationFn: () => authApi.deleteAccount(password),
    onSuccess: () => {
      qc.clear();
      logout();
      navigate("/");
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || "Failed to delete account");
    },
  });

  function handleDelete() {
    if (confirmText !== "DELETE" || !password) return;
    setError("");
    deleteMutation.mutate();
  }

  async function handleExport() {
    setExporting(true);
    try {
      const { data } = await authApi.exportData();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `boardy-export-${new Date().toISOString().split("T")[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to export data");
    } finally {
      setExporting(false);
    }
  }

  return (
    <div className="min-h-screen bg-landing-background font-body">
      {/* Header */}
      <header className="w-full border-b border-landing-outline-variant/20 bg-white/70 backdrop-blur-md sticky top-0 z-50">
        <nav className="flex justify-between items-center max-w-7xl mx-auto px-6 md:px-12 py-5">
          <div className="flex items-center gap-4">
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
              <div className="font-headline italic text-2xl font-bold text-landing-on-background">
                Boardy
              </div>
            </Link>
          </div>
        </nav>
      </header>

      {/* Main */}
      <main className="max-w-2xl mx-auto px-6 md:px-12 py-12">
        <h1 className="font-headline italic text-3xl md:text-4xl mb-2">
          Account Settings
        </h1>
        <p className="text-landing-secondary mb-8">
          Manage your account preferences
        </p>

        {/* Account info */}
        <div className="bg-white rounded-2xl shadow-startup border border-landing-outline-variant/10 p-6 mb-8">
          <h2 className="font-semibold text-lg mb-4">Account Information</h2>
          <div className="space-y-3">
            <div>
              <label className="text-sm text-landing-secondary">Email</label>
              <p className="text-landing-on-background">{user?.email}</p>
            </div>
          </div>
        </div>

        {/* Data Export (GDPR) */}
        <div className="bg-white rounded-2xl shadow-startup border border-landing-outline-variant/10 p-6 mb-8">
          <h2 className="font-semibold text-lg mb-2">Your Data</h2>
          <p className="text-sm text-landing-secondary mb-4">
            Download a copy of all your data including boards, cards, and comments.
            This is your right under GDPR Article 20 (Data Portability).
          </p>
          <button
            onClick={handleExport}
            disabled={exporting}
            className="flex items-center gap-2 px-5 py-3 bg-landing-primary text-white rounded-xl font-medium hover:shadow-lg hover:shadow-landing-primary/20 disabled:opacity-50 transition-all"
          >
            {exporting ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <Download size={18} />
            )}
            {exporting ? "Exporting..." : "Export My Data"}
          </button>
        </div>

        {/* Danger zone */}
        <div className="bg-white rounded-2xl shadow-startup border border-red-200 p-6">
          <h2 className="font-semibold text-lg mb-2 flex items-center gap-2 text-red-600">
            <AlertTriangle size={20} />
            Danger Zone
          </h2>
          <p className="text-sm text-landing-secondary mb-6">
            Once you delete your account, there is no going back. All your boards and data will be permanently deleted.
          </p>

          {!showDeleteConfirm ? (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="flex items-center gap-2 px-5 py-3 border-2 border-red-200 text-red-600 rounded-xl font-medium hover:bg-red-50 transition-colors"
            >
              <Trash2 size={18} />
              Delete Account
            </button>
          ) : (
            <div className="bg-red-50 rounded-xl p-5 border border-red-200">
              <p className="text-sm text-red-700 mb-4 font-medium">
                This will permanently delete:
              </p>
              <ul className="text-sm text-red-600 mb-4 list-disc list-inside space-y-1">
                <li>All boards you own</li>
                <li>All cards, comments, and attachments</li>
                <li>Your membership in shared boards</li>
                <li>Your account and all data</li>
              </ul>

              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-red-700 block mb-2">
                    Enter your password
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-red-300 text-sm focus:outline-none focus:ring-2 focus:ring-red-500/30"
                    placeholder="Your password"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium text-red-700 block mb-2">
                    Type DELETE to confirm
                  </label>
                  <input
                    type="text"
                    value={confirmText}
                    onChange={(e) => setConfirmText(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-red-300 text-sm focus:outline-none focus:ring-2 focus:ring-red-500/30"
                    placeholder="DELETE"
                  />
                </div>

                {error && (
                  <p className="text-sm text-red-600 bg-red-100 rounded-lg px-3 py-2">
                    {error}
                  </p>
                )}

                <div className="flex gap-3">
                  <button
                    onClick={handleDelete}
                    disabled={confirmText !== "DELETE" || !password || deleteMutation.isPending}
                    className="flex-1 px-5 py-3 bg-red-600 text-white rounded-xl font-medium disabled:opacity-50 hover:bg-red-700 transition-colors flex items-center justify-center gap-2"
                  >
                    {deleteMutation.isPending && <Loader2 size={16} className="animate-spin" />}
                    Delete My Account
                  </button>
                  <button
                    onClick={() => {
                      setShowDeleteConfirm(false);
                      setPassword("");
                      setConfirmText("");
                      setError("");
                    }}
                    className="px-5 py-3 text-gray-600 hover:bg-gray-100 rounded-xl font-medium transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
