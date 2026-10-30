import { NavLink } from "react-router-dom";
import { useSession } from "../session/useSession";
import { Icon, type IconName } from "./Icon";

interface Item { to: string; label: string; icon: IconName; end?: boolean }

const HOME: Item = { to: "/", label: "Главная", icon: "home", end: true };

/** Tabs depend on who is signed in; guests only get sign-in and settings. */
function tabsFor(hasPlayer: boolean, hasParent: boolean): Item[] {
  if (!hasPlayer && !hasParent) {
    return [
      HOME,
      { to: "/parent", label: "Войти", icon: "user" },
      { to: "/settings", label: "Настройки", icon: "sliders" },
    ];
  }
  return [
    HOME,
    { to: "/missions", label: "Конверты", icon: "mail" },
    ...(hasPlayer ? [{ to: "/profile", label: "Профиль", icon: "trophy" } as Item] : []),
    ...(hasParent ? [{ to: "/parent", label: "Родителям", icon: "users" } as Item] : []),
  ];
}

/** Mobile tab bar, like in marketplace apps. Hidden on wide screens via CSS. */
export function BottomNav() {
  const { player, parent } = useSession();
  const items = tabsFor(!!player, !!parent);
  return (
    <nav className="bottom-nav" aria-label="Навигация">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          className={({ isActive }) =>
            `bottom-nav__item${isActive ? " bottom-nav__item--active" : ""}`
          }
        >
          <Icon name={item.icon} size={24} />
          <span>{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
