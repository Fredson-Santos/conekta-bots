from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, create_engine, Relationship

# --- MODELO BOT ---
class Bot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    api_id: str
    api_hash: str
    phone: Optional[str] = None
    bot_token: Optional[str] = None
    tipo: str = Field(default="user")
    session_string: Optional[str] = None
    ativo: bool = Field(default=True)
    regras: List["Regra"] = Relationship(back_populates="bot")

# --- MODELO REGRA ---
class Regra(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    origem: str
    destino: str
    bot_id: int = Field(foreign_key="bot.id")
    bot: Optional[Bot] = Relationship(back_populates="regras")
    ativo: bool = Field(default=True)

# --- NOVO MODELO: LOG DE EXECUÇÃO (Isto faltava no seu arquivo) ---
class LogExecucao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bot_id: int = Field(foreign_key="bot.id")
    bot_nome: str
    origem: str
    destino: str
    status: str
    mensagem: str
    data_hora: datetime = Field(default_factory=datetime.now)

# --- CONFIGURAÇÃO ---
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    create_db_and_tables()
    print("✅ Banco de dados atualizado com Logs!")