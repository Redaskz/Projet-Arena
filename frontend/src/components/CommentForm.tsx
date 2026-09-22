import { useState } from "react";
import type { FormEvent } from "react";

interface CommentFormProps {
  onSubmit: (content: string) => Promise<void>;
}

function CommentForm({ onSubmit }: CommentFormProps) {
  const [content, setContent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isTooLong = content.length > 500;
  const isEmpty = content.trim().length === 0;
  const isDisabled = isEmpty || isTooLong || isSubmitting;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (isDisabled) {
      return;
    }

    try {
      setIsSubmitting(true);

      await onSubmit(content.trim());

      setContent("");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="comment-content">
        Ajouter un commentaire
      </label>

      <textarea
        id="comment-content"
        value={content}
        onChange={(event) => setContent(event.target.value)}
        minLength={1}
        maxLength={500}
        rows={4}
        placeholder="Écris ton commentaire..."
      />

      <p>
        {content.length} / 500 caractères
      </p>

      {isTooLong && (
        <p>
          Le commentaire ne peut pas dépasser 500 caractères.
        </p>
      )}

      <button type="submit" disabled={isDisabled}>
        {isSubmitting ? "Envoi..." : "Publier"}
      </button>
    </form>
  );
}

export default CommentForm;