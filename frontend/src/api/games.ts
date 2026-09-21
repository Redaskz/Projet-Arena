// Les 5 genres acceptés par le backend (enum GameGenre dans backend/app/models/game.py).
export type GameGenre = 'fps' | 'moba' | 'sport' | 'fighting' | 'battle_royale';

// Libellés affichés à l'utilisateur. Record<GameGenre, string> oblige TypeScript
// à vérifier qu'aucun genre n'a été oublié : ajouter un genre au type sans
// libellé ici provoque une erreur de compilation.
export const GENRE_LABELS: Record<GameGenre, string> = {
  fps: 'FPS',
  moba: 'MOBA',
  sport: 'Sport',
  fighting: 'Combat',
  battle_royale: 'Battle royale',
};

// TODO: provisoire — le type Game de types/index.ts (Yanis) ne correspond pas à
// ce que renvoie GET /games (schéma GameRead du backend). Ce type recopie
// GameRead ; il sera supprimé quand Game sera aligné, et remplacé par Game.
export interface GameDetails {
  id: number;
  name: string;
  genre: GameGenre;
  platform: string | null;
  team_size: number;
  cover_url: string | null;
}
