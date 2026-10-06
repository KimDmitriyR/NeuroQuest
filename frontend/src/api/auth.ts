import { api } from "./client";
import type { ParentRead, Player, TokenResponse } from "../types/api";

export const authApi = {
  register: (email: string, password: string, acceptTerms: boolean) =>
    api.post<TokenResponse>("/api/auth/register", {
      email,
      password,
      accept_terms: acceptTerms,
    }),
  login: (email: string, password: string) =>
    api.post<TokenResponse>("/api/auth/login", { email, password }),
  me: () => api.get<ParentRead>("/api/auth/me"),
};

export const parentsApi = {
  listChildren: () => api.get<Player[]>("/api/parents/me/children"),
};
