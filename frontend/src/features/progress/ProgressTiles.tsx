import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { playersApi } from "../../api/players";
import "./ProgressTiles.css";

/** Home-page summary: master code progress and achievements count. */
export function ProgressTiles({ playerId }: { playerId: string }) {
  const { data: masterCode } = useQuery({
    queryKey: ["master-code", playerId],
    queryFn: () => playersApi.masterCode(playerId),
  });
  const { data: achievements } = useQuery({
    queryKey: ["achievements", playerId],
    queryFn: () => playersApi.achievements(playerId),
  });

  const unlocked = masterCode?.unlocked_count ?? 0;
  const total = masterCode?.total_positions ?? 12;
  const percent = total ? Math.round((unlocked / total) * 100) : 0;

  return (
    <div className="progress-tiles">
      <Link to="/profile" className="progress-tile card">
        <div className="progress-tile__title">Мастер-код</div>
        <div className="progress-tile__value">
          {unlocked}<span> / {total}</span>
        </div>
        <div className="progress-tile__bar" aria-hidden="true">
          <div className="progress-tile__fill" style={{ width: `${percent}%` }} />
        </div>
        <div className="progress-tile__hint">
          {masterCode?.is_complete ? "Код собран! Открой гранд-финал" : "Проходи карточки и собирай буквы"}
        </div>
      </Link>

      <Link to="/profile" className="progress-tile card">
        <div className="progress-tile__title">Достижения</div>
        <div className="progress-tile__value">{achievements?.length ?? 0}</div>
        <div className="progress-tile__hint">Награды за правильные решения</div>
      </Link>
    </div>
  );
}
