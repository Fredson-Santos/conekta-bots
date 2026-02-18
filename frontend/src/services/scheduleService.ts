import api from "@/lib/api";
import type { Schedule } from "@/types";

export interface ScheduleCreate {
    mensagem: string;
    cron_expr: string;
    ativo?: boolean;
    bot_id: number;
}

export interface ScheduleUpdate {
    mensagem?: string;
    cron_expr?: string;
    ativo?: boolean;
}

export const scheduleService = {
    getAll: async (): Promise<Schedule[]> => {
        const response = await api.get<Schedule[]>("/schedules/");
        return response.data;
    },

    getById: async (id: number): Promise<Schedule> => {
        const response = await api.get<Schedule>(`/schedules/${id}`);
        return response.data;
    },

    create: async (data: ScheduleCreate): Promise<Schedule> => {
        const response = await api.post<Schedule>("/schedules/", data);
        return response.data;
    },

    update: async (id: number, data: ScheduleUpdate): Promise<Schedule> => {
        const response = await api.put<Schedule>(`/schedules/${id}`, data);
        return response.data;
    },

    delete: async (id: number): Promise<void> => {
        await api.delete(`/schedules/${id}`);
    },

    sendNow: async (id: number): Promise<void> => {
        await api.post(`/schedules/${id}/send`);
    }
};
