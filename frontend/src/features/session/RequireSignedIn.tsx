import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useSession } from "./useSession";

/**
 * Route guard. Anyone who is not signed in (no parent login and no child
 * profile on this device) is sent to the login/registration screen and brought
 * back to where they were headed once they sign in.
 *
 * `parentOnly` is for screens that only make sense for a logged-in parent.
 * The API enforces the same rules; this just keeps people off dead screens.
 */
export function RequireSignedIn({ parentOnly = false }: { parentOnly?: boolean }) {
  const { player, parent, playerLoading, parentLoading } = useSession();
  const location = useLocation();

  if (playerLoading || parentLoading) {
    return <div className="page"><div className="state-box">Загрузка...</div></div>;
  }

  const allowed = parentOnly ? !!parent : !!player || !!parent;
  if (!allowed) {
    return (
      <Navigate
        to="/parent"
        replace
        state={{
          from: location.pathname + location.search,
          notice: "Войди или зарегистрируйся, чтобы продолжить.",
        }}
      />
    );
  }
  return <Outlet />;
}
