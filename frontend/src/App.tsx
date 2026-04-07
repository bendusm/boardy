import { useEffect, useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth";
import { authApi } from "@/lib/api";
import LandingPage from "@/pages/Landing";
import LoginPage from "@/pages/Login";
import RegisterPage from "@/pages/Register";
import DashboardPage from "@/pages/Dashboard";
import BoardPage from "@/pages/Board";
import AccountPage from "@/pages/Account";
import PrivacyPage from "@/pages/Privacy";
import TermsPage from "@/pages/Terms";
import ImprintPage from "@/pages/Imprint";
import DocsPage from "@/pages/Docs";

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, csrfToken } = useAuthStore();
  const isAuthenticated = !!user || !!csrfToken;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function AuthLoader({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);
  const setAuth = useAuthStore((s) => s.setAuth);
  const csrfToken = useAuthStore((s) => s.csrfToken);

  useEffect(() => {
    // Try to restore session from httpOnly cookie
    if (!csrfToken) {
      authApi.me()
        .then(({ data }) => {
          // Read CSRF token from cookie (set by social auth or regular login)
          const csrfFromCookie = document.cookie
            .split("; ")
            .find((c) => c.startsWith("boardy_csrf="))
            ?.split("=")[1] || "";
          const restoredCsrf = sessionStorage.getItem("boardy_csrf") || csrfFromCookie;
          if (restoredCsrf) {
            sessionStorage.setItem("boardy_csrf", restoredCsrf);
          }
          setAuth(data, restoredCsrf);
        })
        .catch(() => {
          // No valid session
        })
        .finally(() => setLoading(false));
    } else {
      // Already have CSRF token, try to get user
      authApi.me()
        .then(({ data }) => setAuth(data, csrfToken))
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-landing-primary border-t-transparent rounded-full" />
      </div>
    );
  }

  return <>{children}</>;
}

export default function App() {
  return (
    <AuthLoader>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/terms" element={<TermsPage />} />
        <Route path="/imprint" element={<ImprintPage />} />
        <Route path="/docs" element={<DocsPage />} />
        <Route
          path="/dashboard"
          element={
            <RequireAuth>
              <DashboardPage />
            </RequireAuth>
          }
        />
        <Route
          path="/boards/:boardId"
          element={
            <RequireAuth>
              <BoardPage />
            </RequireAuth>
          }
        />
        <Route
          path="/account"
          element={
            <RequireAuth>
              <AccountPage />
            </RequireAuth>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthLoader>
  );
}
