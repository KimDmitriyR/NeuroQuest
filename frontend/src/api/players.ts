import { api } from "./client";
import type {
  EarnedAchievementView,
  MasterCodeProgressView,
  Player,
  PlayerToken,
} from "../types/api";

export const playersApi = {
  create: (name: string) => api.post<Player>("/api/players", { name }),
  /** the child this device's own token belongs to */
  me: () => api.get<Player>("/api/players/me"),
  /** parent-only: credential for the child's device (goes into the child link) */
  issueToken: (playerId: string) =>
    api.post<PlayerToken>(`/api/players/${playerId}/access-token`),
  /** parent-only: revoke every old link/device of this child, get a fresh token */
  resetToken: (playerId: string) =>
    api.post<PlayerToken>(`/api/players/${playerId}/access-token/reset`),
  get: (playerId: string) => api.get<Player>(`/api/players/${playerId}`),
  achievements: (playerId: string) =>
    api.get<EarnedAchievementView[]>(`/api/players/${playerId}/achievements`),
  masterCode: (playerId: string) =>
    api.get<MasterCodeProgressView>(`/api/players/${playerId}/master-code`),
};
