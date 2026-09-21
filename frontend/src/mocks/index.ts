// TODO: provisoire — tout ce dossier disparaît quand le backend servira
// GET /games, GET /teams, POST /teams et GET /tournaments. Il suffira alors de
// passer USE_MOCKS à false : les pages repartiront sur les vraies requêtes.
import { ApiError } from '../api/client';
import type { TeamCreate } from '../api/teams';
import type { Game, Team, Tournament } from '../types';

// Typé boolean explicitement : sinon TypeScript le voit comme la constante
// `true` et considère la branche "vraie API" comme du code mort.
export const USE_MOCKS: boolean = true;

// Fixtures typées Game et Team : si le type change (ajout ou renommage d'un
// champ), TypeScript refuse de compiler tant qu'elles ne sont pas alignées.
// Elles ont donc exactement les mêmes noms de champs que la vraie API.
export const MOCK_GAMES: Game[] = [
  {
    id: 1, name: 'Counter-Strike 2', genre: 'fps', platform: 'PC', team_size: 5,
    cover_url: null, rating: 3.6, released_at: '2023-09-27', rawg_id: null,
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 2, name: 'Valorant', genre: 'fps', platform: 'PC', team_size: 5,
    cover_url: null, rating: 3.5, released_at: '2020-06-02', rawg_id: null,
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 3, name: 'League of Legends', genre: 'moba', platform: 'PC', team_size: 5,
    cover_url: null, rating: 3.8, released_at: '2009-10-27', rawg_id: null,
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 4, name: 'EA Sports FC 25', genre: 'sport', platform: 'PC, PS5, Xbox', team_size: 1,
    cover_url: null, rating: null, released_at: '2024-09-27', rawg_id: null,
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 5, name: 'Street Fighter 6', genre: 'fighting', platform: 'PS5', team_size: 1,
    cover_url: null, rating: 4.1, released_at: '2023-06-02', rawg_id: null,
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    // platform vide : montre le texte "Plateforme non précisée" de GameCard.
    id: 6, name: 'Fortnite', genre: 'battle_royale', platform: '', team_size: 4,
    cover_url: null, rating: null, released_at: null, rawg_id: null,
    created_at: '2026-09-15T10:00:00Z',
  },
];

// `let` et pas `const` : createTeamMock ajoute les équipes créées,
// pour que la liste rechargée les affiche comme le ferait la vraie API.
let mockTeams: Team[] = [
  { id: 1, name: 'Team Vitality', tag: 'VIT', game_id: 1, captain_id: 1, created_at: '2026-09-16T09:00:00Z' },
  { id: 2, name: 'Karmine Corp', tag: 'KC', game_id: 3, captain_id: 2, created_at: '2026-09-16T09:00:00Z' },
  { id: 3, name: 'Gentle Mates', tag: 'M8', game_id: 2, captain_id: 3, created_at: '2026-09-16T09:00:00Z' },
];

// Même forme que ce que renvoie useFetch une fois le chargement réussi.
export function mockFetchState<T>(data: T) {
  return { data, loading: false, error: null };
}

export function getMockTeams(): Team[] {
  // Copie : un nouveau tableau à chaque appel, pour que React voie le changement.
  return [...mockTeams];
}

export async function createTeamMock(payload: TeamCreate): Promise<Team> {
  // Délai simulé : permet de voir le bouton désactivé pendant l'envoi.
  await new Promise((resolve) => setTimeout(resolve, 600));

  const nameTaken = mockTeams.some(
    (team) => team.name.toLowerCase() === payload.name.toLowerCase(),
  );
  if (nameTaken) {
    // Même erreur que la vraie API : un ApiError avec le statut 409.
    throw new ApiError(409, "Ce nom d'équipe est déjà pris.");
  }

  // Les champs remplis par le serveur (id, captain_id, created_at) sont
  // simulés ici, comme le ferait le backend.
  const team: Team = {
    id: mockTeams.length + 1,
    captain_id: 1,
    created_at: new Date().toISOString(),
    ...payload,
  };
  mockTeams = [...mockTeams, team];
  return team;
}

// Tournois fictifs de Victor (page /tournaments), repris de sa branche
// feat/tournaments-page et convertis en snake_case pour suivre types/index.ts.
export const MOCK_TOURNAMENTS: Tournament[] = [
  { id: 1, name: 'Arena Masters CS2', game_id: 1, status: 'upcoming', start_date: '2026-10-05T18:00:00', max_teams: 16 },
  { id: 2, name: 'Valorant Winter Cup', game_id: 2, status: 'ongoing', start_date: '2026-09-20T18:00:00', max_teams: 16 },
  { id: 3, name: 'League of Legends Championship', game_id: 3, status: 'finished', start_date: '2026-08-15T14:00:00', max_teams: 32 },
  { id: 4, name: 'FC 25 Arena Cup', game_id: 4, status: 'upcoming', start_date: '2026-10-12T15:00:00', max_teams: 16 },
  { id: 5, name: 'Street Fighter Open', game_id: 5, status: 'ongoing', start_date: '2026-09-18T19:00:00', max_teams: 32 },
  { id: 6, name: 'Fortnite Battle Arena', game_id: 6, status: 'finished', start_date: '2026-07-20T16:00:00', max_teams: 24 },
  { id: 7, name: 'CS2 Community Cup', game_id: 1, status: 'ongoing', start_date: '2026-09-19T17:00:00', max_teams: 8 },
  { id: 8, name: 'Valorant Open Series', game_id: 2, status: 'upcoming', start_date: '2026-10-20T18:00:00', max_teams: 32 },
  { id: 9, name: 'League Arena Masters', game_id: 3, status: 'finished', start_date: '2026-08-30T16:00:00', max_teams: 16 },
  { id: 10, name: 'Fortnite Pro Cup', game_id: 6, status: 'upcoming', start_date: '2026-10-25T20:00:00', max_teams: 16 },
];

// Accesseurs utilisés par TournamentsPage (Victor) : une copie à chaque appel.
export function getMockGames(): Game[] {
  return [...MOCK_GAMES];
}

export function getMockTournaments(): Tournament[] {
  return [...MOCK_TOURNAMENTS];
}
