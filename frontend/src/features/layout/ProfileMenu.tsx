import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../session/useSession";
import { Icon, type IconName } from "./Icon";
import "./ProfileMenu.css";

interface MenuItemProps {
  icon: IconName;
  danger?: boolean;
  onClick: () => void;
  children: string;
}

function MenuItem({ icon, danger, onClick, children }: MenuItemProps) {
  return (
    <button
      type="button"
      role="menuitem"
      className={`profile-menu__item${danger ? " profile-menu__item--danger" : ""}`}
      onClick={onClick}
    >
      <Icon name={icon} size={20} />
      <span>{children}</span>
    </button>
  );
}

/** Top-right profile button with a dropdown (profile, settings, sign out...). */
export function ProfileMenu() {
  const { player, parent, signOutAll } = useSession();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (e: PointerEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const go = (to: string) => {
    setOpen(false);
    navigate(to);
  };

  const displayName = player?.name ?? (parent ? "Родитель" : "Войти");
  const initialSource = player?.name ?? parent?.email ?? "";
  const initial = initialSource ? initialSource.charAt(0).toUpperCase() : null;
  const signedIn = !!player || !!parent;

  return (
    <div className="profile-menu" ref={rootRef}>
      <button
        type="button"
        className="profile-menu__button"
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
      >
        <span className="profile-menu__avatar">
          {initial ?? <Icon name="user" size={20} />}
        </span>
        <span className="profile-menu__label">{displayName}</span>
        <span className={`profile-menu__chevron${open ? " profile-menu__chevron--open" : ""}`}>
          <Icon name="chevron" size={16} />
        </span>
      </button>

      {open && (
        <div className="profile-menu__panel" role="menu">
          <div className="profile-menu__head">
            <span className="profile-menu__avatar profile-menu__avatar--large">
              {initial ?? <Icon name="user" size={24} />}
            </span>
            <div className="profile-menu__who">
              <div className="profile-menu__name">{player?.name ?? "Гость"}</div>
              <div className="profile-menu__sub">
                {parent
                  ? `Родитель: ${parent.email}`
                  : player
                    ? "Профиль ребёнка"
                    : "Профиль не выбран"}
              </div>
            </div>
          </div>

          <MenuItem icon="trophy" onClick={() => go("/profile")}>Мой профиль</MenuItem>
          <MenuItem icon="mail" onClick={() => go("/missions")}>Конверты с миссиями</MenuItem>
          <MenuItem icon="users" onClick={() => go("/parent")}>Кабинет родителя</MenuItem>
          <MenuItem icon="sliders" onClick={() => go("/settings")}>Настройки</MenuItem>

          {signedIn && (
            <>
              <div className="profile-menu__divider" />
              <MenuItem
                icon="logout"
                danger
                onClick={() => {
                  setOpen(false);
                  signOutAll();
                  navigate("/");
                }}
              >
                Выйти
              </MenuItem>
            </>
          )}

          <div className="profile-menu__legal">
            <button type="button" onClick={() => go("/terms")}>Соглашение</button>
            <span>·</span>
            <button type="button" onClick={() => go("/privacy")}>Конфиденциальность</button>
          </div>
        </div>
      )}
    </div>
  );
}
