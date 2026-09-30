// Solution de repli : le frontend est branché sur le vrai backend, mais ces
// données fictives restent en place. Si l'API est indisponible (démo, poste
// sans Docker), repasser USE_MOCKS à true suffit à faire tourner toute
// l'interface, connexion comprise, sans aucun appel réseau.

import { ApiError } from '../api/client';
import type { TeamCreate } from '../api/teams';
import type { Game, Match, Team, Tournament, User } from '../types';

// Typé boolean explicitement : sinon TypeScript le voit comme la constante
// `false` et considère la branche "mocks" comme du code mort.
export const USE_MOCKS: boolean = false;

// Fixtures typées Game et Team : si le type change, TypeScript refuse de compiler
// tant que les données fictives ne sont pas alignées avec les vrais types.
export const MOCK_GAMES: Game[] = [
  {
    id: 1,
    name: 'Counter-Strike 2',
    genre: 'fps',
    platform: 'PC',
    team_size: 5,
    cover_url: null,
    rating: 3.6,
    released_at: '2023-09-27',
    rawg_id: null,
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 2,
    name: 'Valorant',
    genre: 'fps',
    platform: 'PC',
    team_size: 5,
    cover_url: null,
    rating: 3.5,
    released_at: '2020-06-02',
    rawg_id: null,
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 3,
    name: 'League of Legends',
    genre: 'moba',
    platform: 'PC',
    team_size: 5,
    cover_url: null,
    rating: 3.8,
    released_at: '2009-10-27',
    rawg_id: null,
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 4,
    name: 'EA Sports FC 25',
    genre: 'sport',
    platform: 'PC, PS5, Xbox',
    team_size: 1,
    cover_url: null,
    rating: null,
    released_at: '2024-09-27',
    rawg_id: null,
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 5,
    name: 'Street Fighter 6',
    genre: 'fighting',
    platform: 'PS5',
    team_size: 1,
    cover_url: null,
    rating: 4.1,
    released_at: '2023-06-02',
    rawg_id: null,
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    // Cette valeur permet de tester l'affichage lorsqu'une plateforme est absente.
    id: 6,
    name: 'Fortnite',
    genre: 'battle_royale',
    platform: '',
    team_size: 4,
    cover_url: null,
    rating: null,
    released_at: null,
    rawg_id: null,
    created_at: '2026-09-15T10:00:00Z',
  },
];

// `let` permet à createTeamMock d'ajouter une équipe et de conserver
// cette nouvelle équipe lors des futurs affichages.
let mockTeams: Team[] = [
  {
    id: 1,
    name: 'Team Vitality',
    tag: 'VIT',
    game_id: 1,
    captain_id: 1,
    created_at: '2026-09-16T09:00:00Z',
  },
  {
    id: 2,
    name: 'Karmine Corp',
    tag: 'KC',
    game_id: 3,
    captain_id: 2,
    created_at: '2026-09-16T09:00:00Z',
  },
  {
    id: 3,
    name: 'Gentle Mates',
    tag: 'M8',
    game_id: 2,
    captain_id: 3,
    created_at: '2026-09-16T09:00:00Z',
  },
];

// Même forme que ce que renvoie useFetch une fois le chargement terminé.
export function mockFetchState<T>(data: T) {
  return {
    data,
    loading: false,
    error: null,
  };
}

export function getMockTeams(): Team[] {
  // Une copie évite qu'un composant puisse modifier directement les fixtures.
  return [...mockTeams];
}

export async function createTeamMock(
  payload: TeamCreate,
): Promise<Team> {
  // Un petit délai permet de conserver le comportement d'une vraie requête HTTP.
  await new Promise((resolve) => setTimeout(resolve, 600));

  const nameTaken = mockTeams.some(
    (team) => team.name.toLowerCase() === payload.name.toLowerCase(),
  );

  if (nameTaken) {
    // On reproduit l'erreur que pourrait renvoyer le backend lors d'un conflit.
    throw new ApiError(409, "Ce nom d'équipe est déjà pris.");
  }

  // Les champs normalement générés par le serveur sont simulés ici.
  const team: Team = {
    id: mockTeams.length + 1,
    created_at: new Date().toISOString(),
    ...payload,
  };

  mockTeams = [...mockTeams, team];

  return team;
};

