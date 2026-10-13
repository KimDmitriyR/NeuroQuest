import { Link, useNavigate } from "react-router-dom";
import { useSession } from "../features/session/useSession";
import "./SettingsPage.css";

const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" });

export function SettingsPage() {
  const { player, parent, clearPlayer, logoutParent, signOutAll } = useSession();
  const navigate = useNavigate();

  return (
    <div className="page page--narrow">
      <h1 className="page-title">Настройки</h1>
      <p className="page-subtitle">Аккаунт, профиль ребёнка и документы</p>

      <section className="card settings-card">
        <h2>Аккаунт родителя</h2>
        {parent ? (
          <>
            <dl className="settings-list">
              <div><dt>Email</dt><dd>{parent.email}</dd></div>
              <div><dt>Согласие с документами</dt><dd>{formatDate(parent.terms_accepted_at)} · версия {parent.terms_version}</dd></div>
            </dl>
            <div className="settings-actions">
              <Link className="btn btn--ghost" to="/parent">Открыть кабинет</Link>
              <button className="btn btn--danger" onClick={logoutParent}>Выйти из аккаунта</button>
            </div>
          </>
        ) : (
          <>
            <p className="settings-note">Вы не вошли. Кабинет родителя нужен, чтобы создавать профили детей и проверять миссии.</p>
            <div className="settings-actions">
              <Link className="btn" to="/parent">Войти или зарегистрироваться</Link>
            </div>
          </>
        )}
      </section>

      <section className="card settings-card">
        <h2>Профиль ребёнка на этом устройстве</h2>
        {player ? (
          <>
            <dl className="settings-list">
              <div><dt>Играет</dt><dd>{player.name}</dd></div>
            </dl>
            <div className="settings-actions">
              <Link className="btn btn--ghost" to="/profile">Мой профиль</Link>
              <button className="btn btn--danger" onClick={clearPlayer}>Выйти из профиля ребёнка</button>
            </div>
          </>
        ) : (
          <>
            <p className="settings-note">Профиль не выбран. Его создаёт родитель в кабинете и открывает на этом устройстве.</p>
            <div className="settings-actions">
              <Link className="btn btn--ghost" to="/parent">Кабинет родителя</Link>
            </div>
          </>
        )}
      </section>

      <section className="card settings-card">
        <h2>Документы</h2>
        <div className="settings-actions">
          <Link className="btn btn--ghost" to="/terms">Пользовательское соглашение</Link>
          <Link className="btn btn--ghost" to="/privacy">Политика конфиденциальности</Link>
        </div>
      </section>

      {(player || parent) && (
        <button
          className="btn btn--danger btn--block settings-signout"
          onClick={() => {
            signOutAll();
            navigate("/");
          }}
        >
          Выйти из всего на этом устройстве
        </button>
      )}
    </div>
  );
}
