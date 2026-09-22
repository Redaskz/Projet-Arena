import { useMemo } from "react";
import ErrorMessage from "../components/ErrorMessage";
import Loader from "../components/Loader";
import TournamentCard from "../components/TournamentCard";
import TournamentFilters from "../components/TournamentFilters";
import { useFetch } from "../hooks/useFetch";
import useLocalStorage from "../hooks/useLocalStorage";
import {
  getMockGames,
  getMockTournaments,
  USE_MOCKS,
} from "../mocks";
import type { Game, Tournament } from "../types";

function TournamentsPage() {
  const [selectedGameId, setSelectedGameId] = useLocalStorage<string>(
    "tournaments.game",
    "all",
  );

  const [selectedStatus, setSelectedStatus] = useLocalStorage<string>(
    "tournaments.status",
    "all",
  );

  const {
    data: apiTournaments,
    loading: apiLoading,
    error: apiError,
  } = useFetch<Tournament[]>("/tournaments");

  const {
    data: apiGames,
    loading: gamesLoading,
    error: gamesError,
  } = useFetch<Game[]>("/games");

  // Les mocks permettent de tester l'interface même lorsque le backend
  // n'est pas disponible pendant le développement frontend.
  const tournaments = USE_MOCKS
    ? getMockTournaments()
    : (apiTournaments ?? []);

  const games = USE_MOCKS
    ? getMockGames()
    : (apiGames ?? []);

  const loading = USE_MOCKS
    ? false
    : apiLoading || gamesLoading;

  const error = USE_MOCKS
    ? null
    : apiError ?? gamesError;

  const filteredTournaments = useMemo(() => {
    return tournaments.filter((tournament) => {
      // Les types reproduisent les réponses du backend :
      // on utilise donc game_id plutôt qu'un nom différent côté frontend.
      const gameMatches =
        selectedGameId === "all" ||
        tournament.game_id === Number(selectedGameId);

      const statusMatches =
        selectedStatus === "all" ||
        tournament.status === selectedStatus;

      return gameMatches && statusMatches;
    });
  }, [tournaments, selectedGameId, selectedStatus]);

  if (loading) {
    return <Loader />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <main>
      <h1>Tournois</h1>

      <TournamentFilters
        games={games}
        selectedGameId={selectedGameId}
        selectedStatus={selectedStatus}
        onGameChange={setSelectedGameId}
        onStatusChange={setSelectedStatus}
      />

      {filteredTournaments.length === 0 ? (
        <p>Aucun tournoi ne correspond aux filtres sélectionnés.</p>
      ) : (
        <section
          className="tournament-grid"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
            gap: "1rem",
          }}
        >
          {filteredTournaments.map((tournament) => {
            // On retrouve le jeu grâce à l'identifiant fourni par le backend
            // afin d'afficher son nom plutôt que son identifiant numérique.
            const game = games.find(
              (item) => item.id === tournament.game_id,
            );

            return (
              <TournamentCard
                key={tournament.id}
                tournament={tournament}
                gameName={game?.name ?? "Jeu inconnu"}
              />
            );
          })}
        </section>
      )}
    </main>
  );
}

export default TournamentsPage;