import { useCallback, useEffect, useState } from "react";
import { playersApi } from "../../api/players";
import type { Player } from "../../types/api";

const STORAGE_KEY = "neuroquest.player_id";

export function usePlayer() {
  const [player, setPlayer] = useState<Player | null>(null);
  const [loading, setLoading] = useState(() => !!localStorage.getItem(STORAGE_KEY));

  useEffect(() => {
    const storedId = localStorage.getItem(STORAGE_KEY);
    if (!storedId) return;
    playersApi
      .get(storedId)
      .then(setPlayer)
      .catch(() => localStorage.removeItem(STORAGE_KEY))
      .finally(() => setLoading(false));
  }, []);

  const createPlayer = useCallback(async (name: string) => {
    const created = await playersApi.create(name);
    localStorage.setItem(STORAGE_KEY, created.id);
    setPlayer(created);
    return created;
  }, []);

  return { player, loading, createPlayer };
}
