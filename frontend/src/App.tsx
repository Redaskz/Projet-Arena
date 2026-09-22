import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import TournamentsPage from "./pages/TournamentsPage";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/tournaments" element={<TournamentsPage />} />

          {/* Le détail contient lui aussi des données réservées aux utilisateurs
              connectés, donc il doit avoir la même protection que la liste. */}
          <Route
            path="/tournaments/:id"
            element={<TournamentsPage />}
          />
        </Route>

        <Route path="*" element={<Navigate to="/tournaments" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;