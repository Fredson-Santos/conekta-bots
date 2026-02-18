from pydantic import BaseModel, ConfigDict, Field


class BotCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    api_id: str
    api_hash: str
    tipo: str = Field(default="user", pattern="^(user|bot)$")
    bot_token: str | None = None
    phone: str | None = None
    session_string: str | None = None


class BotUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    api_id: str | None = None
    api_hash: str | None = None
    tipo: str | None = Field(default=None, pattern="^(user|bot)$")
    bot_token: str | None = None
    phone: str | None = None
    session_string: str | None = None


class BotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    api_id: str
    tipo: str
    phone: str | None = None
    ativo: bool
    owner_id: int
    # session_string e api_hash OMITIDOS por segurança


class BotToggleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    ativo: bool


# --- Auth por telefone (Telethon) ---


class BotAuthStart(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    api_id: str
    api_hash: str
    phone: str


class BotAuthVerify(BaseModel):
    auth_id: str
    code: str


class BotAuthResponse(BaseModel):
    auth_id: str
    message: str
