import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { playersApi } from "../api/players";
import { AchievementList } from "../features/progress/AchievementList";
import { MasterCodeBoard } from "../features/progress/MasterCodeBoard";
import { useSession } from "../features/session/useSession";
import "./ProfilePage.css";

export function ProfilePage() {
  const { player, playerLoading } = useSession();
  const { data: masterCode } = useQuery({
    queryKey: ["master-code", player?.id],
    queryFn: () => playersApi.masterCode(player!.id),
    enabled: !!player,
  });
  const { data: achievements } = useQuery({
    queryKey: ["achievements", player?.id],
    queryFn: () => playersApi.achievements(player!.id),
    enabled: !!player,
  });

  if (playerLoading) return <div className="page"><div className="state-box">Загрузка...</div></div>;
  if (!player) {
    return (
      <div className="page">
        <div className="state-box card">
          <p>Профиль ребёнка не выбран. Его создаёт родитель в кабинете.</p>
          <Link className="btn" to="/parent">Кабинет родителя</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <section className="profile-hero">
        <span className="profile-hero__avatar">{player.name.charAt(0).toUpperCase()}</span>
        <div className="profile-hero__info">
          <h1 className="profile-hero__name">{player.name}</h1>
          <div className="profile-hero__stats">
            <span><b>{masterCode?.unlocked_count ?? 0}/{masterCode?.total_positions ?? 12}</b> букв кода</span>
            <span><b>{achievements?.length ?? 0}</b> достижений</span>
          </div>
        </div>
        {masterCode?.is_complete && (
          <Link to="/finale" className="btn btn--white">🎉 Гранд-финал</Link>
        )}
      </section>

      <h2 className="section-title">Мастер-код</h2>
      <MasterCodeBoard playerId={player.id} />

      <h2 className="section-title">Достижения</h2>
      <AchievementList playerId={player.id} />
    </div>
  );
}
