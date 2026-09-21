import type { ReactNode } from 'react';
import './Card.css';

// Carte générique partagée par tout le groupe (jeux, équipes, tournois...).
// Elle ne connaît aucune donnée métier : chaque page lui passe du texte déjà
// mis en forme. C'est ce qui la rend réutilisable sans modification.
interface CardProps {
  title: string;
  subtitle?: string;
  imageUrl?: string;
  // ReactNode plutôt que string : on peut passer un simple texte ("FPS")
  // ou un composant complet (ex. <StatusBadge />) sans changer Card.
  badge?: ReactNode;
  children?: ReactNode;
}

function Card({ title, subtitle, imageUrl, badge, children }: CardProps) {
  return (
    <article className="card">
      {imageUrl && (
        // alt="" : l'image est décorative, le titre juste en dessous porte
        // déjà l'information. Un lecteur d'écran ne le lira pas deux fois.
        <img className="card__image" src={imageUrl} alt="" loading="lazy" />
      )}

      <div className="card__body">
        <div className="card__header">
          <h3 className="card__title">{title}</h3>
          {badge && <span className="card__badge">{badge}</span>}
        </div>

        {subtitle && <p className="card__subtitle">{subtitle}</p>}

        {children}
      </div>
    </article>
  );
}

export default Card;
