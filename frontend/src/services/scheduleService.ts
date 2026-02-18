import api from "@/lib/api";
import type { Schedule } from "@/types";

export interface ScheduleCreate {
    nome: string;
    origem: string;
    destino: string;
    msg_id_atual: number;
    tipo_envio: string;
    horario: string;
    bot_id: number;
}

export interface ScheduleUpdate {
    nome?: string;
    origem?: string;
    destino?: string;
    msg_id_atual?: number;
    tipo_envio?: string;
    horario?: string;
}

export const scheduleService = {
    getAll: async (): Promise<Schedule[]> => {
        const { data } = await api.get<Schedule[]>("/schedules/");
        return data;
    },

    getByBot: async (botId: number): Promise<Schedule[]> => {
        const { data } = await api.get<Schedule[]>(`/schedules/bot/${botId}`);
        return data;
    },

    getById: async (id: number): Promise<Schedule> => {
        const { data } = await api.get<Schedule>(`/schedules/${id}`);
        return data;
    },

    create: async (payload: ScheduleCreate): Promise<Schedule> => {
        const { data } = await api.post<Schedule>("/schedules/", payload);
        return data;
    },

    update: async (id: number, botId: number, payload: ScheduleUpdate): Promise<Schedule> => {
        const { data } = await api.patch<Schedule>(`/schedules/${id}/bot/${botId}`, payload);
        return data;
    },

    delete: async (id: number, botId: number): Promise<void> => {
        await api.delete(`/schedules/${id}/bot/${botId}`);
    },

    toggle: async (id: number, botId: number): Promise<Schedule> => {
        const { data } = await api.patch<Schedule>(`/schedules/${id}/bot/${botId}/toggle`);
        return data;
    },
};
