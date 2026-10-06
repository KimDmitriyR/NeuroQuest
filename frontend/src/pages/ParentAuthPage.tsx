import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/useAuth";
import { ApiError } from "../api/client";
import "./ParentAuthPage.css";

export function ParentAuthPage() {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (mode === "register" && !acceptTerms) {
      setError(
        "Нужно подтвердить согласие с условиями и политикой обработки персональных данных",
      );
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      if (mode === "login") {
        await login(email.trim(), password);
      } else {
        await register(email.trim(), password, acceptTerms);
      }
      navigate("/parent");
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) setError("Неверный email или пароль");
        else if (err.status === 409) setError("Этот email уже зарегистрирован");
        else if (err.status === 422) setError("Проверь email и пароль (минимум 8 символов)");
        else setError(err.message);
      } else {
        setError("Что-то пошло не так");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="parent-auth">
      <h1>Кабинет родителя</h1>
      <div className="parent-auth__tabs">
        <button
          className={mode === "login" ? "parent-auth__tab parent-auth__tab--active" : "parent-auth__tab"}
          onClick={() => setMode("login")}
        >
          Войти
        </button>
        <button
          className={mode === "register" ? "parent-auth__tab parent-auth__tab--active" : "parent-auth__tab"}
          onClick={() => setMode("register")}
        >
          Регистрация
        </button>
      </div>

      <form onSubmit={handleSubmit} className="parent-auth__form">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
          autoFocus
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Пароль (минимум 8 символов)"
          required
          minLength={8}
        />
        {mode === "register" && (
          <label className="parent-auth__consent">
            <input
              type="checkbox"
              checked={acceptTerms}
              onChange={(e) => setAcceptTerms(e.target.checked)}
            />
            <span>
              Я согласен(на) с{" "}
              <a href="/terms" target="_blank" rel="noreferrer">
                Пользовательским соглашением
              </a>{" "}
              и{" "}
              <a href="/privacy" target="_blank" rel="noreferrer">
                Политикой обработки персональных данных
              </a>
              , в том числе данных моего ребёнка
            </span>
          </label>
        )}

        <button type="submit" disabled={submitting || (mode === "register" && !acceptTerms)}>
          {submitting ? "..." : mode === "login" ? "Войти" : "Создать аккаунт"}
        </button>
      </form>

      {error && <div className="parent-auth__error">{error}</div>}

      <button className="parent-auth__back" onClick={() => navigate("/")}>
        ← На главную
      </button>
    </div>
  );
}
