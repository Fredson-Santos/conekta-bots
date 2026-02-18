from pydantic import BaseModel, ConfigDict, Field


class ScheduleCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    origem: str
    destino: str
    msg_id_atual: int
    tipo_envio: str = Field(pattern="^(sequencial|fixo)$")
    horario: str  # "HH:MM" ou múltiplos "HH:MM,HH:MM"
    bot_id: int


class ScheduleUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    origem: str | None = None
    destino: str | None = None
    msg_id_atual: int | None = None
    tipo_envio: str | None = Field(default=None, pattern="^(sequencial|fixo)$")
    horario: str | None = None
    bot_id: int | None = None


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    origem: str
    destino: str
    msg_id_atual: int
    tipo_envio: str
    horario: str
    bot_id: int
    ativo: bool
