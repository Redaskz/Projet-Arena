import StatusBadge from "./StatusBadge";

type RegistrationStatus = "pending" | "accepted" | "rejected";

interface RegistrationItem {
  id: number;
  teamName: string;
  status: RegistrationStatus;
}

interface RegistrationListProps {
  registrations: RegistrationItem[];
}

function RegistrationList({ registrations }: RegistrationListProps) {
  if (registrations.length === 0) {
    return <p>Aucune équipe inscrite pour le moment.</p>;
  }

  return (
    <section>
      <h2>Équipes inscrites</h2>

      <ul>
        {registrations.map((registration) => (
          <li key={registration.id}>
            <span>{registration.teamName}</span>
            <StatusBadge status={registration.status} />
          </li>
        ))}
      </ul>
    </section>
  );
}

export default RegistrationList;