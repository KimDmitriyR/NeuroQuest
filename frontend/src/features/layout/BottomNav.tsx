import { NavLink } from "react-router-dom";
import { Icon, type IconName } from "./Icon";

const ITEMS: { to: string; label: string; icon: IconName; end?: boolean }[] = [
  { to: "/", label: "Главная", icon: "home", end: true },
  { to: "/missions", label: "Конверты", icon: "mail" },
  { to: "/profile", label: "Профиль", icon: "trophy" },
  { to: "/parent", label: "Родителям", icon: "users" },
];

/** Mobile tab bar, like in marketplace apps. Hidden on wide screens via CSS. */
export function BottomNav() {
  return (
    <nav className="bottom-nav" aria-label="Навигация">
      {ITEMS.map((item) => (
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
