import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { scheduleService } from "@/services/scheduleService";
import type { ScheduleCreate } from "@/services/scheduleService";

export function useSchedules() {
    const queryClient = useQueryClient();

    const { data: schedules, isLoading } = useQuery({
        queryKey: ["schedules"],
        queryFn: scheduleService.getAll,
    });

    const { mutate: createSchedule, isPending: isCreating } = useMutation({
        mutationFn: (data: ScheduleCreate) => scheduleService.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["schedules"] });
        },
    });

    const { mutate: deleteSchedule } = useMutation({
        mutationFn: ({ scheduleId, botId }: { scheduleId: number; botId: number }) =>
            scheduleService.delete(scheduleId, botId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["schedules"] });
        },
    });

    const { mutate: toggleSchedule } = useMutation({
        mutationFn: ({ scheduleId, botId }: { scheduleId: number; botId: number }) =>
            scheduleService.toggle(scheduleId, botId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["schedules"] });
        },
    });

    return {
        schedules,
        isLoading,
        createSchedule,
        isCreating,
        deleteSchedule,
        toggleSchedule,
    };
}
