import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { LayoutDashboard, Loader2 } from "lucide-react";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

export default function RegisterPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    setLoading(true);
    try {
      const { data } = await authApi.register(email, password);
      setAuth(data.user, data.access_token);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed");
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
              to="/login"
              className="text-landing-secondary font-medium text-sm px-4 py-2 hover:text-landing-primary transition-colors"
            >
              Log in
            </Link>
          </div>
        </nav>
      </header>

      {/* Main */}
      <main className="flex items-center justify-center px-6 py-20">
        <div className="w-full max-w-md">
          <div className="text-center mb-10">
            <h1 className="font-headline italic text-4xl md:text-5xl mb-4">
              Get started free
            </h1>
            <p className="text-landing-secondary">
              Create your account and let AI manage your boards
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
                  <span className="text-landing-secondary font-normal ml-2">
                    (min 8 characters)
                  </span>
                </label>
                <input
                  id="password"
                  type="password"
                  required
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
                    Creating account...
                  </>
                ) : (
                  "Create account"
                )}
              </button>
            </form>

            <p className="mt-6 text-xs text-landing-secondary text-center">
              By creating an account, you agree to our Terms of Service and
              Privacy Policy
            </p>

            <div className="mt-6 pt-6 border-t border-landing-outline-variant/20 text-center">
              <p className="text-sm text-landing-secondary">
                Already have an account?{" "}
                <Link
                  to="/login"
                  className="text-landing-primary hover:underline font-semibold"
                >
                  Sign in
                </Link>
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
