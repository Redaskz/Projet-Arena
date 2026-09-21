import type { Team } from '../types';

export interface Standing {
  team: Team;
  played: number;
  wins: number;
  draws: number;
  losses: number;
  points: number;
  difference: number;
}

interface StandingsTableProps {
  standings: Standing[];
}

function StandingsTable({ standings }: StandingsTableProps) {
  return (
    <table>
      <thead>
        <tr>
          <th>Équipe</th>
          <th>J</th>
          <th>V</th>
          <th>N</th>
          <th>D</th>
          <th>Pts</th>
          <th>Diff.</th>
        </tr>
      </thead>

      <tbody>
        {standings.map((standing) => (
          <tr key={standing.team.id}>
            <td>{standing.team.name}</td>
            <td>{standing.played}</td>
            <td>{standing.wins}</td>
            <td>{standing.draws}</td>
            <td>{standing.losses}</td>
            <td>{standing.points}</td>
            <td>{standing.difference}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default StandingsTable;