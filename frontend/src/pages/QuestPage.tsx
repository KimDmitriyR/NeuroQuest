import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { QuestChat } from "../features/quest/QuestChat";
import "./QuestPage.css";

export function QuestPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [completed, setCompleted] = useState(false);

  if (!sessionId) return null;

  return (
    <div className="quest-page">
      <header className="quest-page__header">
        <button className="quest-page__back" onClick={() => navigate("/")}>
          ← Домой
        </button>
        {completed && (
          <button className="quest-page__profile" onClick={() => navigate("/profile")}>
            Профиль →
          </button>
        )}
      </header>
      <QuestChat sessionId={sessionId} onCompleted={() => setCompleted(true)} />
    </div>
  );
}
