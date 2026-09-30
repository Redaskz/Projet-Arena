import { patch } from './client';
import type { Match } from '../types';
import { USE_MOCKS, updateMatchScoreMock } from '../mocks';

// Saisir un score, c'est aussi clore le match : on envoie le statut `played`
// en même temps, sinon le match resterait « à jouer » avec un score.
// PATCH /matches/{id} est protégé : client.ts y joint le jeton de la session.
// Le backend répond 409 si le match a déjà été joué.
export function updateMatchScore(
  matchId: number,
  scoreA: number,
  scoreB: number,
): Promise<Match> {
  if (USE_MOCKS) {
    return updateMatchScoreMock(matchId, scoreA, scoreB);
  }

  return patch<Match>(`/matches/${matchId}`, {
    score_a: scoreA,
    score_b: scoreB,
    status: 'played',
  });
}
