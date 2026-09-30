// Ces types reproduisent les schémas *Read du backend (backend/app/schemas/).
// Les dates arrivent en chaînes ISO : JSON n'a pas de type date.

// Enums du backend, recopiés valeur pour valeur. Ils sont exportés parce que
// StatusBadge et les filtres s'appuient dessus : une valeur ajoutée ici sans
// libellé fait échouer la compilation au lieu d'afficher un badge vide.
export type GameGenre = 'fps' | 'moba' | 'sport' | 'fighting' | 'battle_royale';
export type TournamentStatus = 'upcoming' | 'ongoing' | 'finished';
export type MatchStatus = 'scheduled' | 'played';
export type RegistrationStatus = 'pending' | 'accepted' | 'rejected';
export type UserRole = 'player' | 'admin';

export interface Game {
  id: number;
  name: string;
  genre: GameGenre;
  // Facultatif à la création (GameCreate.platform), donc null possible.
  platform: string | null;
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
  status: TournamentStatus;
  // Date seule ("2026-10-05"), sans heure : c'est un `date` côté Pydantic.
  start_date: string;
  max_teams: number;
  created_at: string;
}

export interface Match {
  id: number;
  tournament_id: number;
  round: number;
  team_a_id: number;
  team_b_id: number;
  score_a: number | null;
  score_b: number | null;
  status: MatchStatus;
  // Le calendrier généré ne fixe pas d'horaire : null tant qu'il n'est pas planifié.
  scheduled_at: string | null;
  created_at: string;
}

// Commentaires et inscriptions n'ont pas encore de route côté backend : ces
// types décrivent le contrat prévu, utilisé pour l'instant par des données locales.
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
  status: RegistrationStatus;
  registered_at: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  created_at: string;
}

// Réponse de POST /auth/login.
export interface Token {
  access_token: string;
  token_type: string;
}
