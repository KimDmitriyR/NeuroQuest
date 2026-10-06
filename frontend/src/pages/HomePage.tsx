import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePlayer } from "../features/player/usePlayer";
import { questsApi } from "../api/quests";
import { ApiError } from "../api/client";
import "./HomePage.css";

function consumeQuestParamFromUrl(): string | null {
  const url = new URL(window.location.href);
  const token = url.searchParams.get("quest");
  if (!token) return null;
  url.searchParams.delete("quest");
  window.history.replaceState({}, "", url.toString());
  return token;
}

export function HomePage() {
  const { player, loading } = usePlayer();
  const navigate = useNavigate();

  const [qrToken, setQrToken] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  const startQuest = async (token: string) => {
    if (!player || !token.trim()) return;
    setError(null);
    setStarting(true);
    try {
      const session = await questsApi.start(player.id, token.trim());
      navigate(`/quest/${session.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Что-то пошло не так");
    } finally {
      setStarting(false);
    }
  };

  // a scanned QR code lands here as /?quest=<token> - auto-start immediately
  // once we know who's playing, instead of making them retype the code
  useEffect(() => {
    if (loading) return;
    const token = consumeQuestParamFromUrl();
    if (token && player) startQuest(token);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading, player]);

  if (loading) return <div className="home-page__status">Загрузка...</div>;

  const handleStartQuest = (e: React.FormEvent) => {
    e.preventDefault();
    startQuest(qrToken);
  };

  if (!player) {
    return (
      <div className="home-page">
        <h1>NeuroQuest</h1>
        <p className="home-page__hint">
          Чтобы начать играть, попроси родителя открыть личный кабинет и
          создать тебе профиль.
        </p>
        <a className="home-page__parent-link" href="/parent">
          Кабинет родителя →
        </a>
      </div>
    );
  }

  return (
    <div className="home-page">
      <h1>Привет, {player.name}!</h1>
      <p className="home-page__hint">Отсканируй QR-код на карточке или введи его код:</p>
      <form onSubmit={handleStartQuest} className="home-page__form">
        <input
          value={qrToken}
          onChange={(e) => setQrToken(e.target.value)}
          placeholder="например, finstartup-2-0-01"
          autoFocus
        />
        <button type="submit" disabled={starting}>
          {starting ? "Загрузка..." : "Начать квест"}
        </button>
      </form>
      {error && <div className="home-page__error">{error}</div>}
      <a className="home-page__profile-link" href="/missions">
        Конверты с миссиями →
      </a>
      <a className="home-page__profile-link" href="/profile">
        Мой профиль →
      </a>
      <a className="home-page__parent-link" href="/parent">
        Кабинет родителя
      </a>
      <div className="home-page__legal-links">
        <a href="/terms">Пользовательское соглашение</a>
        {" · "}
        <a href="/privacy">Политика конфиденциальности</a>
      </div>
    </div>
  );
}
