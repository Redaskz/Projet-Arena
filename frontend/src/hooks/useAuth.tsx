import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useNavigate } from "react-router-dom";
import { getMe, login as loginRequest } from "../api/auth";
import { TOKEN_STORAGE_KEY, setUnauthorizedHandler } from "../api/client";
import type { User } from "../types";
import useLocalStorage from "./useLocalStorage";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (identifier: string, password: string) => Promise<void>;
  logout: () => void;
}

interface AuthProviderProps {
  children: ReactNode;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: AuthProviderProps) {
  const navigate = useNavigate();

  // Seul le jeton est persisté, sous la clé que relit api/client.ts. L'utilisateur
  // n'est pas stocké : il est redemandé à GET /auth/me, qui fait foi (un compte
  // a pu être modifié ou supprimé depuis la dernière visite).
  const [token, setToken] = useLocalStorage<string | null>(TOKEN_STORAGE_KEY, null);
  const [user, setUser] = useState<User | null>(null);

  // isLoading évite d'envoyer l'utilisateur vers /login pendant que la session
  // sauvegardée est vérifiée auprès du backend : sans lui, un F5 sur une route
  // protégée éjecterait l'utilisateur avant la réponse de /auth/me.
  // Sans jeton stocké, il n'y a rien à vérifier : on démarre directement à false.
  const [isLoading, setIsLoading] = useState<boolean>(token !== null);

  useEffect(() => {
    // Restauration uniquement : un jeton présent mais pas encore d'utilisateur.
    // Après une connexion, les deux sont posés ensemble et on ne refait rien.
    if (token === null || user !== null) {
      return;
    }

    // Garde contre une réponse arrivée après démontage (double appel du
    // StrictMode en développement, ou déconnexion pendant la requête).
    let cancelled = false;

    getMe(token)
      .then((currentUser) => {
        if (!cancelled) {
          setUser(currentUser);
        }
      })
      .catch(() => {
        // Jeton expiré, compte supprimé ou API injoignable : la session ne
        // peut pas être restaurée, on la vide plutôt que de garder un jeton mort.
        if (!cancelled) {
          setToken(null);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [token, user, setToken]);

  useEffect(() => {
    // Appelé par le client HTTP quand une requête authentifiée reçoit un 401 :
    // le jeton n'est plus accepté, on vide la session et on renvoie vers la
    // page de connexion.
    setUnauthorizedHandler(() => {
      setToken(null);
      setUser(null);
      navigate("/login", { replace: true });
    });

    return () => {
      setUnauthorizedHandler(null);
    };
  }, [navigate, setToken]);

  async function login(identifier: string, password: string): Promise<void> {
    const accessToken = await loginRequest(identifier, password);
    const currentUser = await getMe(accessToken);

    // Le jeton n'est enregistré qu'une fois l'utilisateur obtenu : si /auth/me
    // échoue, aucune demi-session ne reste stockée.
    setToken(accessToken);
    setUser(currentUser);
  }

  function logout(): void {
    // useLocalStorage réécrit la clé à null : le client HTTP cesse aussitôt
    // d'envoyer le jeton, et un F5 ne restaure plus rien.
    setToken(null);
    setUser(null);
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
