import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { LayoutDashboard, Loader2 } from "lucide-react";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

export default function LoginPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await authApi.login(email, password);
      queryClient.clear(); // Clear cache from previous user
      setAuth(data.user, data.csrf_token);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
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
            <Link
              to="/register"
              className="bg-landing-primary text-white px-5 py-2.5 rounded-full text-sm font-semibold hover:shadow-lg hover:shadow-landing-primary/20 transition-all"
            >
              Start for free
            </Link>
          </div>
        </nav>
      </header>

      {/* Main */}
      <main className="flex items-center justify-center px-6 py-20">
        <div className="w-full max-w-md">
          <div className="text-center mb-10">
            <h1 className="font-headline italic text-4xl md:text-5xl mb-4">
              Welcome back
            </h1>
            <p className="text-landing-secondary">
              Sign in to continue managing your boards
            </p>
          </div>

          <div className="bg-white rounded-3xl shadow-startup border border-landing-outline-variant/10 p-8">
            {error && (
              <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label
                  className="block text-sm font-semibold text-landing-on-background mb-2"
                  htmlFor="email"
                >
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-landing-outline-variant/30 bg-landing-surface-container-low text-sm focus:outline-none focus:ring-2 focus:ring-landing-primary/30 focus:border-landing-primary transition-all"
                  placeholder="you@example.com"
                />
              </div>

              <div>
                <label
                  className="block text-sm font-semibold text-landing-on-background mb-2"
                  htmlFor="password"
                >
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-landing-outline-variant/30 bg-landing-surface-container-low text-sm focus:outline-none focus:ring-2 focus:ring-landing-primary/30 focus:border-landing-primary transition-all"
                  placeholder="••••••••"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 px-6 bg-landing-primary text-white rounded-full text-base font-bold hover:shadow-lg hover:shadow-landing-primary/20 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  "Sign in"
                )}
              </button>
            </form>

            <div className="mt-6 pt-6 border-t border-landing-outline-variant/20 text-center">
              <p className="text-sm text-landing-secondary">
                Don't have an account?{" "}
                <Link
                  to="/register"
                  className="text-landing-primary hover:underline font-semibold"
                >
                  Create one for free
                </Link>
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
