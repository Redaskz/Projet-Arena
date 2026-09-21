import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import GamesPage from './pages/GamesPage';
import LoginPage from './pages/LoginPage';
import MatchesPage from './pages/MatchesPage';
import TeamsPage from './pages/TeamsPage';
import TournamentDetailPage from './pages/TournamentDetailPage';
import TournamentsPage from './pages/TournamentsPage';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/tournaments" element={<TournamentsPage />} />
          </Route>

          <Route
            path="/tournaments/:id"
            element={<TournamentDetailPage />}
          />
          <Route path="/games" element={<GamesPage />} />
          <Route path="/teams" element={<TeamsPage />} />
          <Route path="/matches" element={<MatchesPage />} />

          <Route path="*" element={<Navigate to="/tournaments" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
