import "./RewardToast.css";

interface RewardToastProps {
  icon: string;
  title: string;
  subtitle: string;
}

export function RewardToast({ icon, title, subtitle }: RewardToastProps) {
  return (
    <div className="reward-toast">
      <span className="reward-toast__icon">{icon}</span>
      <div>
        <div className="reward-toast__title">{title}</div>
        <div className="reward-toast__subtitle">{subtitle}</div>
      </div>
    </div>
  );
}
