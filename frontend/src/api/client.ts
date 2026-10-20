const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export const PARENT_TOKEN_KEY = "neuroquest.parent_token";
/** the child's own credential on this device (issued by the parent) */
export const PLAYER_TOKEN_KEY = "neuroquest.player_token";
/** fired when the server says this device's child link was reset */
export const PLAYER_TOKEN_REJECTED_EVENT = "neuroquest:player-token-rejected";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = localStorage.getItem(PARENT_TOKEN_KEY);
  const playerToken = localStorage.getItem(PLAYER_TOKEN_KEY);
  const response = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(playerToken ? { "X-Player-Token": playerToken } : {}),
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    if (
      response.status === 401 &&
      playerToken &&
      body.detail === "Access link was reset"
    ) {
      // the parent reset this child's link: this device is no longer signed in
      localStorage.removeItem(PLAYER_TOKEN_KEY);
      window.dispatchEvent(new Event(PLAYER_TOKEN_REJECTED_EVENT));
    }
    throw new ApiError(response.status, body.detail ?? response.statusText);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
};
