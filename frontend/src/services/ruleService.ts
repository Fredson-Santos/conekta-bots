import api from "@/lib/api";
import type { Rule } from "@/types";

export interface RuleCreate {
    nome: string;
    origem: string;
    destino: string;
    bot_id: number;
    filtro?: string;
    substituto?: string;
    bloqueios?: string;
    somente_se_tiver?: string;
    converter_shopee?: boolean;
}

export interface RuleUpdate {
    nome?: string;
    origem?: string;
    destino?: string;
    filtro?: string | null;
    substituto?: string | null;
    bloqueios?: string | null;
    somente_se_tiver?: string | null;
    converter_shopee?: boolean;
}

export const ruleService = {
    getAll: async (): Promise<Rule[]> => {
        const { data } = await api.get<Rule[]>("/rules/");
        return data;
    },

    getByBot: async (botId: number): Promise<Rule[]> => {
        const { data } = await api.get<Rule[]>(`/rules/bot/${botId}`);
        return data;
    },

    getById: async (id: number): Promise<Rule> => {
        const { data } = await api.get<Rule>(`/rules/${id}`);
        return data;
    },

    create: async (payload: RuleCreate): Promise<Rule> => {
        const { data } = await api.post<Rule>("/rules/", payload);
        return data;
    },

    update: async (id: number, botId: number, payload: RuleUpdate): Promise<Rule> => {
        const { data } = await api.patch<Rule>(`/rules/${id}/bot/${botId}`, payload);
        return data;
    },

    delete: async (id: number, botId: number): Promise<void> => {
        await api.delete(`/rules/${id}/bot/${botId}`);
    },

    toggle: async (id: number, botId: number): Promise<Rule> => {
        const { data } = await api.patch<Rule>(`/rules/${id}/bot/${botId}/toggle`);
        return data;
    },
};
