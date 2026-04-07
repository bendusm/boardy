import axios from "axios";

const CSRF_STORAGE_KEY = "boardy_csrf";

export const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
  withCredentials: true, // Send httpOnly cookies automatically
});

// Attach CSRF token for state-changing requests
api.interceptors.request.use((config) => {
  const method = config.method?.toUpperCase();
  if (method && ["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const csrfToken = sessionStorage.getItem(CSRF_STORAGE_KEY);
    if (csrfToken) {
      config.headers["X-CSRF-Token"] = csrfToken;
    }
  }
  return config;
});

// Auto-logout on 401 (except for /auth/me which is used to check session)
api.interceptors.response.use(
  (r) => r,
  (err) => {
    const isAuthCheck = err.config?.url?.includes("/auth/me");
    if (err.response?.status === 401 && !isAuthCheck) {
      sessionStorage.removeItem(CSRF_STORAGE_KEY);
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// ─── Auth ─────────────────────────────────────────────────────────

export const authApi = {
  register: (email: string, password: string, agreedToTerms: boolean) =>
    api.post("/auth/register", { email, password, agreed_to_terms: agreedToTerms }),
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),
  logout: () => api.post("/auth/logout"),
  me: () => api.get("/auth/me"),
  deleteAccount: (password: string) =>
    api.delete("/auth/account", { data: { password } }),
  exportData: () => api.get("/auth/export"),
};

// ─── Boards ───────────────────────────────────────────────────────

export const boardsApi = {
  list: () => api.get("/boards"),
  create: (name: string) => api.post("/boards", { name }),
  get: (id: string) => api.get(`/boards/${id}`),
  delete: (id: string) => api.delete(`/boards/${id}`),
  rename: (id: string, name: string) => api.patch(`/boards/${id}`, { name }),
};

// ─── Cards ────────────────────────────────────────────────────────

// ─── Columns ──────────────────────────────────────────────────────

export const columnsApi = {
  create: (boardId: string, name: string, position: number) =>
    api.post(`/boards/${boardId}/columns`, { name, position }),
  rename: (boardId: string, columnId: string, name: string) =>
    api.patch(`/boards/${boardId}/columns/${columnId}`, { name, position: 0 }),
  delete: (boardId: string, columnId: string) =>
    api.delete(`/boards/${boardId}/columns/${columnId}`),
};

// ─── Cards ────────────────────────────────────────────────────────

export const cardsApi = {
  create: (boardId: string, columnId: string, data: { title: string; description?: string; priority?: string }) =>
    api.post(`/boards/${boardId}/columns/${columnId}/cards`, data),
  update: (cardId: string, data: object) => api.patch(`/cards/${cardId}`, data),
  move: (cardId: string, toColumnId: string, position: number) =>
    api.post(`/cards/${cardId}/move`, { to_column_id: toColumnId, position }),
  delete: (cardId: string) => api.delete(`/cards/${cardId}`),
  comments: (cardId: string) => api.get(`/cards/${cardId}/comments`),
  addComment: (cardId: string, text: string) =>
    api.post(`/cards/${cardId}/comments`, { text }),
};

// ─── Members ──────────────────────────────────────────────────────

export const membersApi = {
  list: (boardId: string) => api.get(`/boards/${boardId}/members`),
  updateRole: (boardId: string, memberId: string, role: string) =>
    api.patch(`/boards/${boardId}/members/${memberId}`, { role }),
  remove: (boardId: string, memberId: string) =>
    api.delete(`/boards/${boardId}/members/${memberId}`),
};

// ─── Invites ──────────────────────────────────────────────────────

export const invitesApi = {
  create: (boardId: string, email: string, role: string) =>
    api.post(`/boards/${boardId}/invites`, { email, role }),
  listPending: (boardId: string) => api.get(`/boards/${boardId}/invites`),
  cancel: (boardId: string, inviteId: string) =>
    api.delete(`/boards/${boardId}/invites/${inviteId}`),
  my: () => api.get("/invites/my"),
  accept: (token: string) => api.post(`/invites/${token}/accept`),
  decline: (token: string) => api.post(`/invites/${token}/decline`),
};
