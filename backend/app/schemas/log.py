from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bot_id: int
    bot_nome: str
    origem: str
    destino: str
    status: str
    mensagem: str
    data_hora: datetime
