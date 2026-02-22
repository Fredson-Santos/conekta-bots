# 📐 ConektaBots — Guia de Arquitetura & Boas Práticas

## 1. Visão Geral do Projeto

**ConektaBots** é uma plataforma de gerenciamento de bots Telegram que permite:
- Cadastrar e gerenciar múltiplos bots (UserBots e Bot API)
- Criar regras de encaminhamento entre canais (com filtros regex, blacklist e whitelist)
- Agendar envio de mensagens com horários configuráveis
- Monitorar logs de execução em tempo real

### Stack Tecnológica

| Camada | Tecnologia | Propósito |
|--------|-----------|-----------|
| **API** | FastAPI | Framework web async com OpenAPI |
| **ORM** | SQLAlchemy 2.0 | Mapeamento objeto-relacional |
| **Migrations** | Alembic | Versionamento do schema do banco |
| **Auth** | PyJWT + pwdlib[argon2] | JWT tokens + hash Argon2 |
| **Telegram** | Telethon | Client API Telegram (MTProto) |
| **Validação** | Pydantic V2 | Schemas de entrada/saída |
| **Lint/Format** | Ruff | Linter + formatter unificados |
| **Testes** | pytest + httpx | Testes unit/integration async |
| **Tasks** | Taskipy | Task runner via `task <cmd>` |

---

## 2. Arquitetura Clean

### Diagrama de Camadas

```
┌─────────────────────────────────────────┐
│              API Layer                  │  ← Routers (endpoints)
│         app/api/v1/endpoints/           │     Recebe HTTP, valida, delega
├─────────────────────────────────────────┤
│            Schemas Layer                │  ← Pydantic DTOs
│             app/schemas/                │     Contratos de entrada/saída
├─────────────────────────────────────────┤
│           Services Layer                │  ← Business Logic
│            app/services/                │     Regras de negócio isoladas
├─────────────────────────────────────────┤
│            Models Layer                 │  ← SQLAlchemy Models
│             app/models/                 │     Representação do banco
├─────────────────────────────────────────┤
│              DB Layer                   │  ← Session & Engine
│               app/db/                   │     Conexão com o banco
└─────────────────────────────────────────┘
```

### Regras de Dependência

> [!IMPORTANT]
> As dependências fluem **somente para baixo**. Uma camada nunca importa de uma camada acima.

```
endpoints → services → models → db
endpoints → schemas (para validação I/O)
services  → schemas (para tipagem)
```

**Proibido:**
- ❌ `services` importar de `api/endpoints`
- ❌ `models` importar de `services`
- ❌ `endpoints` acessar `db` diretamente (sempre via `services`)

---

## 3. Estrutura de Diretórios

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                # Dependencies injetáveis (get_db, get_current_user)
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py        # POST /login, /register, /refresh
│   │       │   ├── bots.py        # CRUD bots
│   │       │   ├── rules.py       # CRUD regras
│   │       │   ├── schedules.py   # CRUD agendamentos
│   │       │   └── analytics.py   # GET logs
│   │       └── router.py          # Agrega todos os routers
│   ├── core/
│   │   ├── config.py              # Settings (env vars via Pydantic)
│   │   └── security.py            # JWT encode/decode, hash passwords
│   ├── models/                    # SQLAlchemy declarative models
│   ├── schemas/                   # Pydantic request/response DTOs
│   ├── services/                  # Business logic (uma classe por domínio)
│   ├── workers/                   # Bot workers (asyncio tasks)
│   ├── db/
│   │   ├── base.py                # DeclarativeBase
│   │   └── session.py             # Engine + SessionLocal
│   └── main.py                    # FastAPI app factory
├── tests/
│   ├── conftest.py                # Fixtures globais
│   ├── unit/                      # Testes de services (sem I/O)
│   └── integration/               # Testes de endpoints (com TestClient)
├── alembic/                       # Migrations
├── pyproject.toml                 # Deps, taskipy, ruff, pytest
└── .env.example                   # Template de variáveis de ambiente
```

---

## 4. Convenções de Código

### 4.1 Nomenclatura

| Item | Convenção | Exemplo |
|------|----------|---------|
| Arquivos | `snake_case.py` | `bot_service.py` |
| Classes | `PascalCase` | `BotService`, `BotCreate` |
| Funções/Métodos | `snake_case` | `get_user_bots()` |
| Variáveis | `snake_case` | `bot_token` |
| Constantes | `UPPER_SNAKE` | `ACCESS_TOKEN_EXPIRE` |
| Endpoints | `kebab-case` (URL) | `/api/v1/bots/{id}` |

### 4.2 Imports

Ordem (gerenciada automaticamente pelo Ruff `isort`):

```python
# 1. Standard library
from datetime import datetime

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 3. Local
from app.core.config import settings
from app.services.bot_service import BotService
```

### 4.3 Type Hints

**Obrigatório** em todas as funções e métodos:

```python
# ✅ Correto
async def get_bot(bot_id: int, user_id: int) -> Bot | None:
    ...

