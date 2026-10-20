import { useCallback, useEffect, useState } from "react";
import { authApi } from "../../api/auth";
import {
  ApiError,
  PARENT_TOKEN_KEY,
  PLAYER_TOKEN_REJECTED_EVENT,
} from "../../api/client";
import { playersApi } from "../../api/players";
import type { ParentRead, Player } from "../../types/api";
import {
  clearPlayerToken,
  consumePlayerTokenFromUrl,
  getPlayerToken,
  storePlayerToken,
} from "./playerToken";
import type { SessionValue } from "./session-context";

function readInitialPlayerToken(): string | null {
  return consumePlayerTokenFromUrl() ?? getPlayerToken();
}

/** The single source of truth for "who is using the app right now". */
export function useSessionState(): SessionValue {
  // --- active child profile (identified by the token this device holds) ---
  const [playerToken, setPlayerToken] = useState(readInitialPlayerToken);
  const [player, setPlayer] = useState<Player | null>(null);
  const [playerLoading, setPlayerLoading] = useState(() => !!playerToken);

  useEffect(() => {
    if (!playerToken) return;
    let cancelled = false;
    playersApi
      .me()
      .then((p) => !cancelled && setPlayer(p))
      .catch((error) => {
        // only a rejected token means "not signed in"; a network hiccup must
        // not throw the child out of their profile
        if (error instanceof ApiError && error.status === 401) {
          clearPlayerToken();
          if (!cancelled) setPlayerToken(null);
        }
      })
      .finally(() => !cancelled && setPlayerLoading(false));
    return () => {
      cancelled = true;
    };
  }, [playerToken]);

  const clearPlayer = useCallback(() => {
    clearPlayerToken();
    setPlayerToken(null);
    setPlayer(null);
  }, []);

  const activatePlayerToken = useCallback((token: string) => {
    storePlayerToken(token);
    setPlayerLoading(true);
    setPlayerToken(token);
  }, []);

  // the server told us this device's link was reset by the parent
  useEffect(() => {
    window.addEventListener(PLAYER_TOKEN_REJECTED_EVENT, clearPlayer);
    return () => window.removeEventListener(PLAYER_TOKEN_REJECTED_EVENT, clearPlayer);
  }, [clearPlayer]);

  // --- logged-in parent ---
  const [parent, setParent] = useState<ParentRead | null>(null);
  const [parentLoading, setParentLoading] = useState(
    () => !!localStorage.getItem(PARENT_TOKEN_KEY),
  );

  useEffect(() => {
    if (!localStorage.getItem(PARENT_TOKEN_KEY)) return;
    authApi
      .me()
      .then(setParent)
      .catch(() => localStorage.removeItem(PARENT_TOKEN_KEY))
      .finally(() => setParentLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const result = await authApi.login(email, password);
    localStorage.setItem(PARENT_TOKEN_KEY, result.access_token);
    setParent(result.parent);
    return result.parent;
  }, []);

  const register = useCallback(
    async (email: string, password: string, acceptTerms: boolean) => {
      const result = await authApi.register(email, password, acceptTerms);
      localStorage.setItem(PARENT_TOKEN_KEY, result.access_token);
      setParent(result.parent);
      return result.parent;
    },
    [],
  );

  const logoutParent = useCallback(() => {
    localStorage.removeItem(PARENT_TOKEN_KEY);
    setParent(null);
  }, []);

  const signOutAll = useCallback(() => {
    logoutParent();
    clearPlayer();
  }, [logoutParent, clearPlayer]);

  return {
    player,
    playerLoading,
    clearPlayer,
    activatePlayerToken,
    parent,
    parentLoading,
    login,
    register,
    logoutParent,
    signOutAll,
  };
}
