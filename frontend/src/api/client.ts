const API_URL = 'http://localhost:8000';

// Clé sous laquelle useAuth range le jeton, via useLocalStorage. Le client la
// relit à chaque requête : il n'existe qu'une seule copie du jeton, celle du
// localStorage, et une déconnexion est donc visible ici immédiatement.
export const TOKEN_STORAGE_KEY = 'arena.auth.token';

export class ApiError extends Error {
  status: number;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.name = 'ApiError';
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  // Corps JSON, le format de toutes les routes sauf la connexion.
  body?: unknown;
  // Corps formulaire : POST /auth/login attend un formulaire OAuth2, pas du JSON.
  form?: URLSearchParams;
  // Jeton fourni explicitement par l'appelant (connexion, restauration de
  // session). Dans ce cas c'est l'appelant qui gère un éventuel 401.
  token?: string;
}

// useLocalStorage stocke la valeur en JSON : le jeton est donc une chaîne
// entre guillemets. La garde de type écarte toute valeur inattendue.
function readStoredToken(): string | null {
  try {
    const stored = window.localStorage.getItem(TOKEN_STORAGE_KEY);
    if (stored === null) {
      return null;
    }
    const parsed: unknown = JSON.parse(stored);
    return typeof parsed === 'string' && parsed !== '' ? parsed : null;
  } catch {
    return null;
  }
}

// Le client ne connaît ni React ni le routeur : c'est useAuth qui lui confie
// quoi faire quand la session expire (vider l'état, rediriger vers /login).
let unauthorizedHandler: (() => void) | null = null;

export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler;
}

// FastAPI renvoie `detail` en texte pour une HTTPException, mais en tableau
// d'erreurs pour une validation refusée (422). On n'affiche que du texte.
function extractDetail(data: unknown): string | null {
  if (typeof data !== 'object' || data === null || !('detail' in data)) {
    return null;
  }

  const { detail } = data;

  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    return 'Les données envoyées sont invalides.';
  }

  return null;
}

async function send(url: string, options: RequestOptions): Promise<Response> {
  const headers = new Headers();

  if (options.body !== undefined) {
    headers.set('Content-Type', 'application/json');
  }

  const explicitToken = options.token;
  const token = explicitToken ?? readStoredToken();
  if (token !== null) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(`${API_URL}${url}`, {
      method: options.method ?? 'GET',
      headers,
      // Avec un URLSearchParams, fetch pose lui-même le Content-Type
      // application/x-www-form-urlencoded.
      body:
        options.form ??
        (options.body !== undefined ? JSON.stringify(options.body) : undefined),
    });
  } catch {
    // fetch ne rejette que si le serveur est injoignable (API arrêtée, CORS).
    // Statut 0 : aucune réponse HTTP n'a été reçue.
    throw new ApiError(0, "Le serveur est injoignable. Vérifiez que l'API est démarrée.");
  }

  if (!response.ok) {
    let detail = 'Une erreur est survenue.';

    try {
      detail = extractDetail(await response.json()) ?? detail;
    } catch {
      // Certaines réponses d'erreur peuvent ne pas contenir de JSON.
    }

    // Un 401 alors qu'on a envoyé le jeton stocké : il est expiré ou invalide.
    // Sans jeton, un 401 est une réponse normale (mauvais identifiants, action
    // réservée) que l'appelant affiche lui-même.
    if (response.status === 401 && explicitToken === undefined && token !== null) {
      unauthorizedHandler?.();
      detail = 'Votre session a expiré. Veuillez vous reconnecter.';
    }

    throw new ApiError(response.status, detail);
  }

  return response;
}

export async function request<T>(
  url: string,
  options: RequestOptions = {},
): Promise<T> {
  const response = await send(url, options);
  const data: T = await response.json();
  return data;
}

export function get<T>(url: string): Promise<T> {
  return request<T>(url);
}

export function post<T>(url: string, body: unknown): Promise<T> {
  return request<T>(url, {
    method: 'POST',
    body,
  });
}

export function patch<T>(url: string, body: unknown): Promise<T> {
  return request<T>(url, {
    method: 'PATCH',
    body,
  });
}

// Un DELETE répond 204, sans corps : il n'y a rien à lire, d'où Promise<void>.
export async function del(url: string): Promise<void> {
  await send(url, { method: 'DELETE' });
}
