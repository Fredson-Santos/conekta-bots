export interface User {
    id: number;
    email: string;
    isActive: boolean;
    plan: string;
    max_bots: number;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user: User;
}

export interface LoginCredentials {
    username: string; // OAuth2 standard uses 'username' for email
    password: string;
}

export interface RegisterData {
    email: string;
    password: string;
    confirm_password?: string;
}

export interface Bot {
    id: number;
    nome: string;
    api_id: string;
    phone?: string;
    tipo: string;
    ativo: boolean;
    created_at?: string;
}

export interface Rule {
    id: number;
    nome: string;
    gatilho: string;
    resposta: string;
    ativo: boolean;
    bot_id: number;
}

export interface Schedule {
    id: number;
    mensagem: string;
    cron_expr: string;
    ativo: boolean;
    bot_id: number;
}
