import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { scheduleService } from "@/services/scheduleService";
import type { ScheduleUpdate } from "@/services/scheduleService";

export const useSchedules = () => {
    const queryClient = useQueryClient();

    const schedulesQuery = useQuery({
        queryKey: ["schedules"],
        queryFn: scheduleService.getAll,
    });

    const createScheduleMutation = useMutation({
        mutationFn: scheduleService.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["schedules"] });
        },
    });

    const updateScheduleMutation = useMutation({
        mutationFn: ({ id, data }: { id: number; data: ScheduleUpdate }) =>
            scheduleService.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["schedules"] });
        },
    });

    const deleteScheduleMutation = useMutation({
        mutationFn: scheduleService.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["schedules"] });
        },
    });

    return {
        schedules: schedulesQuery.data,
        isLoading: schedulesQuery.isLoading,
        isError: schedulesQuery.isError,
        error: schedulesQuery.error,
        createSchedule: createScheduleMutation.mutate,
        updateSchedule: updateScheduleMutation.mutate,
        deleteSchedule: deleteScheduleMutation.mutate,
        isCreating: createScheduleMutation.isPending,
    };
};
