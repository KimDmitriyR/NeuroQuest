import { useState } from "react";
import { useStartQuest } from "../quest/useStartQuest";
import { Icon } from "./Icon";
import "./QuestCodeForm.css";

/** The "search bar" of the app: type the code printed on a quest card to start it. */
export function QuestCodeForm({ variant = "header" }: { variant?: "header" | "hero" }) {
  const [code, setCode] = useState("");
  const { start, starting, error, clearError } = useStartQuest();

  return (
    <form
      className={`code-form code-form--${variant}`}
      onSubmit={(e) => {
        e.preventDefault();
        start(code);
      }}
    >
      <input
        className="code-form__input"
        value={code}
        onChange={(e) => {
          setCode(e.target.value);
          if (error) clearError();
        }}
        placeholder={
          variant === "hero" ? "Код карточки, например finstartup-2-0-01" : "Введи код карточки"
        }
        aria-label="Код карточки квеста"
        autoComplete="off"
        autoCapitalize="off"
        spellCheck={false}
      />
      <button className="code-form__submit" type="submit" disabled={starting}>
        <Icon name="search" size={20} />
        <span className="code-form__submit-text">{starting ? "..." : "Начать"}</span>
      </button>
      {error && (
        <div className="code-form__error" role="alert">
          {error}
        </div>
      )}
    </form>
  );
}
