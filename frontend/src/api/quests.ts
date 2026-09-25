import { api } from "./client";
import type { ChoiceResultView, SessionView } from "../types/api";

export const questsApi = {
  start: (playerId: string, qrToken: string) =>
    api.post<SessionView>("/api/quests/start", {
      player_id: playerId,
      qr_token: qrToken,
    }),
  getSession: (sessionId: string) =>
    api.get<SessionView>(`/api/quests/sessions/${sessionId}`),
  submitChoice: (sessionId: string, choiceId: string) =>
    api.post<ChoiceResultView>(`/api/quests/sessions/${sessionId}/choices`, {
      choice_id: choiceId,
    }),
};
