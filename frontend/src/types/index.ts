export type Priority = "low" | "medium" | "high" | "critical";
export type CardStatus = "open" | "in_progress" | "blocked" | "done";
export type CreatedBy = "user" | "claude";

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Board {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
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
  position: number;
  created_by: CreatedBy;
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
  columns: (Column & { cards: Card[] })[];
}
