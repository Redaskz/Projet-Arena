import { GENRE_LABELS } from '../api/games';
import type { GameDetails } from '../api/games';
import Card from './Card';

interface GameCardProps {
  game: GameDetails;
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
      subtitle={game.platform ?? 'Plateforme non précisée'}
      // ?? et pas || : on ne remplace que null/undefined, jamais une chaîne valide.
      imageUrl={game.cover_url ?? PLACEHOLDER_COVER}
      badge={GENRE_LABELS[game.genre]}
    >
      <p>
        {game.team_size} {playersLabel} par équipe
      </p>
    </Card>
  );
}

export default GameCard;
