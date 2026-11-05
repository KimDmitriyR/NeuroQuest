import { Link, NavLink, useLocation } from "react-router-dom";
import { useSession } from "../session/useSession";
import { Icon } from "./Icon";
import { ProfileMenu } from "./ProfileMenu";
import { QuestCodeForm } from "./QuestCodeForm";
import wordmark from "../../assets/brand/logo-wordmark.png";

const navClass = ({ isActive }: { isActive: boolean }) =>
  `app-header__nav-item${isActive ? " app-header__nav-item--active" : ""}`;

export function AppHeader() {
  const { pathname } = useLocation();
  const { player, parent } = useSession();
  const signedIn = !!player || !!parent;
  // the home page hero has its own big code field, don't show two;
  // a code can only be entered by a child profile
  const hideSearch = pathname === "/" || !player;

  return (
    <header
      className={`app-header${hideSearch ? " app-header--no-search" : ""}${signedIn ? "" : " app-header--guest"}`}
    >
      <div className="app-header__bar">
        <Link to="/" className="app-logo" aria-label="NeuroQuest — на главную">
          <span className="app-logo__mark">NQ</span>
          <img className="app-logo__word" src={wordmark} width={565} height={100} alt="НЕЙРОКВЕСТ" />
        </Link>

        {player && (
          <div className="app-header__search">
            <QuestCodeForm variant="header" />
          </div>
        )}

        {/* before signing in the right side holds only the sign-in/settings menu */}
        {signedIn && (
          <nav className="app-header__nav" aria-label="Основное меню">
            <NavLink to="/missions" className={navClass}>
              <Icon name="mail" />
              <span>Конверты</span>
            </NavLink>
            {player && (
              <NavLink to="/profile" className={navClass}>
                <Icon name="trophy" />
                <span>Достижения</span>
              </NavLink>
            )}
          </nav>
        )}

        <ProfileMenu />
      </div>
    </header>
  );
}
