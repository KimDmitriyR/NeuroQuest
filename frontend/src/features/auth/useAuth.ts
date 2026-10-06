import { useCallback, useEffect, useState } from "react";
import { authApi } from "../../api/auth";
import { PARENT_TOKEN_KEY } from "../../api/client";
import type { ParentRead } from "../../types/api";

export function useAuth() {
  const [parent, setParent] = useState<ParentRead | null>(null);
  const [loading, setLoading] = useState(() => !!localStorage.getItem(PARENT_TOKEN_KEY));

  useEffect(() => {
    if (!localStorage.getItem(PARENT_TOKEN_KEY)) return;
    authApi
      .me()
      .then(setParent)
      .catch(() => localStorage.removeItem(PARENT_TOKEN_KEY))
      .finally(() => setLoading(false));
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

  const logout = useCallback(() => {
    localStorage.removeItem(PARENT_TOKEN_KEY);
    setParent(null);
  }, []);

  return { parent, loading, login, register, logout };
}