// Tournois fictifs utilisés par la page /tournaments.
// Les champs suivent les types backend en snake_case.
export const MOCK_TOURNAMENTS: Tournament[] = [
  {
    id: 1,
    name: 'Arena Masters CS2',
    game_id: 1,
    status: 'upcoming',
    start_date: '2026-10-05',
    max_teams: 16,
    created_at: '2026-09-01T10:00:00Z',
  },
  {
    id: 2,
    name: 'Valorant Winter Cup',
    game_id: 2,
    status: 'ongoing',
    start_date: '2026-09-20',
    max_teams: 16,
    created_at: '2026-09-01T10:00:00Z',
  },
  {
    id: 3,
    name: 'League of Legends Championship',
    game_id: 3,
    status: 'finished',
    start_date: '2026-08-15',
    max_teams: 32,
    created_at: '2026-09-01T10:00:00Z',
  },
  {
    id: 4,
    name: 'FC 25 Arena Cup',
    game_id: 4,
    status: 'upcoming',
    start_date: '2026-10-12',
    max_teams: 16,
    created_at: '2026-09-01T10:00:00Z',
  },
  {
    id: 5,
    name: 'Street Fighter Open',
    game_id: 5,
    status: 'ongoing',
    start_date: '2026-09-18',
    max_teams: 32,
    created_at: '2026-09-01T10:00:00Z',
  },
  {
    id: 6,
    name: 'Fortnite Battle Arena',
    game_id: 6,
    status: 'finished',
    start_date: '2026-07-20',
    max_teams: 24,
    created_at: '2026-09-01T10:00:00Z',
  },
  {
    id: 7,
    name: 'CS2 Community Cup',
    game_id: 1,
    status: 'ongoing',
    start_date: '2026-09-19',
    max_teams: 8,
    created_at: '2026-09-01T10:00:00Z',
  },
  {
    id: 8,
    name: 'Valorant Open Series',
    game_id: 2,
    status: 'upcoming',
    start_date: '2026-10-20',
    max_teams: 32,
    created_at: '2026-09-01T10:00:00Z',
  },
  {
    id: 9,
    name: 'League Arena Masters',
    game_id: 3,
    status: 'finished',
    start_date: '2026-08-30',
    max_teams: 16,
    created_at: '2026-09-01T10:00:00Z',
  },
  {
    id: 10,
    name: 'Fortnite Pro Cup',
    game_id: 6,
    status: 'upcoming',
    start_date: '2026-10-25',
    max_teams: 16,
    created_at: '2026-09-01T10:00:00Z',
  },
];

// Accesseurs utilisés par les pages pour récupérer les données fictives.
export function getMockGames(): Game[] {
  return [...MOCK_GAMES];
}

export function getMockTournaments(): Tournament[] {
  return [...MOCK_TOURNAMENTS];
}

