import type { ReactNode } from "react";
import { SessionContext } from "./session-context";
import { useSessionState } from "./useSessionState";

export function SessionProvider({ children }: { children: ReactNode }) {
  const value = useSessionState();
  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}
