import type { CSSProperties } from "react";
import type {
  MatchStatus,
  RegistrationStatus,
  TournamentStatus,
} from "../types";

// Union construite à partir des enums de l'API plutôt que recopiée à la main :
// si le backend ajoute un statut et qu'on le reporte dans types/index.ts, les
// deux Record ci-dessous refusent de compiler tant qu'il n'a ni style ni libellé.
// À l'inverse, une valeur qui n'existe pas côté API ("open", "draft") n'est plus
// acceptée nulle part.
type Status = TournamentStatus | MatchStatus | RegistrationStatus;

interface StatusBadgeProps {
  status: Status;
}

interface BadgeStyle {
  backgroundColor: string;
  color: string;
}

const statusStyles: Record<Status, BadgeStyle> = {
  upcoming: {
    backgroundColor: "#fef3c7",
    color: "#92400e",
  },
  ongoing: {
    backgroundColor: "#dbeafe",
    color: "#1d4ed8",
  },
  finished: {
    backgroundColor: "#ede9fe",
    color: "#6d28d9",
  },
  scheduled: {
    backgroundColor: "#dbeafe",
    color: "#1d4ed8",
  },
  played: {
    backgroundColor: "#e5e7eb",
    color: "#374151",
  },
  pending: {
    backgroundColor: "#fef3c7",
    color: "#92400e",
  },
  accepted: {
    backgroundColor: "#dcfce7",
    color: "#166534",
  },
  rejected: {
    backgroundColor: "#fee2e2",
    color: "#b91c1c",
  },
};

// Libellés français affichés dans le badge : le backend envoie les statuts en
// anglais, alors que toute l'interface est en français.
// Même principe que GENRE_LABELS dans api/games.ts : avec Record<Status, string>,
// TypeScript refuse de compiler si un statut du type Status n'a pas de libellé.
const STATUS_LABELS: Record<Status, string> = {
  upcoming: "À venir",
  ongoing: "En cours",
  finished: "Terminé",
  scheduled: "À jouer",
  played: "Joué",
  pending: "En attente",
  accepted: "Acceptée",
  rejected: "Refusée",
};

const baseStyle: CSSProperties = {
  display: "inline-block",
  padding: "0.25rem 0.65rem",
  borderRadius: "999px",
  fontSize: "0.8rem",
  fontWeight: 600,
  lineHeight: 1.2,
};

function StatusBadge({ status }: StatusBadgeProps) {
  const statusStyle = statusStyles[status];

  return (
    <span
      style={{
        ...baseStyle,
        ...statusStyle,
      }}
    >
      {STATUS_LABELS[status]}
    </span>
  );
}

export default StatusBadge;
