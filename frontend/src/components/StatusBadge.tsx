import type { CSSProperties } from "react";

type Status =
  | "draft"
  | "open"
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
      {status}
    </span>
  );
}

export default StatusBadge;