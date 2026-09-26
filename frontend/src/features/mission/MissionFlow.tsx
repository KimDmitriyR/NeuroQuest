import { useState } from "react";
import { RewardToast } from "../quest/RewardToast";
import { PhotoCapture } from "./PhotoCapture";
import { useMission, useStartAttempt, useSubmitAttempt } from "./useMission";
import type { AttemptView, SubmitAttemptResultView } from "../../types/api";
import "./MissionFlow.css";

interface MissionFlowProps {
  missionId: string;
  playerId: string;
}

export function MissionFlow({ missionId, playerId }: MissionFlowProps) {
  const { data: mission, isLoading } = useMission(missionId);
  const startAttempt = useStartAttempt(missionId, playerId);
  const [attempt, setAttempt] = useState<AttemptView | SubmitAttemptResultView | null>(
    null,
  );
  const [totalSteps, setTotalSteps] = useState<number | null>(null);
  const [textInput, setTextInput] = useState("");
  const [feedback, setFeedback] = useState<"correct" | "wrong" | null>(null);
  const submitAttempt = useSubmitAttempt(attempt?.id);

  if (isLoading) return <div className="mission-flow__status">Загрузка...</div>;
  if (!mission) return <div className="mission-flow__status">Миссия не найдена.</div>;

  const handleStart = () => {
    startAttempt.mutate(undefined, { onSuccess: setAttempt });
  };

  const handleSubmitText = () => {
    if (!textInput.trim()) return;
    submitAttempt.mutate(
      { textAnswer: textInput.trim() },
      {
        onSuccess: (result) => {
          setAttempt(result);
          setFeedback(result.is_correct ? "correct" : "wrong");
          if (result.total_steps) setTotalSteps(result.total_steps);
          if (result.is_correct) setTextInput("");
        },
      },
    );
  };

  const handleSubmitPhoto = (dataUrl: string) => {
    submitAttempt.mutate({ photoUrl: dataUrl }, { onSuccess: setAttempt });
  };

  return (
    <div className="mission-flow">
      <h1>{mission.title}</h1>
      <p className="mission-flow__description">{mission.description}</p>

      {!attempt && (
        <>
          <div className="mission-flow__instructions">{mission.instructions}</div>
          <button
            className="mission-flow__start"
            onClick={handleStart}
            disabled={startAttempt.isPending}
          >
            {startAttempt.isPending ? "..." : "Начать миссию"}
          </button>
        </>
      )}

      {attempt && attempt.status === "in_progress" && mission.validation_type === "photo" && (
        <>
          <div className="mission-flow__instructions">{mission.instructions}</div>
          <PhotoCapture onCapture={handleSubmitPhoto} />
        </>
      )}

      {attempt && attempt.status === "in_progress" && mission.validation_type === "text" && (
        <div className="mission-flow__cipher">
          <div className="mission-flow__step-label">
            Шаг {attempt.current_step + 1}
            {totalSteps ? ` из ${totalSteps}` : ""}
          </div>
          <div className="mission-flow__instructions">{mission.instructions}</div>
          <input
            className="mission-flow__cipher-input"
            value={textInput}
            onChange={(e) => {
              setTextInput(e.target.value);
              setFeedback(null);
            }}
            placeholder="Введи расшифрованную фразу"
            onKeyDown={(e) => e.key === "Enter" && handleSubmitText()}
          />
          <button
            className="mission-flow__start"
            onClick={handleSubmitText}
            disabled={submitAttempt.isPending || !textInput.trim()}
          >
            Проверить
          </button>
          {feedback === "wrong" && (
            <div className="mission-flow__feedback mission-flow__feedback--wrong">
              Неверно, попробуй ещё раз
            </div>
          )}
        </div>
      )}

      {attempt && attempt.status === "submitted" && (
        <div className="mission-flow__pending">
          📨 Отправлено на проверку. Как только куратор посмотрит фото, миссия
          будет засчитана.
        </div>
      )}

      {attempt && attempt.status === "approved" && (
        <RewardToast icon="🏆" title="Миссия выполнена!" subtitle="Достижение получено" />
      )}

      {attempt && attempt.status === "rejected" && (
        <div className="mission-flow__feedback mission-flow__feedback--wrong">
          Миссия не засчитана. Попробуй ещё раз позже.
        </div>
      )}
    </div>
  );
}
