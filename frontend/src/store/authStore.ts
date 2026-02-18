import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User, AuthResponse } from "../types";
// Import api conditionally to avoid circular dependency if needed, 
// strictly speaking we use api in actions usually, but let's define types first.

// We will define types in src/types/index.ts usually. 
// For now, I'll put minimal types here or assume they exist.
// Let's create types file first? No, I'll inline interfaces for now or creating types file is better practice.

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    setAuth: (data: AuthResponse) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            setAuth: (data) =>
                set({
                    user: data.user,
                    token: data.access_token,
                    isAuthenticated: true,
                }),
            logout: () => set({ user: null, token: null, isAuthenticated: false }),
        }),
        {
            name: "auth-storage",
        }
    )
);
