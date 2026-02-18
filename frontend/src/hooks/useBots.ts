import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { botService } from "@/services/botService";
import type { BotUpdate } from "@/services/botService";

export const useBots = () => {
    const queryClient = useQueryClient();

    const botsQuery = useQuery({
        queryKey: ["bots"],
        queryFn: botService.getAll,
    });

    const createBotMutation = useMutation({
        mutationFn: botService.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["bots"] });
        },
    });

    const updateBotMutation = useMutation({
        mutationFn: ({ id, data }: { id: number; data: BotUpdate }) =>
            botService.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["bots"] });
        },
    });

    const deleteBotMutation = useMutation({
        mutationFn: botService.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["bots"] });
        },
    });

    const toggleBotMutation = useMutation({
        mutationFn: botService.toggle,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["bots"] });
        }
    });

    return {
        bots: botsQuery.data,
        isLoading: botsQuery.isLoading,
        isError: botsQuery.isError,
        error: botsQuery.error,
        createBot: createBotMutation.mutate,
        updateBot: updateBotMutation.mutate,
        deleteBot: deleteBotMutation.mutate,
        toggleBot: toggleBotMutation.mutate,
        isCreating: createBotMutation.isPending,
    };
};
