export interface User {
    id: number;
    email: string;
    is_active: boolean;
    plan: string;
    max_bots: number;
}

export interface Token {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface RegisterData {
    email: string;
    password: string;
}

export interface Bot {
    id: number;
    nome: string;
    api_id: string;
    phone?: string;
    tipo: string;
    ativo: boolean;
    owner_id: number;
    created_at?: string;
}

export interface Rule {
    id: number;
    nome: string;
    origem: string;
    destino: string;
    filtro: string | null;
    substituto: string | null;
    bloqueios: string | null;
    somente_se_tiver: string | null;
    converter_shopee: boolean;
    ativo: boolean;
    bot_id: number;
}

export interface Configuracao {
    id: number;
    shopee_app_id: string | null;
    shopee_app_secret: string | null;
    owner_id: number;
}

export interface Schedule {
    id: number;
    nome: string;
    origem: string;
    destino: string;
    msg_id_atual: number;
    tipo_envio: string;
    horario: string;
    ativo: boolean;
    bot_id: number;
}

export interface Log {
    id: number;
    bot_id: number;
    bot_nome: string;
    origem: string;
    destino: string;
    status: string;
    mensagem: string;
    data_hora: string;
}
