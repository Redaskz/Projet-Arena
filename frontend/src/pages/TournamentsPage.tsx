import { useMemo } from "react";
import Card from "../components/Card";
import ErrorMessage from "../components/ErrorMessage";
import Loader from "../components/Loader";
import TournamentCard from "../components/TournamentCard";
import TournamentFilters from "../components/TournamentFilters";
import useLocalStorage from "../hooks/useLocalStorage";
import { getMockGames, getMockTournaments, USE_MOCKS } from "../mocks";
import type { Tournament } from "../types";

interface TournamentsPageProps {}

function TournamentsPage({}: TournamentsPageProps) {
  const [selectedGameId, setSelectedGameId] = useLocalStorage<string>(
    "tournaments.game",
    "all",
  );

  const [selectedStatus, setSelectedStatus] = useLocalStorage<string>(
    "tournaments.status",
    "all",
  );

  // Le chargement est actuellement géré avec les données mockées.
  // On garde ces variables pour conserver la même structure lorsque l'API
  // remplacera les mocks.
  const loading = false;
  const error: string | null = null;

  const tournaments: Tournament[] = USE_MOCKS
    ? getMockTournaments()
    : [];

  const games = USE_MOCKS ? getMockGames() : [];

  const filteredTournaments = useMemo(() => {
    return tournaments.filter((tournament: Tournament) => {
      // Les types du projet reproduisent exactement les réponses du backend,
      // donc les identifiants doivent rester en snake_case.
      const gameMatches =
        selectedGameId === "all" ||
        tournament.gameId === Number(selectedGameId);

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
          {filteredTournaments.map((tournament: Tournament) => {
            // On cherche le nom du jeu à partir de l'identifiant renvoyé
            // par le backend plutôt que d'afficher uniquement son ID.
            const game = games.find(
              (item) => item.id === tournament.gameId,
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