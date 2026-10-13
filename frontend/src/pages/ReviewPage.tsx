import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { missionsApi } from "../api/missions";
import { useSession } from "../features/session/useSession";
import "./ReviewPage.css";

export function ReviewPage() {
  const { parent, parentLoading } = useSession();
  const queryClient = useQueryClient();
  const { data: pending, isLoading } = useQuery({
    queryKey: ["pending-attempts"],
    queryFn: () => missionsApi.listPending(),
    refetchInterval: 10000,
    enabled: !!parent,
  });

  const review = async (attemptId: string, approved: boolean) => {
    await missionsApi.reviewAttempt(attemptId, approved);
    queryClient.invalidateQueries({ queryKey: ["pending-attempts"] });
  };

  if (parentLoading) return <div className="page"><div className="state-box">Загрузка...</div></div>;
  if (!parent) {
    return (
      <div className="page">
        <div className="state-box card">
          <p>Проверка миссий доступна только родителю. Войди в кабинет.</p>
          <Link className="btn" to="/parent">Войти</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <h1 className="page-title">Проверка миссий</h1>
      <p className="page-subtitle">Фото, которые дети отправили на подтверждение</p>

      {isLoading && <div className="state-box">Загрузка...</div>}
      {!isLoading && pending?.length === 0 && (
        <div className="state-box card">Нечего проверять 🎉</div>
      )}

      <div className="review-grid">
        {pending?.map((attempt) => (
          <article key={attempt.id} className="review-card card">
            {attempt.photo_url && (
              <img className="review-card__photo" src={attempt.photo_url} alt="Фото на проверку" />
            )}
            <div className="review-card__body">
              <div className="review-card__who">{attempt.player_name}</div>
              <div className="review-card__mission">{attempt.mission_title}</div>
              <div className="review-card__actions">
                <button className="btn btn--sm review-card__approve" onClick={() => review(attempt.id, true)}>
                  ✅ Одобрить
                </button>
                <button className="btn btn--sm btn--danger" onClick={() => review(attempt.id, false)}>
                  ❌ Отклонить
                </button>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
