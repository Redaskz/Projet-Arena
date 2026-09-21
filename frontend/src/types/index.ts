export interface Game {
  id: number;
  name: string;
  slug: string;
  description: string;
}

export interface Team {
  id: number;
  name: string;
  tag: string;
  gameId: number;
  captainId: number;
}

export interface Tournament {
  id: number;
  name: string;
  gameId: number;
  status: 'upcoming' | 'ongoing' | 'finished';
  startDate: string;
  maxTeams: number;
}

export interface Match {
  id: number;
  tournamentId: number;
  round: number;
  teamAId: number;
  teamBId: number;
  scoreA: number | null;
  scoreB: number | null;
  status: 'scheduled' | 'played';
  scheduledAt: string;
}

export interface Comment {
  id: number;
  tournamentId: number;
  userId: number;
  content: string;
  createdAt: string;
}

export interface Registration {
  id: number;
  tournamentId: number;
  teamId: number;
  status: 'pending' | 'accepted' | 'rejected';
  registeredAt: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'player' | 'admin';
}