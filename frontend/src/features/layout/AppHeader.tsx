import { Link, NavLink, useLocation } from "react-router-dom";
import { Icon } from "./Icon";
import { ProfileMenu } from "./ProfileMenu";
import { QuestCodeForm } from "./QuestCodeForm";

const navClass = ({ isActive }: { isActive: boolean }) =>
  `app-header__nav-item${isActive ? " app-header__nav-item--active" : ""}`;

export function AppHeader() {
  const { pathname } = useLocation();
  // the home page hero has its own big code field, don't show two
  const hideSearch = pathname === "/";

  return (
    <header className={`app-header${hideSearch ? " app-header--no-search" : ""}`}>
      <div className="app-header__bar">
        <Link to="/" className="app-logo" aria-label="NeuroQuest — на главную">
          <span className="app-logo__mark">NQ</span>
          <span className="app-logo__text">NeuroQuest</span>
        </Link>

        <div className="app-header__search">
          <QuestCodeForm variant="header" />
        </div>

        <nav className="app-header__nav" aria-label="Основное меню">
          <NavLink to="/missions" className={navClass}>
            <Icon name="mail" />
            <span>Конверты</span>
          </NavLink>
          <NavLink to="/profile" className={navClass}>
            <Icon name="trophy" />
            <span>Достижения</span>
          </NavLink>
        </nav>

        <ProfileMenu />
      </div>
    </header>
  );
}
