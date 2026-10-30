import { useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { QuestCodeForm } from "../features/layout/QuestCodeForm";
import { Mascot, Sparkle } from "../features/brand/Mascot";
import { Icon, type IconName } from "../features/layout/Icon";
import { useStartQuest } from "../features/quest/useStartQuest";
import { ProgressTiles } from "../features/progress/ProgressTiles";
import { useSession } from "../features/session/useSession";
import "./HomePage.css";

// a scanned QR code opens the site as /?quest=<token>; a guest has to sign in
// first, so the code waits here until a child profile is active
const PENDING_QUEST_KEY = "neuroquest.pending_quest";

function consumeQuestParamFromUrl(): string | null {
  const url = new URL(window.location.href);
  const token = url.searchParams.get("quest");
  if (!token) return null;
  url.searchParams.delete("quest");
  window.history.replaceState({}, "", url.toString());
  return token;
}

interface Section { to: string; icon: IconName; title: string; text: string; tone: string }

/** Quick links shown to signed-in users only; each is limited to who can use it. */
function sectionsFor(hasPlayer: boolean, hasParent: boolean): Section[] {
  return [
    { to: "/missions", icon: "mail", title: "Конверты с миссиями", text: "Задания из реального мира: фото, шифры, алгоритмы", tone: "coral" },
    ...(hasPlayer ? [{ to: "/profile", icon: "trophy", title: "Мои достижения", text: "Награды и собранный мастер-код", tone: "butter" } as Section] : []),
    ...(hasParent ? [{ to: "/parent", icon: "users", title: "Кабинет родителя", text: "Профили детей и проверка миссий", tone: "cobalt" } as Section] : []),
    { to: "/settings", icon: "sliders", title: "Настройки", text: "Аккаунт, профиль и документы", tone: "lilac" },
  ];
}

const SECTORS = [
  { tone: "coral", kind: "bean", title: "Финансы", text: "Деньги, покупки и уловки, на которые легко попасться" },
  { tone: "cobalt", kind: "squircle", title: "Кибербезопасность", text: "Пароли, мошенники и что делать, если что-то пошло не так" },
  { tone: "lilac", kind: "cloud", title: "Искусственный интеллект", text: "Как работают нейросети и когда им нельзя верить" },
] as const;

const STEPS = [
  { n: 1, title: "Родитель создаёт профиль", text: "Регистрация в кабинете родителя и профиль для ребёнка." },
  { n: 2, title: "Сканируй карточку", text: "QR-код на карточке запускает квест — или введи код вручную." },
  { n: 3, title: "Проходи и собирай", text: "Выбирай решения, получай достижения и буквы мастер-кода." },
];

export function HomePage() {
  const { player, parent, playerLoading, parentLoading } = useSession();
  const { start } = useStartQuest();
  const navigate = useNavigate();
  const signedIn = !!player || !!parent;
  const sections = sectionsFor(!!player, !!parent);

  // QR landing: remember the scanned code, then start it as soon as a child
  // profile is active. Guests and parents without a child go to sign-in first.
  useEffect(() => {
    if (playerLoading || parentLoading) return;
    const scanned = consumeQuestParamFromUrl();
    if (scanned) sessionStorage.setItem(PENDING_QUEST_KEY, scanned);

    if (player) {
      const token = sessionStorage.getItem(PENDING_QUEST_KEY);
      if (token) {
        sessionStorage.removeItem(PENDING_QUEST_KEY);
        start(token);
      }
    } else if (scanned) {
      navigate("/parent", {
        replace: true,
        state: {
          notice: parent
            ? "Выбери профиль ребёнка («Играть на этом устройстве»), и карточка откроется."
            : "Чтобы открыть карточку, войди или зарегистрируйся.",
        },
      });
    }
  }, [playerLoading, parentLoading, player, parent, start, navigate]);

  return (
    <>
      <section className="hero">
        <Mascot kind="cloud" size={150} className="hero__mascot hero__mascot--cloud" />
        <Mascot kind="squircle" size={128} className="hero__mascot hero__mascot--squircle" />
        <Mascot kind="bean" size={86} className="hero__mascot hero__mascot--bean" />
        <Sparkle size={30} className="hero__sparkle hero__sparkle--a" />
        <Sparkle size={20} color="var(--lilac)" className="hero__sparkle hero__sparkle--b" />
        <Sparkle size={24} color="var(--coral)" className="hero__sparkle hero__sparkle--c" />

        <div className="hero__inner">
          <h1 className="hero__title">
            {player ? (
              <>Привет, {player.name}!</>
            ) : (
              <>
                Квесты, которые учат
                <span className="hero__script">жить в цифровом мире</span>
              </>
            )}
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
              <Link className="btn hero__cta" to="/parent">Войти или зарегистрироваться</Link>
              <span className="hero__note">Профиль ребёнка создаёт родитель</span>
            </div>
          )}
        </div>

        <ul className="sectors">
          {SECTORS.map((s) => (
            <li key={s.title} className={`sector sector--${s.tone}`}>
              <div className="sector__title">{s.title}</div>
              <p className="sector__text">{s.text}</p>
              <Mascot kind={s.kind} size={74} className="sector__mascot" />
            </li>
          ))}
        </ul>
      </section>

      <div className="page home">
        {player && (
          <>
            <h2 className="home__title">Твой прогресс</h2>
            <ProgressTiles playerId={player.id} />
          </>
        )}

        {!player && (
          <>
            <h2 className="home__title">Простой путь к первому квесту</h2>
            <ol className="steps">
              {STEPS.map((s) => (
                <li key={s.n} className={`step step--${s.n}`}>
                  <span className="step__n">{s.n}</span>
                  <div className="step__title">{s.title}</div>
                  <p className="step__text">{s.text}</p>
                </li>
              ))}
            </ol>
          </>
        )}

        {signedIn && (
          <>
            <h2 className="home__title">Разделы</h2>
            <div className="quick-grid">
              {sections.map((s) => (
                <Link key={s.to} to={s.to} className="quick-tile">
                  <span className={`quick-tile__icon quick-tile__icon--${s.tone}`}><Icon name={s.icon} size={26} /></span>
                  <span className="quick-tile__title">{s.title}</span>
                  <span className="quick-tile__text">{s.text}</span>
                </Link>
              ))}
            </div>
          </>
        )}

        {!player && (
          <section className="cta-band">
            <Mascot kind="bean" size={110} className="cta-band__mascot" />
            <div className="cta-band__body">
              <h2 className="cta-band__title">Учимся, играя</h2>
              <p className="cta-band__text">
                Начни с кабинета родителя: создай профиль ребёнка и выдай ему ссылку, чтобы он играл со своего устройства.
              </p>
              <Link className="btn btn--white" to="/parent">Создать профиль</Link>
            </div>
          </section>
        )}
      </div>
    </>
  );
}
