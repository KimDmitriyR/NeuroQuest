import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { usePlayer } from "../features/player/usePlayer";
import { MasterCodeBoard } from "../features/progress/MasterCodeBoard";
import { AchievementList } from "../features/progress/AchievementList";
import { playersApi } from "../api/players";
import "./ProfilePage.css";

export function ProfilePage() {
  const { player, loading } = usePlayer();
  const navigate = useNavigate();
  const { data: masterCode } = useQuery({
    queryKey: ["master-code", player?.id],
    queryFn: () => playersApi.masterCode(player!.id),
    enabled: !!player,
  });

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

      {masterCode?.is_complete && (
        <button className="profile-page__finale-button" onClick={() => navigate("/finale")}>
          🎉 Открыть гранд-финал
        </button>
      )}

      <h2 className="profile-page__section-title">Достижения</h2>
      <AchievementList playerId={player.id} />
    </div>
  );
}
