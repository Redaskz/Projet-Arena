import type { Match, Team } from '../types';

interface MatchRowProps {
  match: Match;
  teamA: Team;
  teamB: Team;
  onScoreSaved?: () => void;
}

function MatchRow({
  match,
  teamA,
  teamB,
  onScoreSaved,
}: MatchRowProps) {
  return (
    <article>
      <div>
        <strong>{teamA.name}</strong>
        <span> {match.scoreA ?? '-'} </span>
        <span> - </span>
        <span>{match.scoreB ?? '-'}</span>
        <strong> {teamB.name}</strong>
      </div>

      <p>
        {match.status === 'played'
          ? 'Match terminé'
          : 'Match à jouer'}
      </p>

      {onScoreSaved && (
        <button type="button" onClick={onScoreSaved}>
          Actualiser
        </button>
      )}
    </article>
  );
}

export default MatchRow;