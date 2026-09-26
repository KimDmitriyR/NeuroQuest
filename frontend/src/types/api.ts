export interface Player {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export type ChoiceOutcome = "positive" | "neutral" | "negative";
export type QuestNodeType = "choice" | "completion";
export type QuestSessionStatus = "in_progress" | "completed";

export interface ChoiceOption {
  id: string;
  label: string;
  text: string;
}

export interface NodeView {
  id: string;
  type: QuestNodeType;
  message: string;
  choices: ChoiceOption[];
}

export interface SessionView {
  id: string;
  player_id: string;
  quest_id: string;
  status: QuestSessionStatus;
  started_at: string;
  completed_at: string | null;
  current_node: NodeView;
}

export interface AchievementView {
  title: string;
  description: string | null;
}

export interface MasterCodeLetterView {
  letter: string;
  position: number;
}

export interface ChoiceResultView {
  status_label: string | null;
  outcome: ChoiceOutcome;
  consequence_text: string;
  lesson_text: string | null;
  unlock_title: string | null;
  unlock_description: string | null;
  achievement_granted: AchievementView | null;
  completed: boolean;
  completion_achievement: AchievementView | null;
  master_code_letter: MasterCodeLetterView | null;
  next_node: NodeView | null;
}

export type MissionValidationType = "photo" | "text";
export type MissionAttemptStatus =
  | "in_progress"
  | "submitted"
  | "approved"
  | "rejected";

export interface MissionView {
  id: string;
  sector_id: string;
  title: string;
  description: string;
  instructions: string;
  validation_type: MissionValidationType;
}

export interface AttemptView {
  id: string;
  player_id: string;
  mission_id: string;
  status: MissionAttemptStatus;
  photo_url: string | null;
  text_answer: string | null;
  current_step: number;
  started_at: string;
  submitted_at: string | null;
  completed_at: string | null;
}

export interface SubmitAttemptResultView extends AttemptView {
  is_correct: boolean | null;
  total_steps: number | null;
}

export interface EarnedAchievementView {
  title: string;
  description: string | null;
  is_badge: boolean;
  earned_at: string;
}

export interface MasterCodeSlotView {
  position: number;
  letter: string | null;
  unlocked: boolean;
}

export interface MasterCodeProgressView {
  slots: MasterCodeSlotView[];
  total_positions: number;
  unlocked_count: number;
  is_complete: boolean;
}
