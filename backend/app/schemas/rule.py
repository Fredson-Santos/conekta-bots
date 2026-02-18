from pydantic import BaseModel, ConfigDict, Field


class RuleCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    origem: str
    destino: str
    bot_id: int
    filtro: str | None = None
    substituto: str | None = None
    bloqueios: str | None = None
    somente_se_tiver: str | None = None


class RuleUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    origem: str | None = None
    destino: str | None = None
    bot_id: int | None = None
    filtro: str | None = None
    substituto: str | None = None
    bloqueios: str | None = None
    somente_se_tiver: str | None = None


class RuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    origem: str
    destino: str
    bot_id: int
    filtro: str | None = None
    substituto: str | None = None
    bloqueios: str | None = None
    somente_se_tiver: str | None = None
    ativo: bool
