import { ApiError } from './client';

/**
 * Extract a readable, user-facing message from an API error or any thrown value.
 * Handles Django Ninja / backend shapes: detail (string or validation array), message.
 */
export function getApiErrorMessage(err: unknown, fallback: string): string {
  if (!(err instanceof ApiError)) {
    return fallback;
  }
  const data = err.data as Record<string, unknown> | null | undefined;
  if (!data || typeof data !== 'object') {
    return fallback;
  }
  const detail = data.detail;
  if (typeof detail === 'string' && detail.trim().length > 0) {
    return detail.trim();
  }
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => (item && typeof item === 'object' && 'msg' in item ? String((item as { msg?: unknown }).msg) : null))
      .filter(Boolean) as string[];
    if (messages.length > 0) {
      return messages.join('. ');
    }
  }
  if (typeof data.message === 'string' && data.message.trim().length > 0) {
    return data.message.trim();
  }
  return fallback;
}
