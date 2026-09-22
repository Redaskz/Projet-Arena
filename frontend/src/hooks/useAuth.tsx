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

  // isLoading empêche ProtectedRoute de considérer l'utilisateur comme
  // déconnecté pendant que la session sauvegardée est relue.
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // La session est conservée dans localStorage afin qu'un F5 ne
    // déconnecte pas l'utilisateur alors que sa session existe toujours.
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
      // Une donnée invalide ne doit pas bloquer toute l'application :
      // on repart donc d'une session vide.
      localStorage.removeItem(STORAGE_KEY);
    } finally {
      setIsLoading(false);
    }
  }, []);

  async function login(email: string, password: string): Promise<void> {
    // TODO: provisoire — la connexion utilise actuellement des identifiants
    // simulés en attendant le branchement définitif sur l'API backend.
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
    // conserve la connexion de l'utilisateur.
    localStorage.setItem(STORAGE_KEY, JSON.stringify(authData));
  }

  function logout(): void {
    setUser(null);
    setToken(null);

    // Supprimer la session évite qu'un autre utilisateur récupère
    // accidentellement la session précédente sur le même navigateur.
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