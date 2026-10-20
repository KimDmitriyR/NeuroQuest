import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { playersApi } from "../../api/players";
import { useSession } from "../session/useSession";
import { copyText } from "./copyText";
import type { Player } from "../../types/api";
import "./ChildCard.css";

export function ChildCard({ child }: { child: Player }) {
  const { player: activePlayer, activatePlayerToken } = useSession();
  const [copied, setCopied] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { data: achievements } = useQuery({
    queryKey: ["achievements", child.id],
    queryFn: () => playersApi.achievements(child.id),
  });
  const { data: masterCode } = useQuery({
    queryKey: ["master-code", child.id],
    queryFn: () => playersApi.masterCode(child.id),
  });

  // every action below needs a fresh child token from the server (parent-only)
  const withToken = async (
    getToken: () => Promise<{ access_token: string }>,
    action: (token: string) => Promise<void>,
  ) => {
    setBusy(true);
    setError(null);
    try {
      await action((await getToken()).access_token);
    } catch {
      setError("Не получилось. Проверь соединение и попробуй ещё раз.");
    } finally {
      setBusy(false);
    }
  };

  const playHere = () =>
    withToken(
      () => playersApi.issueToken(child.id),
      async (token) => {
        activatePlayerToken(token);
        window.location.href = "/";
      },
    );

  const copyLink = () =>
    withToken(
      () => playersApi.issueToken(child.id),
      async (token) => {
        const url = `${window.location.origin}/?t=${encodeURIComponent(token)}`;
        if (await copyText(url)) {
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        } else {
          // the browser blocked every way of copying: let the parent copy it by hand
          window.prompt("Скопируй ссылку и отправь её ребёнку:", url);
        }
      },
    );

  const resetLink = () => {
    const sure = window.confirm(
      `Сбросить доступ для ${child.name}? Все ранее отправленные ссылки и ` +
        "устройства ребёнка перестанут работать. Прогресс сохранится.",
    );
    if (!sure) return;
    return withToken(
      () => playersApi.resetToken(child.id),
      async (token) => {
        // keep THIS device signed in if it is the one playing as this child
        if (activePlayer?.id === child.id) activatePlayerToken(token);
        window.alert("Готово. Старые ссылки больше не работают — скопируй новую ссылку для ребёнка.");
      },
    );
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
        <button className="btn btn--sm" onClick={playHere} disabled={busy}>Играть на этом устройстве</button>
        <button className="btn btn--sm btn--ghost" onClick={copyLink} disabled={busy}>
          {copied ? "Скопировано!" : "Ссылка для ребёнка"}
        </button>
      </div>
      <button className="child-card__reset" onClick={resetLink} disabled={busy}>
        Сбросить доступ (если ссылка попала не туда)
      </button>
      {error && <p className="child-card__error" role="alert">{error}</p>}
    </div>
  );
}
