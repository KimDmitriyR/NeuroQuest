import { useNavigate } from "react-router-dom";
import { usePlayer } from "../features/player/usePlayer";
import { MasterCodeBoard } from "../features/progress/MasterCodeBoard";
import { AchievementList } from "../features/progress/AchievementList";
import "./ProfilePage.css";

export function ProfilePage() {
  const { player, loading } = usePlayer();
  const navigate = useNavigate();

  if (loading) return <div className="profile-page__status">Загрузка...</div>;
  if (!player) {
    return (
      <div className="profile-page__status">
        Сначала создай игрока.
        <button onClick={() => navigate("/")}>На главную</button>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <header className="profile-page__header">
        <button className="profile-page__back" onClick={() => navigate("/")}>
          ← Домой
        </button>
        <h1>{player.name}</h1>
      </header>

      <MasterCodeBoard playerId={player.id} />

      <h2 className="profile-page__section-title">Достижения</h2>
      <AchievementList playerId={player.id} />
    </div>
  );
}
