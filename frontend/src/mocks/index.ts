// TODO: provisoire — tout ce dossier disparaît quand le backend servira
// GET /games, GET /teams et POST /teams. Il suffira alors de passer
// USE_MOCKS à false : les pages repartiront sur les vraies requêtes.
import { ApiError } from '../api/client';
import type { GameDetails } from '../api/games';
import type { Team } from '../types';

// Typé boolean explicitement : sinon TypeScript le voit comme la constante
// `true` et considère la branche "vraie API" comme du code mort.
export const USE_MOCKS: boolean = true;

export const MOCK_GAMES: GameDetails[] = [
  { id: 1, name: 'Counter-Strike 2', genre: 'fps', platform: 'PC', team_size: 5, cover_url: null },
  { id: 2, name: 'Valorant', genre: 'fps', platform: 'PC', team_size: 5, cover_url: null },
  { id: 3, name: 'League of Legends', genre: 'moba', platform: 'PC', team_size: 5, cover_url: null },
  { id: 4, name: 'EA Sports FC 25', genre: 'sport', platform: 'PC, PS5, Xbox', team_size: 1, cover_url: null },
  { id: 5, name: 'Street Fighter 6', genre: 'fighting', platform: 'PS5', team_size: 1, cover_url: null },
  { id: 6, name: 'Fortnite', genre: 'battle_royale', platform: null, team_size: 4, cover_url: null },
];

// `let` et pas `const` : createTeamMock ajoute les équipes créées,
// pour que la liste rechargée les affiche comme le ferait la vraie API.
let mockTeams: Team[] = [
  { id: 1, name: 'Team Vitality', tag: 'VIT', gameId: 1, captainId: 1 },
  { id: 2, name: 'Karmine Corp', tag: 'KC', gameId: 3, captainId: 2 },
  { id: 3, name: 'Gentle Mates', tag: 'M8', gameId: 2, captainId: 3 },
];

// Même forme que ce que renvoie useFetch une fois le chargement réussi.
export function mockFetchState<T>(data: T) {
  return { data, loading: false, error: null };
}

export function getMockTeams(): Team[] {
  // Copie : un nouveau tableau à chaque appel, pour que React voie le changement.
  return [...mockTeams];
}

export async function createTeamMock(payload: {
  name: string;
  tag: string;
  gameId: number;
}): Promise<Team> {
  // Délai simulé : permet de voir le bouton désactivé pendant l'envoi.
  await new Promise((resolve) => setTimeout(resolve, 600));

  const nameTaken = mockTeams.some(
    (team) => team.name.toLowerCase() === payload.name.toLowerCase(),
  );
  if (nameTaken) {
    // Même erreur que la vraie API : un ApiError avec le statut 409.
    throw new ApiError(409, "Ce nom d'équipe est déjà pris.");
  }

  const team: Team = { id: mockTeams.length + 1, captainId: 1, ...payload };
  mockTeams = [...mockTeams, team];
  return team;
}
