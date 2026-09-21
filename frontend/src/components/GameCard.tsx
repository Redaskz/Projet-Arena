import { getGenreLabel } from '../api/games';
import type { Game } from '../types';
import Card from './Card';

interface GameCardProps {
  game: Game;
}

// Image affichée quand RAWG n'a pas fourni de jaquette (cover_url à null).
// Le fichier est dans public/, donc servi tel quel à la racine du site.
const PLACEHOLDER_COVER = '/game-placeholder.svg';

// GameCard ne fait que traduire un jeu en props de Card :
// toute la mise en page est dans Card, réutilisée par le reste du groupe.
function GameCard({ game }: GameCardProps) {
  // "1 joueur" / "5 joueurs" : on accorde le pluriel.
  const playersLabel = game.team_size > 1 ? 'joueurs' : 'joueur';

  return (
    <Card
      title={game.name}
      // `||` et pas `??` : platform est typé string, mais le backend peut
      // renvoyer null (champ facultatif) ou une chaîne vide. `||` couvre les deux.
      subtitle={game.platform || 'Plateforme non précisée'}
      // `??` ici : on ne remplace que null, jamais une URL valide.
      imageUrl={game.cover_url ?? PLACEHOLDER_COVER}
      badge={getGenreLabel(game.genre)}
    >
      <p>
        {game.team_size} {playersLabel} par équipe
      </p>
    </Card>
  );
}

export default GameCard;
