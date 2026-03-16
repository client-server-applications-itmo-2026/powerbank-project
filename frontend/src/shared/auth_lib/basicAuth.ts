interface Credentials {
  email: string;
  password: string;
}

const CREDENTIALS_KEY = 'auth_credentials';

export function saveCredentials(credentials: Credentials): void {
  localStorage.setItem(CREDENTIALS_KEY, JSON.stringify(credentials));
}

export function loadCredentials(): Credentials | null {
  const stored = localStorage.getItem(CREDENTIALS_KEY);
  if (!stored) return null;
  try {
    return JSON.parse(stored);
  } catch {
    return null;
  }
}

export function clearCredentials(): void {
  localStorage.removeItem(CREDENTIALS_KEY);
}

export function makeBasicAuthHeader(credentials: Credentials): string {
  const { email, password } = credentials;
  const encoded = btoa(`${email}:${password}`);
  return `Basic ${encoded}`;
}