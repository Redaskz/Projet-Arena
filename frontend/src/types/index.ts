export interface Game {
  id: number;
  name: string;
  genre: string;
  platform: string;
  team_size: number;
  cover_url: string | null;
  rating: number | null;
  released_at: string | null;
  rawg_id: number | null;
  created_at: string;
}

export interface Team {
  id: number;
  name: string;
  tag: string;
  game_id: number;
  captain_id: number;
  created_at: string;
  players?: Player[];
}

export interface Player {
  id: number;
  gamertag: string;
  role: string;
  country: string | null;
  team_id: number;
  created_at: string;
}

export interface Tournament {
  id: number;
  name: string;
  game_id: number;
  status: 'upcoming' | 'ongoing' | 'finished';
  start_date: string;
  max_teams: number;
}

export interface Match {
  id: number;
  tournament_id: number;
  round: number;
  team_a_id: number;
  team_b_id: number;
  score_a: number | null;
  score_b: number | null;
  status: 'scheduled' | 'played';
  scheduled_at: string;
}

export interface Comment {
  id: number;
  tournament_id: number;
  user_id: number;
  content: string;
  created_at: string;
}

export interface Registration {
  id: number;
  tournament_id: number;
  team_id: number;
  status: 'pending' | 'accepted' | 'rejected';
  registered_at: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'player' | 'admin';
}