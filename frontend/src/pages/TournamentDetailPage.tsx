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