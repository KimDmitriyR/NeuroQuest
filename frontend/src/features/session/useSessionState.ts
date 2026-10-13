import { useCallback, useEffect, useState } from "react";
import { authApi } from "../../api/auth";
import { PARENT_TOKEN_KEY } from "../../api/client";
import { playersApi } from "../../api/players";
import type { ParentRead, Player } from "../../types/api";
import type { SessionValue } from "./session-context";

export const PLAYER_STORAGE_KEY = "neuroquest.player_id";

// a parent can send a child a link like /?child=<id>: remember that profile
// on this device and strip the parameter from the address bar
function consumeChildParamFromUrl(): string | null {
  const url = new URL(window.location.href);
  const childId = url.searchParams.get("child");
  if (!childId) return null;

  localStorage.setItem(PLAYER_STORAGE_KEY, childId);
  url.searchParams.delete("child");
  window.history.replaceState({}, "", url.toString());
  return childId;
}

function readInitialPlayerId(): string | null {
  return consumeChildParamFromUrl() ?? localStorage.getItem(PLAYER_STORAGE_KEY);
}

/** The single source of truth for "who is using the app right now". */
export function useSessionState(): SessionValue {
  // --- active child profile ---
  const [playerId, setPlayerId] = useState(readInitialPlayerId);
  const [player, setPlayer] = useState<Player | null>(null);
  const [playerLoading, setPlayerLoading] = useState(() => !!playerId);

  useEffect(() => {
    if (!playerId) return;
    let cancelled = false;
    playersApi
      .get(playerId)
      .then((p) => !cancelled && setPlayer(p))
      .catch(() => {
        localStorage.removeItem(PLAYER_STORAGE_KEY);
        if (!cancelled) setPlayerId(null);
      })
      .finally(() => !cancelled && setPlayerLoading(false));
    return () => {
      cancelled = true;
    };
  }, [playerId]);

  const clearPlayer = useCallback(() => {
    localStorage.removeItem(PLAYER_STORAGE_KEY);
    setPlayerId(null);
    setPlayer(null);
  }, []);

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
    parent,
    parentLoading,
    login,
    register,
    logoutParent,
    signOutAll,
  };
}
