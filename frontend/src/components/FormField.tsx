import type { ReactNode } from 'react';
import './FormField.css';

interface FormFieldProps {
  // id du champ (input ou select) passé en children.
  id: string;
  label: string;
  error?: string;
  children: ReactNode;
}

// Label + champ + message d'erreur, répété pour chaque champ du formulaire.
// L'erreur s'affiche directement SOUS le champ concerné, pas dans une alerte.
function FormField({ id, label, error, children }: FormFieldProps) {
  return (
    <div className="form-field">
      <label htmlFor={id}>{label}</label>
      {children}
      {error && (
        // id `${id}-error` : le champ le référence avec aria-describedby,
        // donc un lecteur d'écran lit l'erreur en même temps que le champ.
        <p id={`${id}-error`} className="form-field__error">
          {error}
        </p>
      )}
    </div>
  );
}

export default FormField;
