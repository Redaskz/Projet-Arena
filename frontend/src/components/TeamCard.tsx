import type { Team } from '../types';
import Card from './Card';

interface TeamCardProps {
  team: Team;
  // Le nom du jeu est passé par la page, pas cherché ici : une équipe ne
  // contient que gameId, et c'est la page qui a déjà la liste des jeux.
  // La carte reste purement affichage, sans requête ni recherche.
  gameName: string;
}

function TeamCard({ team, gameName }: TeamCardProps) {
  return <Card title={team.name} subtitle={gameName} badge={team.tag} />;
}

export default TeamCard;
