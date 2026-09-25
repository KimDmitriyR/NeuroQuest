import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { questsApi } from "../../api/quests";
import type { ChoiceResultView } from "../../types/api";

export function useQuestSession(sessionId: string) {
  return useQuery({
    queryKey: ["quest-session", sessionId],
    queryFn: () => questsApi.getSession(sessionId),
  });
}

export function useSubmitChoice(sessionId: string) {
  const queryClient = useQueryClient();

  return useMutation<ChoiceResultView, Error, string>({
    mutationFn: (choiceId: string) => questsApi.submitChoice(sessionId, choiceId),
    onSuccess: (result) => {
      // the session's current_node changed server-side; refresh it so the
      // next choice's options are in sync, without re-deriving the graph
      // ourselves on the frontend
      if (!result.completed) {
        queryClient.setQueryData(["quest-session", sessionId], (old: unknown) => {
          if (!old || typeof old !== "object") return old;
          return { ...old, current_node: result.next_node };
        });
      } else {
        queryClient.invalidateQueries({ queryKey: ["quest-session", sessionId] });
      }
    },
  });
}
