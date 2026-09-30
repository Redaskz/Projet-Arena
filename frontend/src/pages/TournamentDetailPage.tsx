import { useState } from "react";
import { useParams } from "react-router-dom";

import CommentForm from "../components/CommentForm";
import CommentList from "../components/CommentList";
import ErrorMessage from "../components/ErrorMessage";
import Loader from "../components/Loader";
import RegistrationList from "../components/RegistrationList";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../hooks/useAuth";
import useDocumentTitle from "../hooks/useDocumentTitle";
import { useFetch } from "../hooks/useFetch";
import { USE_MOCKS, getMockTournaments, mockFetchState } from "../mocks";
import type { RegistrationStatus, Tournament } from "../types";

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

function findMockTournament(id: number): Tournament | null {
  return getMockTournaments().find((tournament) => tournament.id === id) ?? null;
}

function TournamentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();

  useDocumentTitle("Arena - Tournoi");

  const fetched = useFetch<Tournament>(`/tournaments/${id ?? ""}`);
  const mockTournament = findMockTournament(Number(id));
  const { data: tournament, loading, error } = USE_MOCKS
    ? {
        ...mockFetchState(mockTournament),
        error: mockTournament ? null : "Tournoi introuvable.",
      }
    : fetched;

  // Inscriptions et commentaires n'ont pas encore de route côté backend :
  // ces listes restent locales en attendant, quel que soit USE_MOCKS.
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

  async function handleCommentSubmit(content: string) {
    const newComment: CommentItem = {
      id: Date.now(),
      authorName: user?.username ?? "Anonyme",
      content,
      createdAt: new Date().toLocaleDateString("fr-FR"),
    };

    setComments((previousComments) => [
      ...previousComments,
      newComment,
    ]);
  }

  if (!id) {
    return (
      <ErrorMessage message="Identifiant du tournoi manquant." />
    );
  }

  if (loading) {
    return <Loader />;
  }

  // Le 404 du backend (« Tournoi introuvable ») arrive ici via useFetch.
  if (error || !tournament) {
    return <ErrorMessage message={error ?? "Aucune donnée reçue."} />;
  }

  return (
    <main>
      <header>
        <h1>{tournament.name}</h1>
        <StatusBadge status={tournament.status} />
      </header>

      <p>
        Début :{" "}
        {new Date(tournament.start_date).toLocaleDateString("fr-FR")}
        {" · "}
        {tournament.max_teams} équipes maximum
      </p>

      <RegistrationList registrations={registrations} />

      <section>
        <CommentForm onSubmit={handleCommentSubmit} />
        <CommentList comments={comments} />
      </section>
    </main>
  );
}

export default TournamentDetailPage;
