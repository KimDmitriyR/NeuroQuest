import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Icon } from "../features/layout/Icon";
import { QuestChat } from "../features/quest/QuestChat";
import "./QuestPage.css";

export function QuestPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [completed, setCompleted] = useState(false);

  if (!sessionId) return null;

  return (
    <div className="quest-page">
      <div className="quest-page__bar">
        <Link to="/" className="back-link">
          <Icon name="back" size={18} /> Домой
        </Link>
        {completed && (
          <Link to="/profile" className="btn btn--sm">
            К достижениям
          </Link>
        )}
      </div>
      <QuestChat sessionId={sessionId} onCompleted={() => setCompleted(true)} />
    </div>
  );
}
