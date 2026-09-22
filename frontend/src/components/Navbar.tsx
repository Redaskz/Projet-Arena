import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

// Pas d'interface NavbarProps : notre convention (une interface XProps par
// composant) ne vaut que si le composant reçoit des props. Une interface vide
// n'apporte aucun typage et ESLint la rejette.
function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    // La session est supprimée par logout ; la redirection permet
    // ensuite de ramener immédiatement l'utilisateur vers la connexion.
    logout();
    navigate("/login");
  };

  return (
    <nav>
      {isAuthenticated ? (
        <>
          <NavLink to="/tournaments">Tournois</NavLink>
          <NavLink to="/games">Jeux</NavLink>
          <NavLink to="/teams">Équipes</NavLink>
          <NavLink to="/matches">Matchs</NavLink>

          {/* Préfixe "Connecté :" : sans lui, "Demo" se lisait comme un lien de
              plus dans le menu. La classe le met en retrait (voir index.css). */}
          <span className="navbar__user">Connecté : {user?.username}</span>

          <button type="button" onClick={handleLogout}>
            Déconnexion
          </button>
        </>
      ) : (
        <NavLink to="/login">Connexion</NavLink>
      )}
    </nav>
  );
}

export default Navbar;