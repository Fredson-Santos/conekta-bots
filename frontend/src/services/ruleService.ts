import api from "@/lib/api";
import type { Rule } from "@/types";

export interface RuleCreate {
    nome: string;
    gatilho: string;
    resposta: string;
    ativo?: boolean;
    bot_id: number;
}

export interface RuleUpdate {
    nome?: string;
    gatilho?: string;
    resposta?: string;
    ativo?: boolean;
}

export const ruleService = {
    getAll: async (): Promise<Rule[]> => {
        const response = await api.get<Rule[]>("/rules/");
        return response.data;
    },

    getById: async (id: number): Promise<Rule> => {
        const response = await api.get<Rule>(`/rules/${id}`);
        return response.data;
    },

    create: async (data: RuleCreate): Promise<Rule> => {
        const response = await api.post<Rule>("/rules/", data);
        return response.data;
    },

    update: async (id: number, data: RuleUpdate): Promise<Rule> => {
        const response = await api.put<Rule>(`/rules/${id}`, data);
        return response.data;
    },

    delete: async (id: number): Promise<void> => {
        await api.delete(`/rules/${id}`);
    }
};
