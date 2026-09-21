import { NavLink } from 'react-router-dom';

function Navbar() {
  return (
    <nav>
      <NavLink to="/tournaments">Tournois</NavLink>
      <NavLink to="/games">Jeux</NavLink>
      <NavLink to="/teams">Équipes</NavLink>
      <NavLink to="/matches">Matchs</NavLink>
      <NavLink to="/login">Connexion</NavLink>
    </nav>
  );
}

export default Navbar;