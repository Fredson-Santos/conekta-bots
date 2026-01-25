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
    
    # Relações
    regras: List["Regra"] = Relationship(back_populates="bot")
    agendamentos: List["Agendamento"] = Relationship(back_populates="bot") # NOVO

# --- MODELO REGRA (Repasse Imediato) ---
class Regra(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    origem: str
    destino: str
    filtro: Optional[str] = None
    substituto: Optional[str] = None
    bot_id: int = Field(foreign_key="bot.id")
    bot: Optional[Bot] = Relationship(back_populates="regras")
    ativo: bool = Field(default=True)

# --- NOVO MODELO: AGENDAMENTO (Envio Programado) ---
class Agendamento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str           # Ex: "Oferta Manhã"
    origem: str         # Canal de onde vamos copiar a mensagem (ID ou Username)
    destino: str        # Para onde vai
    msg_id_atual: int   # Qual ID de mensagem vamos enviar hoje?
    
    # Tipo: "sequencial" (soma +1 no ID após enviar) ou "fixo" (repete a mesma)
    tipo_envio: str     
    
    horario: str        # Formato "HH:MM" (Ex: "10:00")
    
    bot_id: int = Field(foreign_key="bot.id")
    bot: Optional[Bot] = Relationship(back_populates="agendamentos")
    ativo: bool = Field(default=True)

# --- MODELO LOG ---
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
    print("✅ Banco de dados atualizado com Agendamentos!")