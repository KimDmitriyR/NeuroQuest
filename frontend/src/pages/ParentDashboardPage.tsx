import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/useAuth";
import { useAddChild, useChildren } from "../features/parent/useChildren";
import { ChildCard } from "../features/parent/ChildCard";
import "./ParentDashboardPage.css";

export function ParentDashboardPage() {
  const { parent, loading } = useAuth();
  const navigate = useNavigate();
  const { data: children, isLoading } = useChildren();
  const addChild = useAddChild();
  const [newName, setNewName] = useState("");

  if (loading) return <div className="parent-dashboard__status">Загрузка...</div>;
  if (!parent) {
    return (
      <div className="parent-dashboard__status">
        Сначала войди в кабинет.
        <button onClick={() => navigate("/parent")}>Войти</button>
      </div>
    );
  }

  const handleAddChild = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    addChild.mutate(newName.trim(), { onSuccess: () => setNewName("") });
  };

  return (
    <div className="parent-dashboard">
      <header className="parent-dashboard__header">
        <div>
          <h1>Кабинет родителя</h1>
          <div className="parent-dashboard__email">{parent.email}</div>
        </div>
        <button className="parent-dashboard__review-link" onClick={() => navigate("/review")}>
          📨 Проверка миссий
        </button>
      </header>

      <div className="parent-dashboard__children">
        {isLoading && <div className="parent-dashboard__status">Загрузка...</div>}
        {children?.map((child) => (
          <ChildCard key={child.id} child={child} />
        ))}
      </div>

      <form onSubmit={handleAddChild} className="parent-dashboard__add-form">
        <input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="Имя ребёнка"
        />
        <button type="submit" disabled={addChild.isPending}>
          + Добавить ребёнка
        </button>
      </form>
    </div>
  );
}
