import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePlayer } from "../features/player/usePlayer";
import { questsApi } from "../api/quests";
import { ApiError } from "../api/client";
import "./HomePage.css";

export function HomePage() {
  const { player, loading, createPlayer } = usePlayer();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [qrToken, setQrToken] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  if (loading) return <div className="home-page__status">Загрузка...</div>;

  const handleCreatePlayer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    await createPlayer(name.trim());
  };

  const handleStartQuest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!player || !qrToken.trim()) return;
    setError(null);
    setStarting(true);
    try {
      const session = await questsApi.start(player.id, qrToken.trim());
      navigate(`/quest/${session.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Что-то пошло не так");
    } finally {
      setStarting(false);
    }
  };

  if (!player) {
    return (
      <div className="home-page">
        <h1>NeuroQuest</h1>
        <form onSubmit={handleCreatePlayer} className="home-page__form">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Как тебя зовут?"
            autoFocus
          />
          <button type="submit">Начать</button>
        </form>
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
    </div>
  );
}
