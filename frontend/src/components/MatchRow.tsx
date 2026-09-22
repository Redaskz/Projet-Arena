import type { Match, Team } from '../types';

interface MatchRowProps {
  match: Match;
  teamA: Team;
  teamB: Team;
}

function MatchRow({ match, teamA, teamB }: MatchRowProps) {
  return (
    <article>
      <div>
        <strong>{teamA.name}</strong>
        <span> {match.score_a ?? '-'} </span>
        <span> - </span>
        <span>{match.score_b ?? '-'}</span>
        <strong> {teamB.name}</strong>
      </div>

      <p>
        {match.status === 'played'
          ? 'Match terminé'
          : 'Match à jouer'}
      </p>
    </article>
  );
}

export default MatchRow;