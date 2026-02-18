import api from "@/lib/api";
import type { Bot } from "@/types";

export interface BotCreate {
    nome: string;
    api_id: string;
    api_hash: string;
    phone: string;
    tipo: string;
    bot_token?: string;
    session_string?: string;
}

export interface BotUpdate {
    nome?: string;
    ativo?: boolean;
}

export const botService = {
    getAll: async (): Promise<Bot[]> => {
        const response = await api.get<Bot[]>("/bots/");
        return response.data;
    },

    getById: async (id: number): Promise<Bot> => {
        const response = await api.get<Bot>(`/bots/${id}`);
        return response.data;
    },

    create: async (data: BotCreate): Promise<Bot> => {
        const response = await api.post<Bot>("/bots/", data);
        return response.data;
    },

    update: async (id: number, data: BotUpdate): Promise<Bot> => {
        const response = await api.put<Bot>(`/bots/${id}`, data);
        return response.data;
    },

    delete: async (id: number): Promise<void> => {
        await api.delete(`/bots/${id}`);
    },

    toggle: async (id: number): Promise<Bot> => {
        const response = await api.post<Bot>(`/bots/${id}/toggle`);
        return response.data;
    },

    startAuth: async (id: number): Promise<{ auth_id: string; message: string }> => {
        const response = await api.post<{ auth_id: string; message: string }>(`/bots/${id}/auth/start`);
        return response.data;
    },

    verifyAuth: async (id: number, code: string, password?: string): Promise<Bot> => {
        const response = await api.post<Bot>(`/bots/${id}/auth/verify`, {
            code,
            password
        });
        return response.data;
    }
};
