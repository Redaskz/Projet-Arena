import { post } from './client';
import type { Team } from '../types';
import { USE_MOCKS, createTeamMock } from '../mocks';

// Ce que le client envoie pour créer une équipe (schéma TeamCreate du backend).
// Pas d'id ni de created_at : ce sont des champs remplis par le serveur.
// captain_id, lui, est obligatoire côté API : le formulaire y met l'utilisateur
// connecté, qui devient capitaine de l'équipe qu'il crée.
export interface TeamCreate {
  name: string;
  tag: string;
  game_id: number;
  captain_id: number;
}

// Les composants n'appellent jamais fetch : ils appellent createTeam, qui passe
// par client.ts. En cas de refus, client.ts lève un ApiError qui garde le
// statut HTTP (409, 422...) : c'est ce qui permet au formulaire de réagir au 409.
// POST /teams est protégé : client.ts y joint le jeton de la session.
export function createTeam(payload: TeamCreate): Promise<Team> {
  if (USE_MOCKS) {
    return createTeamMock(payload);
  }
  return post<Team>('/teams', payload);
}
