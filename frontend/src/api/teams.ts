import { post } from './client';
import type { Team } from '../types';
import { USE_MOCKS, createTeamMock } from '../mocks';

// Ce que le client envoie pour créer une équipe. Pas d'id ni de captainId :
// ce sont des champs remplis par le serveur, le client n'a pas à les inventer.
export interface TeamCreate {
  name: string;
  tag: string;
  gameId: number;
}

// Les composants n'appellent jamais fetch : ils appellent createTeam, qui passe
// par client.ts. En cas de refus, client.ts lève un ApiError qui garde le
// statut HTTP (409, 422...) : c'est ce qui permet au formulaire de réagir au 409.
export function createTeam(payload: TeamCreate): Promise<Team> {
  // TODO: provisoire — POST /teams n'existe pas encore côté backend.
  if (USE_MOCKS) {
    return createTeamMock(payload);
  }
  return post<Team>('/teams', payload);
}
