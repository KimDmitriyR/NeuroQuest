import { useNavigate } from "react-router-dom";
import { usePlayer } from "../features/player/usePlayer";
import { useMissions } from "../features/mission/useMission";
import "./MissionsPage.css";

export function MissionsPage() {
  const { player, loading } = usePlayer();
  const { data: missions, isLoading } = useMissions();
  const navigate = useNavigate();

  if (loading || isLoading) return <div className="missions-page__status">Загрузка...</div>;
  if (!player) {
    return (
      <div className="missions-page__status">
        Сначала создай игрока.
        <button onClick={() => navigate("/")}>На главную</button>
      </div>
    );
  }

  return (
    <div className="missions-page">
      <header className="missions-page__header">
        <button className="missions-page__back" onClick={() => navigate("/")}>
          ← Домой
        </button>
        <h1>Конверты с миссиями</h1>
      </header>
      <ul className="missions-page__list">
        {missions?.map((mission) => (
          <li key={mission.id}>
            <button
              className="missions-page__item"
              onClick={() => navigate(`/mission/${mission.id}`)}
            >
              <span className="missions-page__icon">
                {mission.validation_type === "photo" ? "📷" : "🔐"}
              </span>
              <span>
                <div className="missions-page__item-title">{mission.title}</div>
                <div className="missions-page__item-desc">{mission.description}</div>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
