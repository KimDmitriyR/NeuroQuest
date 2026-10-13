import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { playersApi } from "../../api/players";
import { PLAYER_STORAGE_KEY } from "../player/usePlayer";
import type { Player } from "../../types/api";
import "./ChildCard.css";

export function ChildCard({ child }: { child: Player }) {
  const [copied, setCopied] = useState(false);
  const { data: achievements } = useQuery({
    queryKey: ["achievements", child.id],
    queryFn: () => playersApi.achievements(child.id),
  });
  const { data: masterCode } = useQuery({
    queryKey: ["master-code", child.id],
    queryFn: () => playersApi.masterCode(child.id),
  });

  const playHere = () => {
    localStorage.setItem(PLAYER_STORAGE_KEY, child.id);
    window.location.href = "/";
  };

  const copyLink = async () => {
    const url = `${window.location.origin}/?child=${child.id}`;
    await navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="child-card card">
      <div className="child-card__top">
        <span className="child-card__avatar">{child.name.charAt(0).toUpperCase()}</span>
        <div>
          <div className="child-card__name">{child.name}</div>
          <div className="child-card__stats">
            <span>🔤 {masterCode ? `${masterCode.unlocked_count}/${masterCode.total_positions}` : "…"}</span>
            <span>🏆 {achievements ? achievements.length : "…"}</span>
          </div>
        </div>
      </div>
      <div className="child-card__actions">
        <button className="btn btn--sm" onClick={playHere}>Играть на этом устройстве</button>
        <button className="btn btn--sm btn--ghost" onClick={copyLink}>
          {copied ? "Скопировано!" : "Ссылка для ребёнка"}
        </button>
      </div>
    </div>
  );
}
