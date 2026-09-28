import { useEffect, useState } from "react";
import { playersApi } from "../../api/players";
import type { Player } from "../../types/api";

export const PLAYER_STORAGE_KEY = "neuroquest.player_id";

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

export function usePlayer() {
  const [playerId] = useState(readInitialPlayerId);
  const [player, setPlayer] = useState<Player | null>(null);
  const [loading, setLoading] = useState(() => !!playerId);

  useEffect(() => {
    if (!playerId) return;
    playersApi
      .get(playerId)
      .then(setPlayer)
      .catch(() => localStorage.removeItem(PLAYER_STORAGE_KEY))
      .finally(() => setLoading(false));
  }, [playerId]);

  return { player, loading };
}
