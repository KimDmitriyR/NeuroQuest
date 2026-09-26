import { api } from "./client";
import type { AttemptView, MissionView, SubmitAttemptResultView } from "../types/api";

export const missionsApi = {
  get: (missionId: string) => api.get<MissionView>(`/api/missions/${missionId}`),
  startAttempt: (missionId: string, playerId: string) =>
    api.post<AttemptView>(`/api/missions/${missionId}/attempts`, {
      player_id: playerId,
    }),
  submitAttempt: (attemptId: string, photoUrl?: string, textAnswer?: string) =>
    api.post<SubmitAttemptResultView>(`/api/missions/attempts/${attemptId}/submit`, {
      photo_url: photoUrl ?? null,
      text_answer: textAnswer ?? null,
    }),
};
