import { createContext } from "react";
import type { ParentRead, Player } from "../../types/api";

export interface SessionValue {
  /** child profile active on this device (null = nobody selected) */
  player: Player | null;
  playerLoading: boolean;
  clearPlayer: () => void;
  /** make this device play as the child the token belongs to */
  activatePlayerToken: (token: string) => void;

  /** logged-in parent (null = not logged in) */
  parent: ParentRead | null;
  parentLoading: boolean;
  login: (email: string, password: string) => Promise<ParentRead>;
  register: (
    email: string,
    password: string,
    acceptTerms: boolean,
  ) => Promise<ParentRead>;
  logoutParent: () => void;

  /** sign out of everything on this device: parent + active child */
  signOutAll: () => void;
}

export const SessionContext = createContext<SessionValue | null>(null);
