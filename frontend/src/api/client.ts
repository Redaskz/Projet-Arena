const API_URL = 'http://localhost:8000';

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
  body?: unknown;
}

async function requestNetwork<T>(
  url: string,
  options: RequestOptions = {},
): Promise<T> {
  const response = await fetch(`${API_URL}${url}`, {
    method: options.method ?? 'GET',
    headers:
      options.body !== undefined
        ? {
            'Content-Type': 'application/json',
          }
        : undefined,
    body:
      options.body !== undefined
        ? JSON.stringify(options.body)
        : undefined,
  });

  if (!response.ok) {
    let detail = 'Une erreur est survenue.';

    try {
      const errorData: { detail?: string } = await response.json();
      detail = errorData.detail ?? detail;
    } catch {
      // Certaines réponses d'erreur peuvent ne pas contenir de JSON.
    }

    throw new ApiError(response.status, detail);
  }

  // Une réponse DELETE peut être vide (HTTP 204).
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function request<T>(
  url: string,
  options: RequestOptions = {},
): Promise<T> {
  return requestNetwork<T>(url, options);
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

export function del<T>(url: string): Promise<T> {
  return request<T>(url, {
    method: 'DELETE',
  });
}