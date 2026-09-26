import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { missionsApi } from "../../api/missions";

export function useMissions() {
  return useQuery({
    queryKey: ["missions"],
    queryFn: () => missionsApi.list(),
  });
}

export function useMission(missionId: string) {
  return useQuery({
    queryKey: ["mission", missionId],
    queryFn: () => missionsApi.get(missionId),
  });
}

export function useStartAttempt(missionId: string, playerId: string) {
  return useMutation({
    mutationFn: () => missionsApi.startAttempt(missionId, playerId),
  });
}

export function useSubmitAttempt(attemptId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ photoUrl, textAnswer }: { photoUrl?: string; textAnswer?: string }) => {
      if (!attemptId) throw new Error("No active attempt");
      return missionsApi.submitAttempt(attemptId, photoUrl, textAnswer);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["achievements"] });
    },
  });
}
