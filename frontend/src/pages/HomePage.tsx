import { useEffect } from "react";
import { Link } from "react-router-dom";
import { QuestCodeForm } from "../features/layout/QuestCodeForm";
import { Icon, type IconName } from "../features/layout/Icon";
import { useStartQuest } from "../features/quest/useStartQuest";
import { ProgressTiles } from "../features/progress/ProgressTiles";
import { useSession } from "../features/session/useSession";
import "./HomePage.css";

// a scanned QR code opens the site as /?quest=<token>
function consumeQuestParamFromUrl(): string | null {
  const url = new URL(window.location.href);
  const token = url.searchParams.get("quest");
  if (!token) return null;
  url.searchParams.delete("quest");
  window.history.replaceState({}, "", url.toString());
  return token;
}

const SECTIONS: { to: string; icon: IconName; title: string; text: string }[] = [
  { to: "/missions", icon: "mail", title: "Конверты с миссиями", text: "Задания из реального мира: фото, шифры, алгоритмы" },
  { to: "/profile", icon: "trophy", title: "Мои достижения", text: "Награды и собранный мастер-код" },
  { to: "/parent", icon: "users", title: "Кабинет родителя", text: "Профили детей и проверка миссий" },
  { to: "/settings", icon: "sliders", title: "Настройки", text: "Аккаунт, профиль и документы" },
];

const STEPS = [
  { n: 1, title: "Родитель создаёт профиль", text: "Регистрация в кабинете родителя и профиль для ребёнка." },
  { n: 2, title: "Сканируй карточку", text: "QR-код на карточке запускает квест — или введи код вручную." },
  { n: 3, title: "Проходи и собирай", text: "Выбирай решения, получай достижения и буквы мастер-кода." },
];

export function HomePage() {
  const { player, playerLoading } = useSession();
  const { start } = useStartQuest();

  // QR landing: start the scanned quest as soon as we know who is playing
  useEffect(() => {
    if (playerLoading || !player) return;
    const token = consumeQuestParamFromUrl();
    if (token) start(token);
  }, [playerLoading, player, start]);

  return (
    <>
      <section className="hero">
        <div className="hero__inner">
          <div className="hero__text">
            <span className="hero__badge">Образовательные квесты</span>
            <h1 className="hero__title">
              {player ? `Привет, ${player.name}! 👋` : "Квесты, которые учат жить в цифровом мире"}
            </h1>
            <p className="hero__lead">
              {player
                ? "Отсканируй QR-код на карточке или введи её код — и квест начнётся."
                : "Финансы, кибербезопасность и искусственный интеллект — в формате игры с карточками и заданиями."}
            </p>
            {player ? (
              <div className="hero__form"><QuestCodeForm variant="hero" /></div>
            ) : (
              <div className="hero__actions">
                <Link className="btn btn--white" to="/parent">Кабинет родителя</Link>
                <span className="hero__note">Профиль ребёнка создаёт родитель</span>
              </div>
            )}
          </div>

          <div className="hero__art" aria-hidden="true">
            <div className="hero-card hero-card--a"><span>💸</span>Финансы</div>
            <div className="hero-card hero-card--b"><span>🛡️</span>Кибербезопасность</div>
            <div className="hero-card hero-card--c"><span>🤖</span>ИИ</div>
          </div>
        </div>
      </section>

      <div className="page">
        {player && (
          <>
            <h2 className="section-title section-title--first">Твой прогресс</h2>
            <ProgressTiles playerId={player.id} />
          </>
        )}

        <h2 className={`section-title${player ? "" : " section-title--first"}`}>Разделы</h2>
        <div className="quick-grid">
          {SECTIONS.map((s) => (
            <Link key={s.to} to={s.to} className="quick-tile card">
              <span className="quick-tile__icon"><Icon name={s.icon} size={26} /></span>
              <span className="quick-tile__title">{s.title}</span>
              <span className="quick-tile__text">{s.text}</span>
            </Link>
          ))}
        </div>

        {!player && (
          <>
            <h2 className="section-title">Как это работает</h2>
            <div className="steps">
              {STEPS.map((s) => (
                <div key={s.n} className="step card">
                  <span className="step__n">{s.n}</span>
                  <div className="step__title">{s.title}</div>
                  <div className="step__text">{s.text}</div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </>
  );
}
