import { useMemo, useState } from 'react';
import { patch } from '../api/client';
import ErrorMessage from '../components/ErrorMessage';
import Loader from '../components/Loader';
import MatchRow from '../components/MatchRow';
import StandingsTable, {
  type Standing,
} from '../components/StandingsTable';
import { useFetch } from '../hooks/useFetch';
import type { Match, Team } from '../types';

type MatchFilter = 'all' | 'scheduled' | 'played';

interface ScoreForm {
  scoreA: string;
  scoreB: string;
}

function MatchesPage() {
  const {
    data: matches,
    loading,
    error,
    refetch,
  } = useFetch<Match[]>('/matches');

  const {
    data: teams,
    loading: teamsLoading,
    error: teamsError,
  } = useFetch<Team[]>('/teams');

  const [filter, setFilter] = useState<MatchFilter>('all');
  const [scores, setScores] = useState<Record<number, ScoreForm>>({});
  const [savingMatchId, setSavingMatchId] = useState<number | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  const filteredMatches = useMemo(() => {
    if (!matches) {
      return [];
    }

    if (filter === 'all') {
      return matches;
    }

    return matches.filter((match) => match.status === filter);
  }, [matches, filter]);

  const standings = useMemo<Standing[]>(() => {
    if (!matches || !teams) {
      return [];
    }

    const calculatedStandings = teams.map((team) => {
      const teamMatches = matches.filter(
        (match) =>
          match.status === 'played' &&
          (match.team_a_id === team.id ||
            match.team_b_id === team.id),
      );

      let wins = 0;
      let draws = 0;
      let losses = 0;
      let points = 0;
      let difference = 0;

      teamMatches.forEach((match) => {
        const isTeamA = match.team_a_id === team.id;
        const teamScore = isTeamA ? match.score_a : match.score_b;
        const opponentScore = isTeamA
          ? match.score_b
          : match.score_a;

        if (teamScore === null || opponentScore === null) {
          return;
        }

        difference += teamScore - opponentScore;

        if (teamScore > opponentScore) {
          wins += 1;
          points += 3;
        } else if (teamScore === opponentScore) {
          draws += 1;
          points += 1;
        } else {
          losses += 1;
        }
      });

      return {
        team,
        played: teamMatches.length,
        wins,
        draws,
        losses,
        points,
        difference,
      };
    });

    return calculatedStandings.sort((a, b) => {
      if (b.points !== a.points) {
        return b.points - a.points;
      }

      if (b.difference !== a.difference) {
        return b.difference - a.difference;
      }

      return b.wins - a.wins;
    });
  }, [matches, teams]);

  const getTeam = (teamId: number): Team | undefined => {
    return teams?.find((team) => team.id === teamId);
  };

  const handleScoreChange = (
    matchId: number,
    field: 'scoreA' | 'scoreB',
    value: string,
  ) => {
    setScores((currentScores) => ({
      ...currentScores,
      [matchId]: {
        scoreA: currentScores[matchId]?.scoreA ?? '',
        scoreB: currentScores[matchId]?.scoreB ?? '',
        [field]: value,
      },
    }));
  };

  const handleScoreSubmit = async (match: Match): Promise<void> => {
    const score = scores[match.id];

    if (!score) {
      return;
    }

    const scoreA = Number(score.scoreA);
    const scoreB = Number(score.scoreB);

    if (
      score.scoreA === '' ||
      score.scoreB === '' ||
      !Number.isInteger(scoreA) ||
      !Number.isInteger(scoreB) ||
      scoreA < 0 ||
      scoreB < 0
    ) {
      setSaveError(
        'Les scores doivent être des entiers supérieurs ou égaux à 0.',
      );
      return;
    }

    setSavingMatchId(match.id);
    setSaveError(null);

    try {
      await patch<Match>(`/matches/${match.id}`, {
        score_a: scoreA,
        score_b: scoreB,
        status: 'played',
      });

      setScores((currentScores) => {
        const nextScores = { ...currentScores };
        delete nextScores[match.id];
        return nextScores;
      });

      refetch();
    } catch (requestError: unknown) {
      if (requestError instanceof Error) {
        setSaveError(requestError.message);
      } else {
        setSaveError('Impossible d’enregistrer le score.');
      }
    } finally {
      setSavingMatchId(null);
    }
  };

  if (loading || teamsLoading) {
    return <Loader />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (teamsError) {
    return <ErrorMessage message={teamsError} />;
  }

  if (!matches || !teams) {
    return <ErrorMessage message="Aucun match disponible." />;
  }

  return (
    <>
      <h1>Matchs</h1>

      <section>
        <label htmlFor="match-filter">Filtrer les matchs :</label>

        <select
          id="match-filter"
          value={filter}
          onChange={(event) =>
            setFilter(event.target.value as MatchFilter)
          }
        >
          <option value="all">Tous</option>
          <option value="scheduled">À jouer</option>
          <option value="played">Terminés</option>
        </select>
      </section>

      {saveError && <ErrorMessage message={saveError} />}

      <section>
        <h2>Liste des matchs</h2>

        {filteredMatches.length === 0 ? (
          <p>Aucun match ne correspond au filtre.</p>
        ) : (
          filteredMatches.map((match) => {
            const teamA = getTeam(match.team_a_id);
            const teamB = getTeam(match.team_b_id);

            if (!teamA || !teamB) {
              return null;
            }

            return (
              <div key={match.id}>
                <MatchRow
                  match={match}
                  teamA={teamA}
                  teamB={teamB}
                />

                {match.status !== 'played' && (
                  <form
                    onSubmit={(event) => {
                      event.preventDefault();
                      void handleScoreSubmit(match);
                    }}
                  >
                    <label htmlFor={`score-a-${match.id}`}>
                      {teamA.name}
                    </label>

                    <input
                      id={`score-a-${match.id}`}
                      type="number"
                      min="0"
                      step="1"
                      value={scores[match.id]?.scoreA ?? ''}
                      onChange={(event) =>
                        handleScoreChange(
                          match.id,
                          'scoreA',
                          event.target.value,
                        )
                      }
                    />

                    <label htmlFor={`score-b-${match.id}`}>
                      {teamB.name}
                    </label>

                    <input
                      id={`score-b-${match.id}`}
                      type="number"
                      min="0"
                      step="1"
                      value={scores[match.id]?.scoreB ?? ''}
                      onChange={(event) =>
                        handleScoreChange(
                          match.id,
                          'scoreB',
                          event.target.value,
                        )
                      }
                    />

                    <button
                      type="submit"
                      disabled={savingMatchId === match.id}
                    >
                      {savingMatchId === match.id
                        ? 'Enregistrement...'
                        : 'Enregistrer le score'}
                    </button>
                  </form>
                )}
              </div>
            );
          })
        )}
      </section>

      <section>
        <h2>Classement</h2>
        <StandingsTable standings={standings} />
      </section>
    </>
  );
}

export default MatchesPage;