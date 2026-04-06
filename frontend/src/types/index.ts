export type Priority = "low" | "medium" | "high" | "critical";
export type CardStatus = "open" | "in_progress" | "blocked" | "done";
export type CardColor = "gray" | "red" | "orange" | "yellow" | "green" | "blue" | "purple" | "pink";
export type CreatedBy = "user" | "claude";
export type BoardRole = "owner" | "editor" | "viewer";
export type InviteStatus = "pending" | "accepted" | "declined";

export interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
}

export interface Board {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
  my_role?: BoardRole;
  created_at: string;
}

export interface Column {
  id: string;
  board_id: string;
  name: string;
  position: number;
  cards?: Card[];
}

export interface Card {
  id: string;
  column_id: string;
  board_id: string;
  title: string;
  description: string | null;
  priority: Priority;
  status: CardStatus;
  color: CardColor;
  position: number;
  created_by: CreatedBy;
  assignee_id: string | null;
  assignee_name: string | null;
  due_date: string | null;
  labels: string[];
  archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: string;
  card_id: string;
  author: CreatedBy;
  text: string;
  created_at: string;
}

export interface BoardFull {
  id: string;
  name: string;
  slug: string;
  my_role?: BoardRole;
  columns: (Column & { cards: Card[] })[];
}

export interface BoardMember {
  id: string;
  user_id: string;
  user_email: string;
  role: BoardRole;
  created_at: string;
}

export interface BoardInvite {
  id: string;
  board_id: string;
  board_name: string;
  email: string;
  role: BoardRole;
  invited_by_email: string;
  status: InviteStatus;
  token: string;
  created_at: string;
  expires_at: string;
}
