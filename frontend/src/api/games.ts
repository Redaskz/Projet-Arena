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

// Game.genre est typé `string` dans types/index.ts : TypeScript ne peut donc
// pas savoir que c'est l'un des 5 genres. Cette fonction le vérifie à
// l'exécution ; le `value is GameGenre` dit ensuite à TypeScript que la valeur
// est sûre, sans cast `as`.
export function isGameGenre(value: string): value is GameGenre {
  return value in GENRE_LABELS;
}

// Libellé d'un genre, ou le texte brut si le backend renvoie un genre inconnu
// du front : on affiche quelque chose plutôt que de planter.
export function getGenreLabel(genre: string): string {
  return isGameGenre(genre) ? GENRE_LABELS[genre] : genre;
}
