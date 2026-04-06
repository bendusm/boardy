import axios from "axios";

export const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Attach JWT token from localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("boardy_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-logout on 401
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("boardy_token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// ─── Auth ─────────────────────────────────────────────────────────

export const authApi = {
  register: (email: string, password: string) =>
    api.post("/auth/register", { email, password }),
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),
  me: () => api.get("/auth/me"),
};

// ─── Boards ───────────────────────────────────────────────────────

export const boardsApi = {
  list: () => api.get("/boards"),
  create: (name: string) => api.post("/boards", { name }),
  get: (id: string) => api.get(`/boards/${id}`),
  delete: (id: string) => api.delete(`/boards/${id}`),
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
