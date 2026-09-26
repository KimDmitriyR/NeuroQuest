import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { missionsApi } from "../api/missions";
import "./ReviewPage.css";

export function ReviewPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: pending, isLoading } = useQuery({
    queryKey: ["pending-attempts"],
    queryFn: () => missionsApi.listPending(),
    refetchInterval: 10000,
  });

  const review = async (attemptId: string, approved: boolean) => {
    await missionsApi.reviewAttempt(attemptId, approved);
    queryClient.invalidateQueries({ queryKey: ["pending-attempts"] });
  };

  return (
    <div className="review-page">
      <header className="review-page__header">
        <button className="review-page__back" onClick={() => navigate("/")}>
          ← Домой
        </button>
        <h1>Проверка миссий</h1>
      </header>

      {isLoading && <div className="review-page__status">Загрузка...</div>}
      {!isLoading && pending?.length === 0 && (
        <div className="review-page__status">Нечего проверять 🎉</div>
      )}

      <ul className="review-page__list">
        {pending?.map((attempt) => (
          <li key={attempt.id} className="review-page__item">
            <div className="review-page__meta">
              <strong>{attempt.player_name}</strong> — {attempt.mission_title}
            </div>
            {attempt.photo_url && (
              <img
                className="review-page__photo"
                src={attempt.photo_url}
                alt="Фото на проверку"
              />
            )}
            <div className="review-page__actions">
              <button
                className="review-page__approve"
                onClick={() => review(attempt.id, true)}
              >
                ✅ Одобрить
              </button>
              <button
                className="review-page__reject"
                onClick={() => review(attempt.id, false)}
              >
                ❌ Отклонить
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
