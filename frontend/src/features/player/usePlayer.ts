import { useSession } from "../session/useSession";

/** Active child profile on this device (shared app-wide via SessionProvider). */
export function usePlayer() {
  const { player, playerLoading, clearPlayer } = useSession();
  return { player, loading: playerLoading, clearPlayer };
}
