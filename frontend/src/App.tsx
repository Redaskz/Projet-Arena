import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import GamesPage from './pages/GamesPage';
import LoginPage from './pages/LoginPage';
import TeamsPage from './pages/TeamsPage';
import TournamentDetailPage from './pages/TournamentDetailPage';
import TournamentsPage from './pages/TournamentsPage';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/tournaments" element={<TournamentsPage />} />
          <Route
            path="/tournaments/:id"
            element={<TournamentDetailPage />}
          />
          <Route path="/games" element={<GamesPage />} />
          <Route path="/teams" element={<TeamsPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;