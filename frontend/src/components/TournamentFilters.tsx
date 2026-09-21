import type { Game } from "../types";

interface TournamentFiltersProps {
  games: Game[];
  selectedGameId: string;
  selectedStatus: string;
  onGameChange: (gameId: string) => void;
  onStatusChange: (status: string) => void;
}

function TournamentFilters({
  games,
  selectedGameId,
  selectedStatus,
  onGameChange,
  onStatusChange,
}: TournamentFiltersProps) {
  return (
    <div className="tournament-filters">
      <label>
        Jeu
        <select
          value={selectedGameId}
          onChange={(event) => onGameChange(event.target.value)}
        >
          <option value="all">Tous les jeux</option>

          {games.map((game) => (
            <option key={game.id} value={game.id}>
              {game.name}
            </option>
          ))}
        </select>
      </label>

      <label>
        Statut
        <select
          value={selectedStatus}
          onChange={(event) => onStatusChange(event.target.value)}
        >
          <option value="all">Tous les statuts</option>
          <option value="upcoming">À venir</option>
          <option value="ongoing">En cours</option>
          <option value="finished">Terminés</option>
        </select>
      </label>
    </div>
  );
}

export default TournamentFilters;