import { GENRE_LABELS, isGameGenre } from '../api/games';
import ErrorMessage from '../components/ErrorMessage';
import FilterSelect from '../components/FilterSelect';
import GameCard from '../components/GameCard';
import Loader from '../components/Loader';
import { useFetch } from '../hooks/useFetch';
import useLocalStorage from '../hooks/useLocalStorage';
import { MOCK_GAMES, USE_MOCKS, mockFetchState } from '../mocks';
import type { Game } from '../types';

// Options du filtre calculées une seule fois, hors du composant :
// la liste des genres est fixe (enum du backend), elle ne dépend pas des données.
const GENRE_OPTIONS = Object.entries(GENRE_LABELS).map(([value, label]) => ({ value, label }));

function GamesPage() {
  const fetched = useFetch<Game[]>('/games');
  // TODO: provisoire — données fictives tant que GET /games n'est pas branché.
  const { data: games, loading, error } = USE_MOCKS ? mockFetchState(MOCK_GAMES) : fetched;

  // Le genre choisi est gardé dans localStorage : après un F5, le filtre est
  // toujours appliqué. 'all' = pas de filtre.
  const [genre, setGenre] = useLocalStorage<string>('arena.games.genre', 'all');

  // Protection : si localStorage contient un genre qui n'existe plus
  // (valeur modifiée à la main, ancien genre supprimé...), on repart sur 'all'
  // au lieu d'afficher une liste vide incompréhensible.
  const activeGenre = isGameGenre(genre) ? genre : 'all';

  // État 1 : chargement.
  if (loading) {
    return <Loader />;
  }

  // État 2 : erreur. Le message est celui renvoyé par l'API (champ detail),
  // transmis par ApiError dans client.ts puis par useFetch.
  // `!games` sert aussi à TypeScript : après ce if, games n'est plus null.
  if (error || !games) {
    return <ErrorMessage message={error ?? 'Aucune donnée reçue.'} />;
  }

  // Filtre calculé à chaque rendu, sans useMemo : la liste est petite,
  // le coût est négligeable et le code reste plus simple à lire.
  const visibleGames =
    activeGenre === 'all' ? games : games.filter((game) => game.genre === activeGenre);

  // État 3 : succès (avec le cas particulier de la liste vide).
  return (
    <section>
      <h1>Catalogue des jeux</h1>

      <FilterSelect
        id="genre-filter"
        label="Genre :"
        allLabel="Tous les genres"
        value={activeGenre}
        options={GENRE_OPTIONS}
        onChange={setGenre}
      />

      {visibleGames.length === 0 ? (
        <p>
          {games.length === 0 ? 'Aucun jeu dans le catalogue.' : 'Aucun jeu pour ce genre.'}
        </p>
      ) : (
        <div className="card-grid">
          {visibleGames.map((game) => (
            <GameCard key={game.id} game={game} />
          ))}
        </div>
      )}
    </section>
  );
}

export default GamesPage;
