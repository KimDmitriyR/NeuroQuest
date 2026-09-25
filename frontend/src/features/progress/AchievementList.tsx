import { useQuery } from "@tanstack/react-query";
import { playersApi } from "../../api/players";
import "./AchievementList.css";

export function AchievementList({ playerId }: { playerId: string }) {
  const { data } = useQuery({
    queryKey: ["achievements", playerId],
    queryFn: () => playersApi.achievements(playerId),
  });

  if (!data) return null;
  if (data.length === 0) {
    return <div className="achievement-list__empty">Пока нет достижений</div>;
  }

  return (
    <ul className="achievement-list">
      {data.map((a) => (
        <li key={a.title} className="achievement-list__item">
          <span className="achievement-list__icon">{a.is_badge ? "🏆" : "⭐"}</span>
          {a.title}
        </li>
      ))}
    </ul>
  );
}
