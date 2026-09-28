import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { parentsApi } from "../../api/auth";
import { playersApi } from "../../api/players";

export function useChildren() {
  return useQuery({
    queryKey: ["children"],
    queryFn: () => parentsApi.listChildren(),
  });
}

export function useAddChild() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => playersApi.create(name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["children"] });
    },
  });
}
