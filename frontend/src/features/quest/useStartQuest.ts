import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError } from "../../api/client";
import { questsApi } from "../../api/quests";
import { useSession } from "../session/useSession";

/** Starts a quest by its card code (what a QR code encodes) for the active child. */
export function useStartQuest() {
  const { player } = useSession();
  const navigate = useNavigate();
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const start = useCallback(
    async (code: string) => {
      const token = code.trim();
      if (!token) return;
      if (!player) {
        setError("Сначала нужен профиль ребёнка — его создаёт родитель в кабинете");
        return;
      }
      setError(null);
      setStarting(true);
      try {
        const session = await questsApi.start(player.id, token);
        navigate(`/quest/${session.id}`);
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) {
          setError("Карточка с таким кодом не найдена");
        } else {
          setError("Не получилось начать квест, попробуй ещё раз");
        }
      } finally {
        setStarting(false);
      }
    },
    [player, navigate],
  );

  return { start, starting, error, clearError: () => setError(null) };
}
