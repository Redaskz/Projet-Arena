// TODO: provisoire — tout ce dossier disparaît quand le backend servira
// les vraies données. Il suffira de passer USE_MOCKS à false.

import type { Game, Team, Tournament } from "../types";

export const USE_MOCKS: boolean = true;

export const MOCK_GAMES: Game[] = [
  {
    id: 1,
    name: "Counter-Strike 2",
    slug: "counter-strike-2",
    description: "FPS compétitif",
  },
  {
    id: 2,
    name: "Valorant",
    slug: "valorant",
    description: "FPS tactique compétitif",
  },
  {
    id: 3,
    name: "League of Legends",
    slug: "league-of-legends",
    description: "MOBA compétitif",
  },
  {
    id: 4,
    name: "EA Sports FC 25",
    slug: "ea-sports-fc-25",
    description: "Jeu de football",
  },
  {
    id: 5,
    name: "Street Fighter 6",
    slug: "street-fighter-6",
    description: "Jeu de combat",
  },
  {
    id: 6,
    name: "Fortnite",
    slug: "fortnite",
    description: "Battle Royale",
  },
];

export const MOCK_TEAMS: Team[] = [
  {
    id: 1,
    name: "Team Vitality",
    tag: "VIT",
    gameId: 1,
    captainId: 1,
  },
  {
    id: 2,
    name: "Karmine Corp",
    tag: "KC",
    gameId: 3,
    captainId: 2,
  },
  {
    id: 3,
    name: "Gentle Mates",
    tag: "M8",
    gameId: 2,
    captainId: 3,
  },
];

export const MOCK_TOURNAMENTS: Tournament[] = [
  {
    id: 1,
    name: "Arena Masters CS2",
    gameId: 1,
    status: "upcoming",
    startDate: "2026-10-05T18:00:00",
    maxTeams: 16,
  },
  {
    id: 2,
    name: "Valorant Winter Cup",
    gameId: 2,
    status: "ongoing",
    startDate: "2026-09-20T18:00:00",
    maxTeams: 16,
  },
  {
    id: 3,
    name: "League of Legends Championship",
    gameId: 3,
    status: "finished",
    startDate: "2026-08-15T14:00:00",
    maxTeams: 32,
  },
  {
    id: 4,
    name: "FC 25 Arena Cup",
    gameId: 4,
    status: "upcoming",
    startDate: "2026-10-12T15:00:00",
    maxTeams: 16,
  },
  {
    id: 5,
    name: "Street Fighter Open",
    gameId: 5,
    status: "ongoing",
    startDate: "2026-09-18T19:00:00",
    maxTeams: 32,
  },
  {
    id: 6,
    name: "Fortnite Battle Arena",
    gameId: 6,
    status: "finished",
    startDate: "2026-07-20T16:00:00",
    maxTeams: 24,
  },
  {
    id: 7,
    name: "CS2 Community Cup",
    gameId: 1,
    status: "ongoing",
    startDate: "2026-09-19T17:00:00",
    maxTeams: 8,
  },
  {
    id: 8,
    name: "Valorant Open Series",
    gameId: 2,
    status: "upcoming",
    startDate: "2026-10-20T18:00:00",
    maxTeams: 32,
  },
  {
    id: 9,
    name: "League Arena Masters",
    gameId: 3,
    status: "finished",
    startDate: "2026-08-30T16:00:00",
    maxTeams: 16,
  },
  {
    id: 10,
    name: "Fortnite Pro Cup",
    gameId: 6,
    status: "upcoming",
    startDate: "2026-10-25T20:00:00",
    maxTeams: 16,
  },
];

export function getMockGames(): Game[] {
  return [...MOCK_GAMES];
}

export function getMockTeams(): Team[] {
  return [...MOCK_TEAMS];
}

export function getMockTournaments(): Tournament[] {
  return [...MOCK_TOURNAMENTS];
}