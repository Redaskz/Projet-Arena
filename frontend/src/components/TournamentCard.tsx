import Card from "./Card";
import type { Tournament } from "../types";

interface TournamentCardProps {
  tournament: Tournament;
  gameName: string;
}

function TournamentCard({
  tournament,
  gameName,
}: TournamentCardProps) {
  return (
    <Card
      title={tournament.name}
      subtitle={gameName}
      badge={tournament.status}
    >
      <p>
        Début :{" "}
        {new Date(tournament.startDate).toLocaleDateString("fr-FR")}
      </p>

      <p>
        Équipes : {tournament.maxTeams} maximum
      </p>
    </Card>
  );
}

export default TournamentCard;