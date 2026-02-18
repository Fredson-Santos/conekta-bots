import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ruleService } from "@/services/ruleService";
import type { RuleUpdate } from "@/services/ruleService";

export const useRules = () => {
    const queryClient = useQueryClient();

    const rulesQuery = useQuery({
        queryKey: ["rules"],
        queryFn: ruleService.getAll,
    });

    const createRuleMutation = useMutation({
        mutationFn: ruleService.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["rules"] });
        },
    });

    const updateRuleMutation = useMutation({
        mutationFn: ({ id, data }: { id: number; data: RuleUpdate }) =>
            ruleService.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["rules"] });
        },
    });

    const deleteRuleMutation = useMutation({
        mutationFn: ruleService.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["rules"] });
        },
    });

    return {
        rules: rulesQuery.data,
        isLoading: rulesQuery.isLoading,
        isError: rulesQuery.isError,
        error: rulesQuery.error,
        createRule: createRuleMutation.mutate,
        updateRule: updateRuleMutation.mutate,
        deleteRule: deleteRuleMutation.mutate,
        isCreating: createRuleMutation.isPending,
    };
};
