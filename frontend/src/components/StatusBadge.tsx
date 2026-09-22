import type { CSSProperties } from "react";

type Status =
  | "draft"
  | "open"
  | "upcoming"
  | "ongoing"
  | "finished"
  | "pending"
  | "accepted"
  | "rejected"
  | "scheduled"
  | "played";

interface StatusBadgeProps {
  status: Status;
}

interface BadgeStyle {
  backgroundColor: string;
  color: string;
}

const statusStyles: Record<Status, BadgeStyle> = {
  draft: {
    backgroundColor: "#e5e7eb",
    color: "#374151",
  },
  open: {
    backgroundColor: "#dcfce7",
    color: "#166534",
  },
  ongoing: {
    backgroundColor: "#dbeafe",
    color: "#1d4ed8",
  },
  finished: {
    backgroundColor: "#ede9fe",
    color: "#6d28d9",
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
  scheduled: {
    backgroundColor: "#dbeafe",
    color: "#1d4ed8",
  },
  played: {
    backgroundColor: "#e5e7eb",
    color: "#374151",
  },

  upcoming: {
  backgroundColor: "#fef3c7",
  color: "#92400e",
},
};

// Libellés français affichés dans le badge : le backend envoie les statuts en
// anglais ("open", "ongoing"...), alors que toute l'interface est en français.
// Même principe que GENRE_LABELS dans api/games.ts : avec Record<Status, string>,
// TypeScript refuse de compiler si un statut du type Status n'a pas de libellé.
const STATUS_LABELS: Record<Status, string> = {
  draft: "Brouillon",
  open: "Ouvert",
  upcoming: "À venir",
  ongoing: "En cours",
  finished: "Terminé",
  pending: "En attente",
  accepted: "Acceptée",
  rejected: "Refusée",
  scheduled: "À jouer",
  played: "Joué",
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