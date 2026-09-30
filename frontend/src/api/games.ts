import type { GameGenre } from '../types';

// Les 5 genres acceptés par le backend (enum GameGenre dans backend/app/models/game.py).
// Le type vit dans types/index.ts avec les autres enums de l'API.
export type { GameGenre };

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

// Une valeur venue de l'extérieur (localStorage, <select>) n'est qu'une chaîne :
// TypeScript ne peut pas savoir que c'est l'un des 5 genres. Cette fonction le
// vérifie à l'exécution ; le `value is GameGenre` dit ensuite à TypeScript que
// la valeur est sûre, sans cast `as`.
export function isGameGenre(value: string): value is GameGenre {
  // hasOwnProperty et non `in` : `in` remonte le prototype, et
  // 'toString' in GENRE_LABELS vaut true.
  return Object.prototype.hasOwnProperty.call(GENRE_LABELS, value);
}

// Libellé d'un genre, ou le texte brut si le backend renvoie un genre inconnu
// du front : on affiche quelque chose plutôt que de planter.
export function getGenreLabel(genre: string): string {
  return isGameGenre(genre) ? GENRE_LABELS[genre] : genre;
}
