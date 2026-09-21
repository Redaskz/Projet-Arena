import { useState } from 'react';
import type { FormEvent } from 'react';
import { ApiError } from '../api/client';
import type { Game } from '../types';
import { createTeam } from '../api/teams';
import ErrorMessage from './ErrorMessage';
import FormField from './FormField';

interface TeamCreateFormProps {
  games: Game[];
  // Appelé après une création réussie : la page recharge alors sa liste.
  onCreated: () => void;
}

// Tous les champs sont des chaînes, même game_id : un input ou un select
// renvoie toujours du texte. La conversion en nombre se fait à l'envoi.
interface TeamForm {
  name: string;
  tag: string;
  game_id: string;
}

// Au plus un message d'erreur par champ du formulaire.
type TeamFormErrors = Partial<Record<keyof TeamForm, string>>;

const EMPTY_FORM: TeamForm = { name: '', tag: '', game_id: '' };

// Fonction pure, en dehors du composant : elle ne dépend que du formulaire,
// donc facile à lire, à tester et à modifier (ex. changer les bornes du tag).
function validateTeamForm(form: TeamForm): TeamFormErrors {
  const errors: TeamFormErrors = {};

  // trim() : un nom composé uniquement d'espaces compte comme vide.
  if (form.name.trim() === '') {
    errors.name = "Le nom de l'équipe est obligatoire.";
  }

  const tagLength = form.tag.trim().length;
  if (tagLength < 3 || tagLength > 5) {
    errors.tag = 'Le tag doit contenir entre 3 et 5 caractères.';
  }

  if (form.game_id === '') {
    errors.game_id = 'Choisissez un jeu.';
  }

  return errors;
}

function TeamCreateForm({ games, onCreated }: TeamCreateFormProps) {
  const [form, setForm] = useState<TeamForm>(EMPTY_FORM);
  const [errors, setErrors] = useState<TeamFormErrors>({});
  const [submitting, setSubmitting] = useState<boolean>(false);
  // Erreur qui ne concerne aucun champ précis (serveur injoignable, 500...).
  const [submitError, setSubmitError] = useState<string | null>(null);

  // keyof TeamForm : TypeScript refuse un nom de champ qui n'existe pas.
  function updateField(field: keyof TeamForm, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
    // On efface l'erreur du champ dès que l'utilisateur le corrige.
    setErrors((current) => ({ ...current, [field]: undefined }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    // Empêche le rechargement de la page, comportement par défaut d'un <form>.
    event.preventDefault();
    setSubmitError(null);

    // Validation côté client AVANT l'envoi : aucune requête si le formulaire
    // est invalide. Le serveur revalide de toute façon (le client est contournable).
    const validationErrors = validateTeamForm(form);
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    setSubmitting(true);
    try {
      await createTeam({
        name: form.name.trim(),
        tag: form.tag.trim(),
        game_id: Number(form.game_id),
      });
      setForm(EMPTY_FORM);
      onCreated();
    } catch (requestError: unknown) {
      if (requestError instanceof ApiError && requestError.status === 409) {
        // 409 Conflict = nom déjà pris. On range le message de l'API dans les
        // erreurs du champ "name" : il s'affiche donc sous ce champ précis.
        setErrors({ name: requestError.message });
      } else if (requestError instanceof Error) {
        setSubmitError(requestError.message);
      } else {
        setSubmitError("Impossible de créer l'équipe.");
      }
    } finally {
      // finally : le bouton se réactive dans tous les cas, succès comme échec.
      setSubmitting(false);
    }
  }

  return (
    // noValidate : on coupe les bulles de validation du navigateur pour
    // afficher nos propres messages, sous chaque champ.
    <form onSubmit={handleSubmit} noValidate>
      <h2>Créer une équipe</h2>

      <FormField id="team-name" label="Nom de l'équipe" error={errors.name}>
        <input
          id="team-name"
          type="text"
          value={form.name}
          onChange={(event) => updateField('name', event.target.value)}
          aria-invalid={errors.name !== undefined}
          aria-describedby="team-name-error"
        />
      </FormField>

      <FormField id="team-tag" label="Tag (3 à 5 caractères)" error={errors.tag}>
        <input
          id="team-tag"
          type="text"
          value={form.tag}
          onChange={(event) => updateField('tag', event.target.value)}
          aria-invalid={errors.tag !== undefined}
          aria-describedby="team-tag-error"
        />
      </FormField>

      <FormField id="team-game" label="Jeu" error={errors.game_id}>
        <select
          id="team-game"
          value={form.game_id}
          onChange={(event) => updateField('game_id', event.target.value)}
          aria-invalid={errors.game_id !== undefined}
          aria-describedby="team-game-error"
        >
          <option value="">-- Choisir un jeu --</option>
          {games.map((game) => (
            <option key={game.id} value={String(game.id)}>
              {game.name}
            </option>
          ))}
        </select>
      </FormField>

      {submitError && <ErrorMessage message={submitError} />}

      {/* Désactivé pendant l'envoi : empêche un double clic de créer deux fois l'équipe. */}
      <button type="submit" className="form-submit" disabled={submitting}>
        {submitting ? 'Création...' : "Créer l'équipe"}
      </button>
    </form>
  );
}

export default TeamCreateForm;
