import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Icon } from "../features/layout/Icon";
import { useMissions } from "../features/mission/useMission";
import type { MissionView } from "../types/api";
import "./MissionsPage.css";

const VALIDATION_INFO = {
  photo: { label: "Фото-задание", meta: "Фото проверяет куратор", icon: "camera" as const },
  text: { label: "Шифр", meta: "Ответ проверяется сразу", icon: "lock" as const },
};

function MissionCard({ mission }: { mission: MissionView }) {
  const info = VALIDATION_INFO[mission.validation_type];
  return (
    <Link
      to={`/mission/${mission.id}`}
      className="product-card"
      style={{ "--accent": mission.sector_color } as React.CSSProperties}
    >
      <div className="product-card__media">
        <span className="product-card__badge">{info.label}</span>
        <span className="product-card__art" aria-hidden="true">
          <Icon name={info.icon} size={64} />
        </span>
      </div>

      <div className="product-card__body">
        <div className="product-card__reward">
          <span aria-hidden="true">🏆</span>
          <span className="product-card__reward-text">{mission.reward_title}</span>
        </div>
        <div className="product-card__name">
          <b>{mission.sector_title}</b> / {mission.title}
        </div>
        <p className="product-card__desc">{mission.description}</p>
        <div className="product-card__meta">
          <Icon name={info.icon} size={15} /> {info.meta}
        </div>
        <span className="product-card__cta">Начать миссию</span>
      </div>
    </Link>
  );
}

export function MissionsPage() {
  const { data: missions, isLoading, isError } = useMissions();
  const [sector, setSector] = useState<string | null>(null);

  const sectors = useMemo(
    () => [...new Set((missions ?? []).map((m) => m.sector_title))],
    [missions],
  );
  const visible = (missions ?? []).filter((m) => !sector || m.sector_title === sector);

  return (
    <div className="page">
      <h1 className="page-title">Конверты с миссиями</h1>
      <p className="page-subtitle">
        Задания из реального мира: выполни, подтверди и получи награду
      </p>

      {sectors.length > 1 && (
        <div className="chips" role="tablist" aria-label="Фильтр по разделам">
          <button
            className={`chip${sector === null ? " chip--active" : ""}`}
            onClick={() => setSector(null)}
          >
            Все
          </button>
          {sectors.map((s) => (
            <button
              key={s}
              className={`chip${sector === s ? " chip--active" : ""}`}
              onClick={() => setSector(s)}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {isLoading && <div className="state-box">Загрузка...</div>}
      {isError && <div className="state-box">Не удалось загрузить миссии. Проверь, что сервер запущен.</div>}

      <div className="product-grid">
        {visible.map((m) => (
          <MissionCard key={m.id} mission={m} />
        ))}
      </div>
    </div>
  );
}
