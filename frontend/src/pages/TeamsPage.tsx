import type { GameDetails } from '../api/games';
import ErrorMessage from '../components/ErrorMessage';
import FilterSelect from '../components/FilterSelect';
import Loader from '../components/Loader';
import TeamCard from '../components/TeamCard';
import TeamCreateForm from '../components/TeamCreateForm';
import { useFetch } from '../hooks/useFetch';
import useLocalStorage from '../hooks/useLocalStorage';
import { MOCK_GAMES, USE_MOCKS, getMockTeams, mockFetchState } from '../mocks';
import type { Team } from '../types';

function TeamsPage() {
  // refetch vient toujours du vrai useFetch : l'appeler provoque un nouveau
  // rendu de la page, qui relit alors la liste (vraie ou fictive).
  const { refetch, ...fetchedTeams } = useFetch<Team[]>('/teams');
  const fetchedGames = useFetch<GameDetails[]>('/games');

  // TODO: provisoire — données fictives tant que /teams et /games ne répondent pas.
  const teamsState = USE_MOCKS ? mockFetchState(getMockTeams()) : fetchedTeams;
  const gamesState = USE_MOCKS ? mockFetchState(MOCK_GAMES) : fetchedGames;
  const { data: teams } = teamsState;
  const { data: games } = gamesState;

  // Filtre par jeu mémorisé comme sur GamesPage. On stocke l'id en texte
  // ('3') parce que c'est ce que renvoie un <select>. 'all' = pas de filtre.
  const [gameFilter, setGameFilter] = useLocalStorage<string>('arena.teams.game', 'all');

  // État 1 : chargement. `&& !teams` : le Loader ne s'affiche qu'au premier
  // chargement. Après une création, le refetch recharge la liste en gardant
  // l'ancienne affichée, sans faire disparaître la page.
  if ((teamsState.loading && !teams) || gamesState.loading) {
    return <Loader />;
  }

  // État 2 : erreur, sur l'une ou l'autre des deux requêtes.
  const error = teamsState.error ?? gamesState.error;
  if (error || !teams || !games) {
    return <ErrorMessage message={error ?? 'Aucune donnée reçue.'} />;
  }

  // Une équipe ne connaît que l'id de son jeu : on cherche son nom dans la liste.
  function getGameName(gameId: number): string {
    return games?.find((game) => game.id === gameId)?.name ?? 'Jeu inconnu';
  }

  const gameOptions = games.map((game) => ({ value: String(game.id), label: game.name }));

  // Même protection que GamesPage : un jeu mémorisé qui n'existe plus → 'all'.
  const activeFilter = gameOptions.some((option) => option.value === gameFilter)
    ? gameFilter
    : 'all';

  const visibleTeams =
    activeFilter === 'all'
      ? teams
      : teams.filter((team) => String(team.gameId) === activeFilter);

  // État 3 : succès.
  return (
    <section>
      <h1>Équipes</h1>

      <TeamCreateForm games={games} onCreated={refetch} />

      <h2>Liste des équipes</h2>

      <FilterSelect
        id="team-game-filter"
        label="Jeu :"
        allLabel="Tous les jeux"
        value={activeFilter}
        options={gameOptions}
        onChange={setGameFilter}
      />

      {visibleTeams.length === 0 ? (
        <p>{teams.length === 0 ? 'Aucune équipe pour le moment.' : 'Aucune équipe pour ce jeu.'}</p>
      ) : (
        <div className="card-grid">
          {visibleTeams.map((team) => (
            <TeamCard key={team.id} team={team} gameName={getGameName(team.gameId)} />
          ))}
        </div>
      )}
    </section>
  );
}

export default TeamsPage;
