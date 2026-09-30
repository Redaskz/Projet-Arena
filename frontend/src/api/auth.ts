import { request } from './client';
import type { Token, User } from '../types';
import { USE_MOCKS, getMeMock, loginMock } from '../mocks';

// POST /auth/login attend un formulaire OAuth2 (username + password) et non du
// JSON : c'est le format imposé par OAuth2PasswordRequestForm côté FastAPI.
// Le champ s'appelle `username` mais le backend y accepte aussi un e-mail.
export async function login(identifier: string, password: string): Promise<string> {
  if (USE_MOCKS) {
    return loginMock(identifier, password);
  }

  const form = new URLSearchParams();
  form.set('username', identifier);
  form.set('password', password);

  const token = await request<Token>('/auth/login', { method: 'POST', form });
  return token.access_token;
}

// Le jeton est passé explicitement : juste après la connexion, il n'est pas
// encore écrit dans le localStorage, et lors d'une restauration c'est useAuth
// qui décide quoi faire d'un refus.
export function getMe(token: string): Promise<User> {
  if (USE_MOCKS) {
    return getMeMock(token);
  }

  return request<User>('/auth/me', { token });
}
