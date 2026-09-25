import { api } from "./client";
import type {
  EarnedAchievementView,
  MasterCodeProgressView,
  Player,
} from "../types/api";

export const playersApi = {
  create: (name: string) => api.post<Player>("/api/players", { name }),
  get: (playerId: string) => api.get<Player>(`/api/players/${playerId}`),
  achievements: (playerId: string) =>
    api.get<EarnedAchievementView[]>(`/api/players/${playerId}/achievements`),
  masterCode: (playerId: string) =>
    api.get<MasterCodeProgressView>(`/api/players/${playerId}/master-code`),
};
