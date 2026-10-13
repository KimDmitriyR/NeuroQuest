import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../features/auth/useAuth";
import { useAddChild, useChildren } from "../features/parent/useChildren";
import { ChildCard } from "../features/parent/ChildCard";
import { Icon } from "../features/layout/Icon";
import "./ParentDashboardPage.css";

export function ParentDashboardPage() {
  const { parent, loading } = useAuth();
  const { data: children, isLoading } = useChildren();
  const addChild = useAddChild();
  const [newName, setNewName] = useState("");

  if (loading) return <div className="page"><div className="state-box">Загрузка...</div></div>;
  if (!parent) {
    return (
      <div className="page">
        <div className="state-box card">
          <p>Сначала войди в кабинет.</p>
          <Link className="btn" to="/parent">Войти</Link>
        </div>
      </div>
    );
  }

  const handleAddChild = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    addChild.mutate(newName.trim(), { onSuccess: () => setNewName("") });
  };

  return (
    <div className="page">
      <div className="dash-head">
        <div>
          <h1 className="page-title">Кабинет родителя</h1>
          <p className="page-subtitle">{parent.email}</p>
        </div>
        <Link to="/review" className="btn btn--ghost">
          <Icon name="mail" size={20} /> Проверка миссий
        </Link>
      </div>

      <h2 className="section-title section-title--first">Мои дети</h2>
      <div className="dash-grid">
        {isLoading && <div className="state-box">Загрузка...</div>}
        {children?.map((child) => (
          <ChildCard key={child.id} child={child} />
        ))}

        <form onSubmit={handleAddChild} className="add-child card">
          <div className="add-child__title">Добавить ребёнка</div>
          <input
            className="input"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Имя ребёнка"
          />
          <button className="btn btn--block" type="submit" disabled={addChild.isPending || !newName.trim()}>
            + Добавить
          </button>
        </form>
      </div>
    </div>
  );
}
