import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ruleService } from "@/services/ruleService";
import type { RuleCreate } from "@/services/ruleService";

export function useRules() {
    const queryClient = useQueryClient();

    const { data: rules, isLoading } = useQuery({
        queryKey: ["rules"],
        queryFn: ruleService.getAll,
    });

    const { mutate: createRule, isPending: isCreating } = useMutation({
        mutationFn: (data: RuleCreate) => ruleService.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["rules"] });
        },
    });

    const { mutate: deleteRule } = useMutation({
        mutationFn: ({ ruleId, botId }: { ruleId: number; botId: number }) =>
            ruleService.delete(ruleId, botId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["rules"] });
        },
    });

    const { mutate: toggleRule } = useMutation({
        mutationFn: ({ ruleId, botId }: { ruleId: number; botId: number }) =>
            ruleService.toggle(ruleId, botId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["rules"] });
        },
    });

    return {
        rules,
        isLoading,
        createRule,
        isCreating,
        deleteRule,
        toggleRule,
    };
}
