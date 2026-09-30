import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../hooks/useAuth";

// `identifier` et non `email` : le backend accepte indifféremment le nom
// d'utilisateur ou l'adresse e-mail dans le champ `username` du formulaire OAuth2.
interface LoginForm {
  identifier: string;
  password: string;
}

// Les noms d'utilisateur font au moins 3 caractères (UserCreate côté backend),
// et une adresse e-mail en compte forcément davantage.
const MIN_IDENTIFIER_LENGTH = 3;

function getLoginErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    // Le backend répond volontairement le même 401 pour un compte inconnu et
    // un mauvais mot de passe : le message ne doit pas trahir lequel des deux.
    if (error.status === 401) {
      return "Identifiant ou mot de passe incorrect.";
    }
    return error.message;
  }

  return "Une erreur est survenue lors de la connexion.";
}

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState<LoginForm>({
    identifier: "",
    password: "",
  });

  const [errors, setErrors] = useState<Partial<LoginForm>>({});
  const [submitError, setSubmitError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (field: keyof LoginForm, value: string) => {
    setForm((previous) => ({
      ...previous,
      [field]: value,
    }));

    setErrors((previous) => ({
      ...previous,
      [field]: "",
    }));

    setSubmitError("");
  };

  const validate = (): boolean => {
    const newErrors: Partial<LoginForm> = {};

    const identifier = form.identifier.trim();

    if (!identifier) {
      newErrors.identifier = "Le nom d'utilisateur ou l'adresse e-mail est obligatoire.";
    } else if (identifier.length < MIN_IDENTIFIER_LENGTH) {
      newErrors.identifier = `L'identifiant doit contenir au moins ${MIN_IDENTIFIER_LENGTH} caractères.`;
    }

    if (!form.password.trim()) {
      newErrors.password = "Le mot de passe est obligatoire.";
    }

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setSubmitError("");

    if (!validate()) {
      return;
    }

    setLoading(true);

    try {
      await login(form.identifier.trim(), form.password);
      navigate("/tournaments");
    } catch (error: unknown) {
      setSubmitError(getLoginErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-card">
        <h1>Connexion</h1>

        <form onSubmit={handleSubmit} noValidate>
          <div className="form-field">
            <label htmlFor="identifier">Nom d'utilisateur ou e-mail</label>

            {/* type="text" et non "email" : le navigateur refuserait sinon un
                simple nom d'utilisateur. */}
            <input
              id="identifier"
              type="text"
              autoComplete="username"
              value={form.identifier}
              onChange={(event) =>
                handleChange("identifier", event.target.value)
              }
              disabled={loading}
              aria-invalid={Boolean(errors.identifier)}
              aria-describedby={
                errors.identifier ? "identifier-error" : undefined
              }
            />

            {errors.identifier && (
              <p id="identifier-error" className="field-error">
                {errors.identifier}
              </p>
            )}
          </div>

          <div className="form-field">
            <label htmlFor="password">Mot de passe</label>

            <input
              id="password"
              type="password"
              autoComplete="current-password"
              value={form.password}
              onChange={(event) =>
                handleChange("password", event.target.value)
              }
              disabled={loading}
              aria-invalid={Boolean(errors.password)}
              aria-describedby={
                errors.password ? "password-error" : undefined
              }
            />

            {errors.password && (
              <p id="password-error" className="field-error">
                {errors.password}
              </p>
            )}
          </div>

          {submitError && (
            <p className="form-error" role="alert">
              {submitError}
            </p>
          )}

          <button type="submit" disabled={loading}>
            {loading ? "Connexion..." : "Se connecter"}
          </button>
        </form>
      </section>
    </main>
  );
}