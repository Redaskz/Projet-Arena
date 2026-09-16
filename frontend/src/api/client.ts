const API_URL = 'http://localhost:8000';

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}
export async function request<T>(url: string): Promise<T> {
  const response = await fetch(`${API_URL}${url}`);

if (!response.ok) {
  const errorData: { detail?: string } = await response.json();

  throw new ApiError(
    response.status,
    errorData.detail ?? 'Une erreur est survenue.',
  );
}

  return response.json() as Promise<T>;
}