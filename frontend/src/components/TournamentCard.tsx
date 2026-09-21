import Card from "./Card";
import StatusBadge from "./StatusBadge";
import type { Tournament } from "../types";

interface TournamentCardProps {
  tournament: Tournament;
  gameName: string;
}

function TournamentCard({
  tournament,
  gameName,
}: TournamentCardProps) {
  const badgeStatus =
    tournament.status === "upcoming" ? "open" : tournament.status;

  return (
    <Card
      title={tournament.name}
      subtitle={gameName}
      badge={<StatusBadge status={badgeStatus} />}
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