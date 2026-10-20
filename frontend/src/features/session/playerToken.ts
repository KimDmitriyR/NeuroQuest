import { PLAYER_TOKEN_KEY } from "../../api/client";

// before child tokens existed a device remembered a bare player id; it can no
// longer authenticate anything, so it is cleaned up on startup
const LEGACY_PLAYER_ID_KEY = "neuroquest.player_id";

export function getPlayerToken(): string | null {
  return localStorage.getItem(PLAYER_TOKEN_KEY);
}

export function storePlayerToken(token: string): void {
  localStorage.setItem(PLAYER_TOKEN_KEY, token);
}

export function clearPlayerToken(): void {
  localStorage.removeItem(PLAYER_TOKEN_KEY);
}

/**
 * A parent sends the child a link like /?t=<token>: keep the token on this
 * device and scrub it from the address bar (and so from history/bookmarks).
 * Old-style /?child=<id> links no longer grant anything; just drop them.
 */
export function consumePlayerTokenFromUrl(): string | null {
  localStorage.removeItem(LEGACY_PLAYER_ID_KEY);

  const url = new URL(window.location.href);
  const token = url.searchParams.get("t");
  const hadLegacy = url.searchParams.has("child");
  if (token === null && !hadLegacy) return null;

  url.searchParams.delete("t");
  url.searchParams.delete("child");
  window.history.replaceState({}, "", url.toString());

  if (!token) return null;
  storePlayerToken(token);
  return token;
}
