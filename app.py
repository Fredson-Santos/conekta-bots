from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import engine, Bot, Regra, LogExecucao, Agendamento

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_session():
    with Session(engine) as session:
        yield session

# ROTA: DASHBOARD
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: Session = Depends(get_session)):
    bots = session.exec(select(Bot)).all()
    logs = session.exec(select(LogExecucao).order_by(LogExecucao.data_hora.desc()).limit(10)).all()
    return templates.TemplateResponse("index.html", {"request": request, "bots": bots, "logs": logs})

# ROTA: LISTAR REGRAS
@app.get("/regras", response_class=HTMLResponse)
async def listar_regras(request: Request, session: Session = Depends(get_session)):
    regras = session.exec(select(Regra)).all()
    bots = session.exec(select(Bot)).all()
    return templates.TemplateResponse("regras.html", {"request": request, "regras": regras, "bots": bots})

# ROTA: CRIAR REGRA (ATUALIZADA)
@app.post("/regras/criar")
async def criar_regra(
    nome: str = Form(...),
    origem: str = Form(...),
    destino: str = Form(...),
    bot_id: int = Form(...),
    filtro: str = Form(None), 
    substituto: str = Form(None),
    bloqueios: str = Form(None), 
    somente_se_tiver: str = Form(None), # <--- NOVO CAMPO
    session: Session = Depends(get_session)
):
    nova_regra = Regra(
        nome=nome, 
        origem=origem, 
        destino=destino, 
        bot_id=bot_id, 
        filtro=filtro,
        substituto=substituto,
        bloqueios=bloqueios,
        somente_se_tiver=somente_se_tiver, # Salva no banco
        ativo=True
    )
    session.add(nova_regra)
    session.commit()
    return RedirectResponse(url="/regras", status_code=303)

# ROTA: DELETAR REGRA
@app.get("/regras/deletar/{id}")
async def deletar_regra(id: int, session: Session = Depends(get_session)):
    regra = session.get(Regra, id)
    if regra:
        session.delete(regra)
        session.commit()
    return RedirectResponse(url="/regras", status_code=303)

# ROTA: AGENDAMENTOS
@app.get("/agendamentos", response_class=HTMLResponse)
async def listar_agendamentos(request: Request, session: Session = Depends(get_session)):
    agendamentos = session.exec(select(Agendamento)).all()
    bots = session.exec(select(Bot)).all()
    return templates.TemplateResponse("agendamentos.html", {"request": request, "agendamentos": agendamentos, "bots": bots})

@app.post("/agendamentos/criar")
async def criar_agendamento(
    nome: str = Form(...), origem: str = Form(...), destino: str = Form(...),
    msg_id_atual: int = Form(...), tipo_envio: str = Form(...), horario: str = Form(...),
    bot_id: int = Form(...), session: Session = Depends(get_session)
):
    novo_agendamento = Agendamento(
        nome=nome, origem=origem, destino=destino, msg_id_atual=msg_id_atual,
        tipo_envio=tipo_envio, horario=horario, bot_id=bot_id, ativo=True
    )
    session.add(novo_agendamento)
    session.commit()
    return RedirectResponse(url="/agendamentos", status_code=303)

@app.get("/agendamentos/deletar/{id}")
async def deletar_agendamento(id: int, session: Session = Depends(get_session)):
    item = session.get(Agendamento, id)
    if item:
        session.delete(item)
        session.commit()
    return RedirectResponse(url="/agendamentos", status_code=303)

# ROTA: LOGS HTMX
@app.get("/htmx/logs", response_class=HTMLResponse)
async def pegar_logs_htmx(request: Request, session: Session = Depends(get_session)):
    logs = session.exec(select(LogExecucao).order_by(LogExecucao.data_hora.desc()).limit(10)).all()
    return templates.TemplateResponse("fragmento_logs.html", {"request": request, "logs": logs})