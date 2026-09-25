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
    <div className="master-code-board">
      <div className="master-code-board__title">
        Мастер-код: {data.unlocked_count}/{data.total_positions}
      </div>
      <div className="master-code-board__slots">
        {data.slots.map((slot) => (
          <div
            key={slot.position}
            className={`master-code-board__slot ${slot.unlocked ? "master-code-board__slot--unlocked" : ""}`}
          >
            {slot.letter ?? "?"}
          </div>
        ))}
      </div>
      {data.is_complete && (
        <div className="master-code-board__complete">🎉 Мастер-код собран!</div>
      )}
    </div>
  );
}
