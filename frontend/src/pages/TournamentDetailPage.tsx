import { useState } from "react";
import { useParams } from "react-router-dom";

import CommentForm from "../components/CommentForm";
import CommentList from "../components/CommentList";
import ErrorMessage from "../components/ErrorMessage";
import Loader from "../components/Loader";
import RegistrationList from "../components/RegistrationList";
import StatusBadge from "../components/StatusBadge";
import useDocumentTitle from "../hooks/useDocumentTitle";

type TournamentStatus = "draft" | "open" | "ongoing" | "finished";

type RegistrationStatus =
  | "pending"
  | "accepted"
  | "rejected";

interface TournamentDetail {
  id: number;
  name: string;
  description: string;
  status: TournamentStatus;
}

interface RegistrationItem {
  id: number;
  teamName: string;
  status: RegistrationStatus;
}

interface CommentItem {
  id: number;
  authorName: string;
  content: string;
  createdAt: string;
}

function TournamentDetailPage() {
  const { id } = useParams<{ id: string }>();

  useDocumentTitle("Arena - Tournoi");

  // TODO: provisoire — remplacer les données locales par api/client.ts de Yanis.
  const [tournament] = useState<TournamentDetail>({
    id: Number(id) || 1,
    name: "Arena Cup",
    description: "Tournoi amical entre équipes étudiantes.",
    status: "open",
  });

  const [registrations] = useState<RegistrationItem[]>([
    {
      id: 1,
      teamName: "ESTIA Dragons",
      status: "accepted",
    },
    {
      id: 2,
      teamName: "Pixel Warriors",
      status: "pending",
    },
    {
      id: 3,
      teamName: "404 Team",
      status: "rejected",
    },
  ]);

  const [comments, setComments] = useState<CommentItem[]>([
    {
      id: 1,
      authorName: "Othmane",
      content: "Bonne chance à toutes les équipes !",
      createdAt: "21/09/2026",
    },
  ]);

  const [isLoading] = useState(false);
  const [error] = useState<string | null>(null);

  async function handleCommentSubmit(content: string) {
    // TODO: provisoire — remplacer par POST via api/client.ts,
    // puis recharger les commentaires depuis le backend.

    const newComment: CommentItem = {
      id: Date.now(),
      authorName: "Othmane",
      content,
      createdAt: new Date().toLocaleDateString("fr-FR"),
    };

    setComments((previousComments) => [
      ...previousComments,
      newComment,
    ]);
  }

  if (isLoading) {
    return <Loader />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (!id) {
    return (
      <ErrorMessage message="Identifiant du tournoi manquant." />
    );
  }

  return (
    <main>
      <header>
        <h1>{tournament.name}</h1>
        <StatusBadge status={tournament.status} />
      </header>

      <p>{tournament.description}</p>

      <RegistrationList registrations={registrations} />

      <section>
        <CommentForm onSubmit={handleCommentSubmit} />
        <CommentList comments={comments} />
      </section>
    </main>
  );
}

export default TournamentDetailPage;