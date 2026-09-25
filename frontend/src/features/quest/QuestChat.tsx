import { useEffect, useRef, useState } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChoiceButton } from "./ChoiceButton";
import { RewardToast } from "./RewardToast";
import { useQuestSession, useSubmitChoice } from "./useQuest";
import type { ChoiceResultView } from "../../types/api";
import "./QuestChat.css";

interface LogEntry {
  id: string;
  kind: "bot" | "player" | "reward";
  text?: string;
  tone?: "neutral" | "positive" | "negative";
  reward?: { icon: string; title: string; subtitle: string };
}

interface QuestChatProps {
  sessionId: string;
  onCompleted?: () => void;
}

let entryCounter = 0;
const nextId = () => `entry-${entryCounter++}`;

export function QuestChat({ sessionId, onCompleted }: QuestChatProps) {
  const { data: session, isLoading, error } = useQuestSession(sessionId);
  const submitChoice = useSubmitChoice(sessionId);
  const [log, setLog] = useState<LogEntry[]>([]);
  const seenNodeIds = useRef<Set<string>>(new Set());
  const bottomRef = useRef<HTMLDivElement>(null);

  // append the bot's message whenever a new node appears (first load, or
  // after a completed request updates current_node)
  useEffect(() => {
    const node = session?.current_node;
    if (!node || seenNodeIds.current.has(node.id)) return;
    seenNodeIds.current.add(node.id);
    setLog((prev) => [
      ...prev,
      { id: nextId(), kind: "bot", text: node.message, tone: "neutral" },
    ]);
  }, [session?.current_node]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [log]);

  if (isLoading) return <div className="quest-chat__status">Загрузка...</div>;
  if (error || !session)
    return <div className="quest-chat__status">Не удалось загрузить квест.</div>;

  const handleChoice = (choiceId: string, choiceText: string) => {
    setLog((prev) => [...prev, { id: nextId(), kind: "player", text: choiceText }]);

    submitChoice.mutate(choiceId, {
      onSuccess: (result: ChoiceResultView) => {
        const entries: LogEntry[] = [
          {
            id: nextId(),
            kind: "bot",
            text: result.consequence_text,
            tone: result.outcome,
          },
        ];
        if (result.lesson_text) {
          entries.push({
            id: nextId(),
            kind: "bot",
            text: `💡 ${result.lesson_text}`,
            tone: "neutral",
          });
        }
        if (result.achievement_granted) {
          entries.push({
            id: nextId(),
            kind: "reward",
            reward: {
              icon: "🏆",
              title: result.achievement_granted.title,
              subtitle: "Достижение получено",
            },
          });
        }
        if (result.completed) {
          if (result.completion_achievement) {
            entries.push({
              id: nextId(),
              kind: "reward",
              reward: {
                icon: "🏆",
                title: result.completion_achievement.title,
                subtitle: "Финальный бейдж карточки",
              },
            });
          }
          if (result.master_code_letter) {
            entries.push({
              id: nextId(),
              kind: "reward",
              reward: {
                icon: "🔤",
                title: `Буква «${result.master_code_letter.letter}»`,
                subtitle: `Позиция ${result.master_code_letter.position} в мастер-коде`,
              },
            });
          }
          if (result.unlock_title) {
            entries.push({
              id: nextId(),
              kind: "reward",
              reward: { icon: "🎁", title: result.unlock_title, subtitle: "Разблокировано" },
            });
          }
          entries.push({
            id: nextId(),
            kind: "bot",
            text: "🎉 Карточка пройдена!",
            tone: "positive",
          });
          onCompleted?.();
        }
        setLog((prev) => [...prev, ...entries]);
      },
    });
  };

  const currentNode = session.current_node;
  const showChoices =
    !submitChoice.isPending && currentNode.type === "choice" && !session.completed_at;

  return (
    <div className="quest-chat">
      <div className="quest-chat__log">
        {log.map((entry) => {
          if (entry.kind === "reward" && entry.reward) {
            return <RewardToast key={entry.id} {...entry.reward} />;
          }
          return (
            <ChatMessage
              key={entry.id}
              from={entry.kind === "player" ? "player" : "bot"}
              tone={entry.tone}
            >
              {entry.text}
            </ChatMessage>
          );
        })}
        <div ref={bottomRef} />
      </div>

      {showChoices && (
        <div className="quest-chat__choices">
          {currentNode.choices.map((choice) => (
            <ChoiceButton
              key={choice.id}
              label={choice.label}
              text={choice.text}
              disabled={submitChoice.isPending}
              onClick={() => handleChoice(choice.id, `${choice.label}. ${choice.text}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
