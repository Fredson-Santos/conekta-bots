from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
# IMPORTANTE: Adicione LogExecucao aqui na importação
from database import engine, Bot, Regra, LogExecucao, Agendamento

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: Session = Depends(get_session)):
    bots = session.exec(select(Bot)).all()
    
    # --- NOVO: BUSCAR OS LOGS ---
    # Se esta parte faltar, o site não recebe os dados!
    logs = session.exec(
        select(LogExecucao).order_by(LogExecucao.data_hora.desc()).limit(10)
    ).all()
    # ----------------------------
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "bots": bots, "logs": logs} # Passamos 'logs' aqui
    )

# ... (Mantenha as rotas de regras e outras como estavam) ...
# Vou repetir a rota de regras aqui para garantir que você tenha o arquivo completo se quiser copiar tudo:

@app.get("/regras", response_class=HTMLResponse)
async def listar_regras(request: Request, session: Session = Depends(get_session)):
    regras = session.exec(select(Regra)).all()
    bots = session.exec(select(Bot)).all()
    return templates.TemplateResponse("regras.html", {"request": request, "regras": regras, "bots": bots})

@app.post("/regras/criar")
async def criar_regra(
    nome: str = Form(...),
    origem: str = Form(...),
    destino: str = Form(...),
    bot_id: int = Form(...),
    # NOVOS CAMPOS OPCIONAIS
    filtro: str = Form(None), 
    substituto: str = Form(None),
    session: Session = Depends(get_session)
):
    nova_regra = Regra(
        nome=nome, 
        origem=origem, 
        destino=destino, 
        bot_id=bot_id, 
        filtro=filtro,         # Salva no banco
        substituto=substituto, # Salva no banco
        ativo=True
    )
    session.add(nova_regra)
    session.commit()
    
    return RedirectResponse(url="/regras", status_code=303)


# --- Adicione esta rota nova no app.py ---

@app.get("/htmx/logs", response_class=HTMLResponse)
async def pegar_logs_htmx(request: Request, session: Session = Depends(get_session)):
    # Busca apenas os logs mais recentes
    logs = session.exec(
        select(LogExecucao).order_by(LogExecucao.data_hora.desc()).limit(10)
    ).all()
    
    # Retorna APENAS o pedacinho da tabela
    return templates.TemplateResponse(
        "fragmento_logs.html", 
        {"request": request, "logs": logs}
    )

@app.get("/regras/deletar/{id}")
async def deletar_regra(id: int, session: Session = Depends(get_session)):
    regra = session.get(Regra, id)
    if regra:
        session.delete(regra)
        session.commit()
    return RedirectResponse(url="/regras", status_code=303) 

# ROTA: LISTAR AGENDAMENTOS
@app.get("/agendamentos", response_class=HTMLResponse)
async def listar_agendamentos(request: Request, session: Session = Depends(get_session)):
    agendamentos = session.exec(select(Agendamento)).all()
    bots = session.exec(select(Bot)).all()
    return templates.TemplateResponse(
        "agendamentos.html", 
        {"request": request, "agendamentos": agendamentos, "bots": bots}
    )

# ROTA: CRIAR AGENDAMENTO
@app.post("/agendamentos/criar")
async def criar_agendamento(
    nome: str = Form(...),
    origem: str = Form(...),
    destino: str = Form(...),
    msg_id_atual: int = Form(...),
    tipo_envio: str = Form(...), # "fixo" ou "sequencial"
    horario: str = Form(...),    # "HH:MM"
    bot_id: int = Form(...),
    session: Session = Depends(get_session)
):
    novo_agendamento = Agendamento(
        nome=nome,
        origem=origem,
        destino=destino,
        msg_id_atual=msg_id_atual,
        tipo_envio=tipo_envio,
        horario=horario,
        bot_id=bot_id,
        ativo=True
    )
    session.add(novo_agendamento)
    session.commit()
    return RedirectResponse(url="/agendamentos", status_code=303)

# ROTA: DELETAR AGENDAMENTO
@app.get("/agendamentos/deletar/{id}")
async def deletar_agendamento(id: int, session: Session = Depends(get_session)):
    agendamento = session.get(Agendamento, id)
    if agendamento:
        session.delete(agendamento)
        session.commit()
    return RedirectResponse(url="/agendamentos", status_code=303)