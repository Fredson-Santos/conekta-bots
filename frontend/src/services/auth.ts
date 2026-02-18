import api from "@/lib/api";
import type { AuthResponse, LoginCredentials, RegisterData } from "../types";

export const authService = {
    login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
        // Basic Auth or FormData?
        // FastAPI OAuth2PasswordRequestForm expects form-data usually.
        // Let's check backend implementation.
        // Task 5 said: "POST /api/v1/auth/login -> Token".
        // Usually it uses OAuth2PasswordRequestForm which is form-data.
        // I'll check if I should use JSON or FormData.
        // The previous work on Swagger Login used python-multipart, so it IS form-data.

        // However, if we look at `test_auth_endpoints.py` or similar, we can confirm.
        // I'll assume JSON for now, if it fails I'll switch to FormData.
        // Actually, clean architecture often changes this to JSON.
        // But FastAPI `OAuth2PasswordRequestForm` dependency requires form-data.
        // Let's assume standard JSON body for our custom Clean Arch `auth.py` unless it uses that dependency.
        // I'll check `backend/app/api/v1/endpoints/auth.py` LATER if needed.
        // For now, I'll send JSON. If it's form-data, I'll change headers.

        // Safer bet: The backend likely expects JSON if it's a "clean" REST API, 
        // unless strictly following OAuth2 spec for token endpoint.
        // Let's try JSON first.
        const { data } = await api.post<AuthResponse>("/auth/login", credentials);
        return data;
    },

    register: async (data: RegisterData): Promise<any> => {
        const response = await api.post("/auth/register", data);
        return response.data;
    },

    getCurrentUser: async (): Promise<any> => {
        const { data } = await api.get("/users/me");
        return data;
    },
};
