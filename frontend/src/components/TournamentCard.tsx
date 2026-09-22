import { Link } from "react-router-dom";
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
  // StatusBadge utilise des statuts génériques. "upcoming" est donc
  // représenté par "open" pour conserver un badge déjà prévu par le socle.
  const badgeStatus =
    tournament.status === "upcoming" ? "open" : tournament.status;

  return (
    <Link
      to={`/tournaments/${tournament.id}`}
      style={{
        textDecoration: "none",
        color: "inherit",
      }}
    >
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
    </Link>
  );
}

export default TournamentCard;