# ❌ Incorreto
async def get_bot(bot_id, user_id):
    ...
```

### 4.4 Docstrings

Use docstrings em services e funções complexas:

```python
async def create_bot(self, user_id: int, data: BotCreate) -> Bot:
    """Cria um novo bot vinculado ao usuário.

    Args:
        user_id: ID do usuário proprietário.
        data: Dados validados do bot.

    Returns:
        Bot criado com ID gerado.

    Raises:
        HTTPException(400): Se o limite de bots do plano for atingido.
    """
```

---

## 5. Padrões por Camada

### 5.1 Endpoints (API Layer)

```python
# app/api/v1/endpoints/bots.py
router = APIRouter(prefix="/bots", tags=["Bots"])

@router.get("/", response_model=list[BotResponse])
async def list_bots(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Endpoints NÃO contêm lógica de negócio — apenas delegam."""
    service = BotService(db)
    return await service.get_all(current_user.id)
```

**Regras:**
- Endpoints recebem dados validados via Pydantic schemas
- Delegam TODA lógica para services
- Retornam response models tipados
- Usam Dependency Injection (`Depends()`)

### 5.2 Services (Business Logic)

```python
# app/services/bot_service.py
class BotService:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, user_id: int, data: BotCreate) -> Bot:
        # Validações de negócio aqui
        user_bots = await self.get_all(user_id)
        if len(user_bots) >= MAX_BOTS_PER_USER:
            raise HTTPException(status_code=400, detail="Limite de bots atingido")

        bot = Bot(**data.model_dump(), owner_id=user_id)
        self.db.add(bot)
        self.db.commit()
        return bot
```

**Regras:**
- Uma classe por domínio (`BotService`, `RuleService`)
- Recebem `db: Session` no construtor
- Contêm validações de negócio
- Não conhecem HTTP (nada de `Request`, `Form`, `Response`)

### 5.3 Models (SQLAlchemy)

```python
# app/models/bot.py
from app.db.base import Base

class Bot(Base):
    __tablename__ = "bot"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="bots")
    regras: Mapped[list["Regra"]] = relationship(back_populates="bot", cascade="all, delete-orphan")
```

**Regras:**
- Usar `Mapped[]` (SQLAlchemy 2.0 style)
- Definir `cascade` em relationships
- Não incluir lógica de negócio

### 5.4 Schemas (Pydantic)

```python
# app/schemas/bot.py
class BotCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    api_id: str
    api_hash: str
    tipo: Literal["user", "bot"] = "user"

class BotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    tipo: str
    ativo: bool
```

**Regras:**
- `Create` — campos para criação (sem id)
- `Update` — todos opcionais (`field: str | None = None`)
- `Response` — o que o cliente recebe (`from_attributes=True`)
- Usar `Field()` para validações (min/max length, regex, etc.)

---

## 6. Segurança

### 6.1 Autenticação JWT

```python
# Fluxo:
1. POST /auth/login  → {email, password} → access_token + refresh_token
2. Requisições autenticadas → Header: Authorization: Bearer <access_token>
3. Token expirado → POST /auth/refresh → novo access_token
```

**Configurações obrigatórias:**
- `ACCESS_TOKEN_EXPIRE`: 30 minutos
- `REFRESH_TOKEN_EXPIRE`: 7 dias
- `SECRET_KEY`: Mínimo 32 caracteres, gerada com `secrets.token_urlsafe(32)`
- Algoritmo: `HS256`

### 6.2 Hash de Senhas

```python
# Usar pwdlib com Argon2 (NUNCA armazenar senha em texto)
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
hashed = password_hash.hash("senha_do_usuario")
is_valid = password_hash.verify("senha_do_usuario", hashed)
```

> [!CAUTION]
> **NUNCA** armazenar senhas em texto. Sempre usar Argon2 via `pwdlib`.

### 6.3 Proteção de Dados Sensíveis

- `session_string`, `api_hash`, `bot_token` são dados **sensíveis**
- **Nunca** retornar `session_string` em responses da API
- Usar `exclude` no schema de response:

```python
class BotResponse(BaseModel):
    # session_string OMITIDO intencionalmente
    id: int
    nome: str
    tipo: str
    ativo: bool
```

### 6.4 Variáveis de Ambiente

```bash
# .env.example
DATABASE_URL=sqlite:///./data/database.db
SECRET_KEY=CHANGE_ME_USE_secrets.token_urlsafe(32)
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:5173
```

> [!WARNING]
> **NUNCA** commitar `.env` no Git. Manter apenas `.env.example` como template.

### 6.5 CORS

```python
# Apenas origens permitidas (nunca usar "*" em produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 6.6 Validação de Input

- **Sempre** validar via Pydantic schemas antes de processamento
- Usar `Field()` com constraints (`min_length`, `max_length`, `regex`)
- Sanitizar regex do usuário (regras de whitelist/blacklist) com `try/except re.error`

---

## 7. Tratamento de Erros

### Padrão de Exceções

```python
# Em services — lançar HTTPException com mensagens claras
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Bot não encontrado"
)

raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Sem permissão para acessar este recurso"
)
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Nos workers (onde print é permitido temporariamente)
logger.info(f"Bot {bot.nome} conectado")
logger.error(f"Erro ao encaminhar mensagem: {e}")
```

---

## 8. Testes

### Estrutura

```
tests/
├── conftest.py           # Fixtures: test_db, test_client, auth_headers
├── unit/
│   ├── test_bot_service.py
│   ├── test_rule_service.py
│   └── test_security.py
└── integration/
    ├── test_auth_api.py
    └── test_bots_api.py
```

### Convenções

```python
# Nomes descritivos: test_<ação>_<resultado_esperado>
async def test_create_bot_returns_201():
    ...

async def test_create_bot_without_auth_returns_401():
    ...

async def test_create_bot_exceeding_limit_returns_400():
    ...
```

### Executar

```bash
task test          # Roda lint + testes
task lint          # Apenas lint (ruff check)
task format        # Auto-fix + format
```

---

## 9. Git & CI/CD

### Branches

| Branch | Propósito |
|--------|-----------|
| `main` | Produção (deploy automático) |
| `develop` | Integração de features |
| `feature/*` | Features novas |
| `fix/*` | Correções de bugs |

### Commits

Usar [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: adicionar CRUD de bots via API REST
fix: corrigir validação de regex em regras whitelist
refactor: extrair lógica de auth para AuthService
docs: adicionar guia de arquitetura
test: adicionar testes para BotService
```

### .gitignore

Manter sempre ignorados:
- `.env` (variáveis sensíveis)
- `data/database.db` (banco local)
- `__pycache__/`, `*.pyc`
- `.venv/`, `node_modules/`
- `sessions/` (Telethon sessions)
