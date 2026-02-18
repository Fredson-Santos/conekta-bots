import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { botService } from "@/services/botService";
import type { BotCreate } from "@/services/botService";

export function useBots() {
    const queryClient = useQueryClient();

    const { data: bots, isLoading } = useQuery({
        queryKey: ["bots"],
        queryFn: botService.getAll,
    });

    const { mutate: createBot, isPending: isCreating } = useMutation({
        mutationFn: (data: BotCreate) => botService.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["bots"] });
        },
    });

    const { mutate: updateBot } = useMutation({
        mutationFn: ({ id, data }: { id: number; data: any }) =>
            botService.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["bots"] });
        },
    });

    const { mutate: deleteBot } = useMutation({
        mutationFn: (id: number) => botService.delete(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["bots"] });
        },
    });

    const { mutate: toggleBot } = useMutation({
        mutationFn: (id: number) => botService.toggle(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["bots"] });
        },
    });

    return {
        bots,
        isLoading,
        createBot,
        isCreating,
        updateBot,
        deleteBot,
        toggleBot,
    };
}
