import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

interface AuthUser {
  id: number;
  email: string;
  username: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

interface AuthProviderProps {
  children: ReactNode;
}

const STORAGE_KEY = "arena_auth";

const DEMO_USER: AuthUser = {
  id: 1,
  email: "demo@arena.fr",
  username: "Demo",
};

const DEMO_TOKEN = "mock-arena-token";

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);

  // isLoading évite d'envoyer temporairement l'utilisateur vers /login
  // pendant que la session sauvegardée est relue dans le localStorage.
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Au chargement de l'application, on récupère la session sauvegardée.
    // Cela permet de rester connecté après un F5 ou un rechargement de page.
    const storedAuth = localStorage.getItem(STORAGE_KEY);

    if (!storedAuth) {
      setIsLoading(false);
      return;
    }

    try {
      const auth = JSON.parse(storedAuth) as {
        user: AuthUser;
        token: string;
      };

      setUser(auth.user);
      setToken(auth.token);
    } catch {
      // Si les données du localStorage sont invalides, on les supprime
      // pour éviter de conserver une session impossible à restaurer.
      localStorage.removeItem(STORAGE_KEY);
    } finally {
      // La lecture de la session est terminée : les routes peuvent maintenant
      // décider normalement si l'utilisateur est connecté ou non.
      setIsLoading(false);
    }
  }, []);

  async function login(email: string, password: string): Promise<void> {
    // TODO: provisoire — la connexion est actuellement simulée.
    // Elle sera remplacée par un appel au backend lorsque l'authentification
    // réelle sera branchée sur l'endpoint /auth/login.
    if (email !== "demo@arena.fr" || password !== "arena123") {
      throw new Error("Identifiants invalides.");
    }

    const authData = {
      user: DEMO_USER,
      token: DEMO_TOKEN,
    };

    setUser(authData.user);
    setToken(authData.token);

    // On sauvegarde la session pour qu'un rafraîchissement de la page
    // ne déconnecte pas l'utilisateur.
    localStorage.setItem(STORAGE_KEY, JSON.stringify(authData));
  }

  function logout(): void {
    setUser(null);
    setToken(null);

    // La session est supprimée du localStorage pour que l'utilisateur
    // soit réellement déconnecté après un nouveau chargement de la page.
    localStorage.removeItem(STORAGE_KEY);
  }

  const value: AuthContextValue = {
    user,
    token,
    isAuthenticated: user !== null && token !== null,
    isLoading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error("useAuth doit être utilisé dans un AuthProvider.");
  }

  return context;
}