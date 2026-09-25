import type { ReactNode } from "react";
import "./ChatMessage.css";

interface ChatMessageProps {
  from: "bot" | "player";
  children: ReactNode;
  tone?: "neutral" | "positive" | "negative";
}

export function ChatMessage({ from, children, tone = "neutral" }: ChatMessageProps) {
  return (
    <div className={`chat-message chat-message--${from} chat-message--${tone}`}>
      <div className="chat-message__bubble">{children}</div>
    </div>
  );
}
