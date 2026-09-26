import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { usePlayer } from "../features/player/usePlayer";
import { playersApi } from "../api/players";
import "./FinalePage.css";

type Phase = "assembling" | "hacking" | "unlocked" | "certificate";

const HACK_CHARS = "01ТВОЙНОВЫЙКОДAI#$%&";

function randomLine(): string {
  let line = "";
  for (let i = 0; i < 40; i++) {
    line += HACK_CHARS[Math.floor(Math.random() * HACK_CHARS.length)];
  }
  return line;
}

function useHackText(active: boolean) {
  const [lines, setLines] = useState<string[]>([]);
  useEffect(() => {
    if (!active) return;
    const interval = setInterval(() => {
      setLines((prev) => [...prev, randomLine()].slice(-14));
    }, 70);
    return () => clearInterval(interval);
  }, [active]);
  return lines;
}

export function FinalePage() {
  const { player, loading } = usePlayer();
  const navigate = useNavigate();
  const [phase, setPhase] = useState<Phase>("assembling");
  const hackLines = useHackText(phase === "hacking");

  const { data: masterCode } = useQuery({
    queryKey: ["master-code", player?.id],
    queryFn: () => playersApi.masterCode(player!.id),
    enabled: !!player,
  });

  const [offsets] = useState(() =>
    Array.from({ length: 12 }, () => ({
      x: (Math.random() - 0.5) * 600,
      y: (Math.random() - 0.5) * 400,
      rotate: (Math.random() - 0.5) * 180,
    })),
  );

  useEffect(() => {
    if (!masterCode?.is_complete) return;
    const t1 = setTimeout(() => setPhase("hacking"), 1800);
    const t2 = setTimeout(() => setPhase("unlocked"), 3600);
    const t3 = setTimeout(() => setPhase("certificate"), 5600);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [masterCode?.is_complete]);

  if (loading) return <div className="finale-page__status">Загрузка...</div>;
  if (!player) {
    return (
      <div className="finale-page__status">
        Сначала создай игрока.
        <button onClick={() => navigate("/")}>На главную</button>
      </div>
    );
  }
  if (!masterCode) return <div className="finale-page__status">Загрузка...</div>;
  if (!masterCode.is_complete) {
    return (
      <div className="finale-page__status">
        Мастер-код ещё не собран ({masterCode.unlocked_count}/
        {masterCode.total_positions}). Пройди больше карточек!
        <button onClick={() => navigate("/profile")}>В профиль</button>
      </div>
    );
  }

  const phrase = masterCode.slots.map((s) => s.letter).join("");

  return (
    <div className="finale-page">
      {phase === "assembling" && (
        <div className="finale-page__assembly">
          {masterCode.slots.map((slot, i) => {
            const offset = offsets[i % offsets.length];
            return (
              <span
                key={slot.position}
                className="finale-page__flying-letter"
                style={
                  {
                    "--x": `${offset.x}px`,
                    "--y": `${offset.y}px`,
                    "--rotate": `${offset.rotate}deg`,
                    animationDelay: `${i * 60}ms`,
                  } as React.CSSProperties
                }
              >
                {slot.letter}
              </span>
            );
          })}
        </div>
      )}

      {phase === "hacking" && (
        <div className="finale-page__hack">
          {hackLines.map((line, i) => (
            <div key={i} className="finale-page__hack-line">
              {line}
            </div>
          ))}
        </div>
      )}

      {(phase === "unlocked" || phase === "certificate") && (
        <div className="finale-page__unlocked">
          <div className="finale-page__phrase">{phrase}</div>
          <div className="finale-page__stamp">
            СИСТЕМА РАЗБЛОКИРОВАНА
            <br />
            ДОСТУП ПОЛУЧЕН
          </div>
        </div>
      )}

      {phase === "certificate" && (
        <div className="finale-page__certificate-wrap">
          <div className="finale-page__certificate" id="certificate">
            <div className="finale-page__cert-title">СЕРТИФИКАТ</div>
            <div className="finale-page__cert-subtitle">
              Сертифицированный НейроХакер
            </div>
            <div className="finale-page__cert-name">{player.name}</div>
            <div className="finale-page__cert-date">
              {new Date().toLocaleDateString("ru-RU")}
            </div>
            <div className="finale-page__cert-code">Код: {phrase}</div>
          </div>
          <button className="finale-page__print" onClick={() => window.print()}>
            🖨️ Распечатать сертификат
          </button>
          <div className="finale-page__prize">
            🎁 Финальный приз скоро появится здесь!
          </div>
          <button className="finale-page__home" onClick={() => navigate("/profile")}>
            В профиль
          </button>
        </div>
      )}
    </div>
  );
}
