const API_URL = 'http://localhost:8000';

export async function request<T>(url: string): Promise<T> {
  const response = await fetch(`${API_URL}${url}`);

  if (!response.ok) {
    throw new Error(`Erreur HTTP : ${response.status}`);
  }

  return response.json() as Promise<T>;
}