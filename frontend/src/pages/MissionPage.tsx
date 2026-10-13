import { Link, useParams } from "react-router-dom";
import { Icon } from "../features/layout/Icon";
import { MissionFlow } from "../features/mission/MissionFlow";
import { useSession } from "../features/session/useSession";
import "./MissionPage.css";

export function MissionPage() {
  const { missionId } = useParams<{ missionId: string }>();
  const { player, playerLoading } = useSession();

  if (!missionId) return null;

  return (
    <div className="page page--narrow">
      <Link to="/missions" className="back-link">
        <Icon name="back" size={18} /> Все миссии
      </Link>

      {playerLoading && <div className="state-box">Загрузка...</div>}

      {!playerLoading && !player && (
        <div className="state-box card">
          <p>Чтобы выполнять миссии, нужен профиль ребёнка. Его создаёт родитель в кабинете.</p>
          <Link className="btn" to="/parent">Кабинет родителя</Link>
        </div>
      )}

      {player && <MissionFlow missionId={missionId} playerId={player.id} />}
    </div>
  );
}
