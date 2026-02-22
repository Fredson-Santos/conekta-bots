import api from "@/lib/api";
import type { Bot } from "@/types";

export interface BotCreate {
    nome: string;
    api_id: string;
    api_hash: string;
    phone?: string;
    tipo: string;
    bot_token?: string;
    session_string?: string;
}

export interface BotUpdate {
    nome?: string;
    ativo?: boolean;
}

export interface BotAuthStart {
    nome: string;
    api_id: string;
    api_hash: string;
    phone: string;
}

export interface BotAuthVerify {
    auth_id: string;
    code: string;
    password?: string;
}

export const botService = {
    getAll: async (): Promise<Bot[]> => {
        const { data } = await api.get<Bot[]>("/bots/");
        return data;
    },

    getById: async (id: number): Promise<Bot> => {
        const { data } = await api.get<Bot>(`/bots/${id}`);
        return data;
    },

    create: async (payload: BotCreate): Promise<Bot> => {
        const { data } = await api.post<Bot>("/bots/", payload);
        return data;
    },

    update: async (id: number, payload: BotUpdate): Promise<Bot> => {
        const { data } = await api.patch<Bot>(`/bots/${id}`, payload);
        return data;
    },

    delete: async (id: number): Promise<void> => {
        await api.delete(`/bots/${id}`);
    },

    toggle: async (id: number): Promise<Bot> => {
        const { data } = await api.patch<Bot>(`/bots/${id}/toggle`);
        return data;
    },

    startAuth: async (payload: BotAuthStart): Promise<{ auth_id: string; message: string }> => {
        const { data } = await api.post<{ auth_id: string; message: string }>("/bots/auth/start", payload);
        return data;
    },

    verifyAuth: async (payload: BotAuthVerify): Promise<Bot> => {
        const { data } = await api.post<Bot>("/bots/auth/verify", payload);
        return data;
    },
};
