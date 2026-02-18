import api from "@/lib/api";
import type { Configuracao } from "@/types";

export interface SettingsUpdate {
    shopee_app_id?: string | null;
    shopee_app_secret?: string | null;
}

export const settingsService = {
    getSettings: async (): Promise<Configuracao | null> => {
        const { data } = await api.get<Configuracao | null>("/settings/");
        return data;
    },

    updateSettings: async (payload: SettingsUpdate): Promise<Configuracao> => {
        const { data } = await api.put<Configuracao>("/settings/", payload);
        return data;
    },
};
