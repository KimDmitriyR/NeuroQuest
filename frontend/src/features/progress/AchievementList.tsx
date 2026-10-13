import { useQuery } from "@tanstack/react-query";
import { playersApi } from "../../api/players";
import "./AchievementList.css";

const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString("ru-RU", { day: "numeric", month: "short" });

export function AchievementList({ playerId }: { playerId: string }) {
  const { data } = useQuery({
    queryKey: ["achievements", playerId],
    queryFn: () => playersApi.achievements(playerId),
  });

  if (!data) return null;
  if (data.length === 0) {
    return <div className="state-box card">Пока нет достижений — пройди первую карточку 🚀</div>;
  }

  return (
    <ul className="achievement-grid">
      {data.map((a) => (
        <li key={a.title} className={`achievement-card card${a.is_badge ? " achievement-card--badge" : ""}`}>
          <span className="achievement-card__icon">{a.is_badge ? "🏆" : "⭐"}</span>
          <span className="achievement-card__title">{a.title}</span>
          <span className="achievement-card__date">{formatDate(a.earned_at)}</span>
        </li>
      ))}
    </ul>
  );
}
