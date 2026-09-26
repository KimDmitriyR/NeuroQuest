import { useNavigate, useParams } from "react-router-dom";
import { usePlayer } from "../features/player/usePlayer";
import { MissionFlow } from "../features/mission/MissionFlow";
import "./MissionPage.css";

export function MissionPage() {
  const { missionId } = useParams<{ missionId: string }>();
  const { player, loading } = usePlayer();
  const navigate = useNavigate();

  if (loading) return <div className="mission-page__status">Загрузка...</div>;
  if (!player) {
    return (
      <div className="mission-page__status">
        Сначала создай игрока.
        <button onClick={() => navigate("/")}>На главную</button>
      </div>
    );
  }
  if (!missionId) return null;

  return (
    <div className="mission-page">
      <header className="mission-page__header">
        <button className="mission-page__back" onClick={() => navigate("/missions")}>
          ← Конверты
        </button>
      </header>
      <MissionFlow missionId={missionId} playerId={player.id} />
    </div>
  );
}
