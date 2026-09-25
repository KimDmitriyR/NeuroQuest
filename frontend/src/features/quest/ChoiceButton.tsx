import "./ChoiceButton.css";

interface ChoiceButtonProps {
  label: string;
  text: string;
  disabled?: boolean;
  onClick: () => void;
}

export function ChoiceButton({ label, text, disabled, onClick }: ChoiceButtonProps) {
  return (
    <button className="choice-button" disabled={disabled} onClick={onClick}>
      <span className="choice-button__label">{label}</span>
      <span className="choice-button__text">{text}</span>
    </button>
  );
}
