import api from "@/lib/api";
import type { Token, LoginCredentials, RegisterData, User } from "../types";

export const authService = {
    login: async (credentials: LoginCredentials): Promise<Token> => {
        const { data } = await api.post<Token>("/auth/login", credentials);
        return data;
    },

    register: async (data: RegisterData): Promise<any> => {
        const response = await api.post("/auth/register", {
            email: data.email,
            password: data.password,
        });
        return response.data;
    },

    getCurrentUser: async (): Promise<User> => {
        const { data } = await api.get<User>("/auth/me");
        return data;
    },

    refresh: async (refreshToken: string): Promise<Token> => {
        const { data } = await api.post<Token>("/auth/refresh", null, {
            params: { refresh_token: refreshToken },
        });
        return data;
    },
};
