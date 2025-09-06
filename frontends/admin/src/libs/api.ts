export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/admin";

export async function fetchJson<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
      signal: controller.signal,
    });
    if (!res.ok) {
      throw new Error(res.statusText);
    }
    return res.json();
  } finally {
    clearTimeout(timeout);
  }
}
