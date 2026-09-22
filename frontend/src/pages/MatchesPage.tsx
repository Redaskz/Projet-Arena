import { useMemo, useState } from 'react';
import ErrorMessage from '../components/ErrorMessage';
import Loader from '../components/Loader';
import MatchRow from '../components/MatchRow';
import StandingsTable, {
  type Standing,
} from '../components/StandingsTable';
import {
  getMockMatches,
  getMockTeams,
} from '../mocks';
import type { Match, Team } from '../types';

type MatchFilter = 'all' | 'scheduled' | 'played';

interface ScoreForm {
  scoreA: string;
  scoreB: string;
}

// Pas d'interface de props : la page est affichée par le routeur sans aucune
// prop, comme GamesPage et TeamsPage. Une interface vide faisait échouer le lint.
function MatchesPage() {
  const [matches, setMatches] = useState<Match[]>(getMockMatches);
  const [teams] = useState<Team[]>(getMockTeams);

  const [filter, setFilter] = useState<MatchFilter>('all');
  const [scores, setScores] = useState<Record<number, ScoreForm>>({});
  const [saveError, setSaveError] = useState<string | null>(null);

  // Ces états gardent les branches demandées par le projet même avec les mocks.
  const loading = false;
  const error: string | null = null;

  const filteredMatches = useMemo(() => {
    if (filter === 'all') {
      return matches;
    }

    return matches.filter((match) => match.status === filter);
  }, [matches, filter]);

  const standings = useMemo<Standing[]>(() => {
    return teams
      .map((team) => {
        const teamMatches = matches.filter(
          (match) =>
            match.status === 'played' &&
            (match.team_a_id === team.id || match.team_b_id === team.id),
        );

        let wins = 0;
        let draws = 0;
        let losses = 0;
        let points = 0;
        let difference = 0;

        teamMatches.forEach((match) => {
          const isTeamA = match.team_a_id === team.id;
          const teamScore = isTeamA ? match.score_a : match.score_b;
          const opponentScore = isTeamA ? match.score_b : match.score_a;

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
      })
      .sort(
        (a, b) =>
          b.points - a.points ||
          b.difference - a.difference ||
          b.wins - a.wins,
      );
  }, [matches, teams]);

  const getTeam = (id: number): Team | undefined =>
    teams.find((team) => team.id === id);

  const handleScoreChange = (
    matchId: number,
    field: 'scoreA' | 'scoreB',
    value: string,
  ): void => {
    setScores((current) => ({
      ...current,
      [matchId]: {
        scoreA: current[matchId]?.scoreA ?? '',
        scoreB: current[matchId]?.scoreB ?? '',
        [field]: value,
      },
    }));
  };

  const handleScoreSubmit = (match: Match): void => {
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
      setSaveError('Les scores doivent être des entiers positifs ou nuls.');
      return;
    }

    // On modifie le mock local pour simuler la réponse du backend.
    setMatches((current) =>
      current.map((currentMatch) =>
        currentMatch.id === match.id
          ? {
              ...currentMatch,
              score_a: scoreA,
              score_b: scoreB,
              status: 'played',
            }
          : currentMatch,
      ),
    );

    setScores((current) => {
      const next = { ...current };
      delete next[match.id];
      return next;
    });

    setSaveError(null);
  };

  if (loading) {
    return <Loader />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (!matches || !teams) {
    return <ErrorMessage message="Aucun match disponible." />;
  }

  return (
    <>
      <h1>Matchs</h1>

      <section>
        <label htmlFor="match-filter">Filtrer les matchs : </label>

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

                {match.status === 'scheduled' && (
                  <form
                    onSubmit={(event) => {
                      event.preventDefault();
                      handleScoreSubmit(match);
                    }}
                  >
                    <label htmlFor={`score-a-${match.id}`}>
                      {teamA.name}
                    </label>

                    <input
                      id={`score-a-${match.id}`}
                      type="number"
                      min="0"
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
                      value={scores[match.id]?.scoreB ?? ''}
                      onChange={(event) =>
                        handleScoreChange(
                          match.id,
                          'scoreB',
                          event.target.value,
                        )
                      }
                    />

                    <button type="submit">
                      Enregistrer le score
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