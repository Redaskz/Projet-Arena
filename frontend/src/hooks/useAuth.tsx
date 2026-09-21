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

  // Au chargement de l'application, on récupère la session sauvegardée.
// Cela permet de rester connecté après un F5.
  useEffect(() => {
    const storedAuth = localStorage.getItem(STORAGE_KEY);

    if (!storedAuth) {
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
      // Si les données du localStorage sont invalides,
      // on les supprime pour repartir sur une session propre.
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  async function login(email: string, password: string): Promise<void> {
    // TODO: provisoire — remplacé par l'appel au backend lorsque
    // l'endpoint /auth/login sera utilisé par le frontend.
    if (email !== "demo@arena.fr" || password !== "arena123") {
      throw new Error("Identifiants invalides.");
    }

    const authData = {
      user: DEMO_USER,
      token: DEMO_TOKEN,
    };

    setUser(authData.user);
    setToken(authData.token);

    // On sauvegarde la session pour qu'un rafraîchissement
    // de la page ne déconnecte pas l'utilisateur.
    localStorage.setItem(STORAGE_KEY, JSON.stringify(authData));
  }

  function logout(): void {
    setUser(null);
    setToken(null);
    localStorage.removeItem(STORAGE_KEY);
  }

  const value: AuthContextValue = {
    user,
    token,
    isAuthenticated: user !== null && token !== null,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error("useAuth doit être utilisé dans un AuthProvider.");
  }

  return context;
}