// Matchs fictifs utilisés par la page des matchs et le classement.
// Plusieurs résultats sont volontairement différents pour tester les calculs.
export const MOCK_MATCHES: Match[] = [
  {
    id: 1,
    tournament_id: 1,
    round: 1,
    team_a_id: 1,
    team_b_id: 2,
    score_a: 2,
    score_b: 1,
    status: 'played',
    scheduled_at: '2026-09-20T18:00:00Z',
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 2,
    tournament_id: 1,
    round: 1,
    team_a_id: 2,
    team_b_id: 3,
    score_a: 0,
    score_b: 0,
    status: 'played',
    scheduled_at: '2026-09-20T20:00:00Z',
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 3,
    tournament_id: 1,
    round: 2,
    team_a_id: 1,
    team_b_id: 3,
    score_a: 3,
    score_b: 1,
    status: 'played',
    scheduled_at: '2026-09-21T18:00:00Z',
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 4,
    tournament_id: 1,
    round: 2,
    team_a_id: 2,
    team_b_id: 1,
    score_a: 1,
    score_b: 2,
    status: 'played',
    scheduled_at: '2026-09-21T20:00:00Z',
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 5,
    tournament_id: 1,
    round: 3,
    team_a_id: 3,
    team_b_id: 2,
    score_a: 2,
    score_b: 2,
    status: 'played',
    scheduled_at: '2026-09-22T18:00:00Z',
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 6,
    tournament_id: 2,
    round: 1,
    team_a_id: 1,
    team_b_id: 3,
    score_a: 0,
    score_b: 1,
    status: 'played',
    scheduled_at: '2026-09-23T18:00:00Z',
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 7,
    tournament_id: 2,
    round: 1,
    team_a_id: 3,
    team_b_id: 1,
    score_a: 2,
    score_b: 2,
    status: 'played',
    scheduled_at: '2026-09-23T20:00:00Z',
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 8,
    tournament_id: 2,
    round: 2,
    team_a_id: 2,
    team_b_id: 3,
    score_a: 1,
    score_b: 3,
    status: 'played',
    scheduled_at: '2026-09-24T18:00:00Z',
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 9,
    tournament_id: 2,
    round: 2,
    team_a_id: 1,
    team_b_id: 2,
    score_a: null,
    score_b: null,
    status: 'scheduled',
    scheduled_at: '2026-09-25T18:00:00Z',
    created_at: '2026-09-15T10:00:00Z',
  },
  {
    id: 10,
    tournament_id: 2,
    round: 3,
    team_a_id: 2,
    team_b_id: 1,
    score_a: null,
    score_b: null,
    status: 'scheduled',
    scheduled_at: '2026-09-25T20:00:00Z',
    created_at: '2026-09-15T10:00:00Z',
  },
];

export function getMockMatches(): Match[] {
  // Une copie évite qu'une modification de la page ne modifie les fixtures partagées.
  return [...MOCK_MATCHES];
}

export async function updateMatchScoreMock(
  matchId: number,
  scoreA: number,
  scoreB: number,
): Promise<Match> {
  const match = MOCK_MATCHES.find((item) => item.id === matchId);

  if (!match) {
    throw new ApiError(404, 'Match introuvable.');
  }

  // Même règle que services/match.py : un score déjà saisi ne se réécrit pas.
  if (match.status === 'played') {
    throw new ApiError(409, "Impossible d'enregistrer un score sur un match déjà joué.");
  }

  match.score_a = scoreA;
  match.score_b = scoreB;
  match.status = 'played';

  return { ...match };
}

// Authentification fictive. Elle accepte n'importe quel identifiant avec un
// mot de passe non vide : en mode repli, le but est de parcourir l'interface,
// pas de contrôler un accès. Aucun mot de passe n'est donc écrit dans le code.
const MOCK_TOKEN = 'mock-arena-token';

let mockUser: User | null = null;

export async function loginMock(identifier: string, password: string): Promise<string> {
  await new Promise((resolve) => setTimeout(resolve, 300));

  if (identifier.trim() === '' || password === '') {
    throw new ApiError(401, 'Identifiants invalides.');
  }

  const username = identifier.includes('@') ? identifier.split('@')[0] : identifier;

  mockUser = {
    id: 1,
    username,
    email: identifier.includes('@') ? identifier : `${identifier}@arena.fr`,
    role: 'admin',
    created_at: '2026-09-01T10:00:00Z',
  };

  return MOCK_TOKEN;
}

export async function getMeMock(token: string): Promise<User> {
  // Après un F5, mockUser est perdu (variable de module) : on restaure un
  // utilisateur générique tant que le jeton fictif est présent.
  if (token !== MOCK_TOKEN) {
    throw new ApiError(401, "Impossible de valider l'authentification.");
  }

  return (
    mockUser ?? {
      id: 1,
      username: 'invite',
      email: 'invite@arena.fr',
      role: 'admin',
      created_at: '2026-09-01T10:00:00Z',
    }
  );
}