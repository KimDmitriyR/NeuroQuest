import { useQuery } from "@tanstack/react-query";
import { playersApi } from "../../api/players";
import "./MasterCodeBoard.css";

export function MasterCodeBoard({ playerId }: { playerId: string }) {
  const { data } = useQuery({
    queryKey: ["master-code", playerId],
    queryFn: () => playersApi.masterCode(playerId),
  });

  if (!data) return null;

  return (
    <div className="master-code-board card">
      <div className="master-code-board__slots">
        {data.slots.map((slot) => (
          <div
            key={slot.position}
            className={`master-code-board__slot${slot.unlocked ? " master-code-board__slot--unlocked" : ""}`}
          >
            {slot.letter ?? "?"}
          </div>
        ))}
      </div>
      <div className="master-code-board__caption">
        {data.is_complete
          ? "🎉 Мастер-код собран!"
          : `Собрано ${data.unlocked_count} из ${data.total_positions} букв — проходи карточки, чтобы открыть остальные`}
      </div>
    </div>
  );
}
