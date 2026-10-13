import { useSession } from "../session/useSession";

/** Logged-in parent (shared app-wide via SessionProvider). */
export function useAuth() {
  const { parent, parentLoading, login, register, logoutParent } = useSession();
  return { parent, loading: parentLoading, login, register, logout: logoutParent };
}
