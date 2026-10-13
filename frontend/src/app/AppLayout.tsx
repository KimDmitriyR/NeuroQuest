import { useEffect } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import { AppHeader } from "../features/layout/AppHeader";
import { BottomNav } from "../features/layout/BottomNav";
import "./AppLayout.css";

export function AppLayout() {
  const { pathname } = useLocation();
  // the quest chat is a full-height screen: no footer and no tab bar there
  const immersive = pathname.startsWith("/quest");

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return (
    <div className={`app-shell${immersive ? " app-shell--immersive" : ""}`}>
      <AppHeader />
      <main className="app-main">
        <Outlet />
      </main>
      {!immersive && (
        <footer className="app-footer">
          <Link to="/terms">Пользовательское соглашение</Link>
          <Link to="/privacy">Политика конфиденциальности</Link>
          <span>© NeuroQuest</span>
        </footer>
      )}
      {!immersive && <BottomNav />}
    </div>
  );
}
