import { loadCredentials, makeBasicAuthHeader } from '../lib/basicAuth';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, data: unknown) {
    super(`API Error ${status}`);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  withAuth = true,
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (withAuth) {
    const creds = loadCredentials();
    if (creds) {
      headers['Authorization'] = makeBasicAuthHeader(creds.email, creds.password);
    }
  }

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    let data: unknown;
    try {
      data = await res.json();
    } catch {
      data = { detail: res.statusText };
    }
    throw new ApiError(res.status, data);
  }

  if (res.status === 204) return undefined as T;

  return res.json() as Promise<T>;
}

async function requestFormData<T>(
  path: string,
  formData: FormData,
  withAuth = true,
): Promise<T> {
  const headers: Record<string, string> = {};
  if (withAuth) {
    const creds = loadCredentials();
    if (creds) {
      headers['Authorization'] = makeBasicAuthHeader(creds.email, creds.password);
    }
  }
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    body: formData,
    headers,
  });
  if (!res.ok) {
    let data: unknown;
    try {
      data = await res.json();
    } catch {
      data = { detail: res.statusText };
    }
    throw new ApiError(res.status, data);
  }
  return res.json() as Promise<T>;
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown, withAuth = true) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }, withAuth),
  postFormData: <T>(path: string, formData: FormData) =>
    requestFormData<T>(path, formData),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
};
