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

# --- ROTAS PRINCIPAIS ---

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: Session = Depends(get_session)):
    bots = session.exec(select(Bot)).all()
    logs = session.exec(select(LogExecucao).order_by(LogExecucao.data_hora.desc()).limit(10)).all()
    return templates.TemplateResponse("index.html", {"request": request, "bots": bots, "logs": logs})

# --- GESTÃO DE BOTS (NOVO) ---

@app.get("/bots/adicionar", response_class=HTMLResponse)
async def form_adicionar_bot(request: Request):
    return templates.TemplateResponse("adicionar_bot.html", {"request": request})

@app.post("/bots/criar")
async def criar_bot(
    nome: str = Form(...),
    tipo: str = Form(...),
    api_id: str = Form(...),
    api_hash: str = Form(...),
    bot_token: str = Form(None),
    phone: str = Form(None),
    session_string: str = Form(None),
    session: Session = Depends(get_session)
):
    # Lógica simples: Se for bot, usamos o token como session_string (padrão Telethon para bots)
    # Se for user, o usuário deve ter colado a string ou usaremos o phone (mas login web é complexo, ideal é colar string)
    
    sessao_final = session_string
    if tipo == "bot" and not session_string:
        sessao_final = None # O worker vai logar usando o token direto na hora do start
    
    novo_bot = Bot(
        nome=nome,
        api_id=api_id,
        api_hash=api_hash,
        tipo=tipo,
        bot_token=bot_token,
        phone=phone,
        session_string=sessao_final,
        ativo=True
    )
    session.add(novo_bot)
    session.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/bots/deletar/{id}")
async def deletar_bot(id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, id)
    if bot:
        # Nota: Ao deletar o bot, as regras e agendamentos filhos podem ficar órfãos ou dar erro
        # dependendo do banco. O ideal seria deletar tudo em cascata, mas vamos deletar o bot por enquanto.
        session.delete(bot)
        session.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/bots/editar/{id}", response_class=HTMLResponse)
async def form_editar_bot(request: Request, id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, id)
    if not bot:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("editar_bot.html", {"request": request, "bot": bot})

@app.post("/bots/editar/{id}")
async def atualizar_bot(
    id: int,
    nome: str = Form(...),
    tipo: str = Form(...),
    api_id: str = Form(...),
    api_hash: str = Form(...),
    bot_token: str = Form(None),
    phone: str = Form(None),
    session_string: str = Form(None),
    session: Session = Depends(get_session)
):
    bot = session.get(Bot, id)
    if bot:
        bot.nome = nome
        bot.tipo = tipo
        bot.api_id = api_id
        bot.api_hash = api_hash
        bot.bot_token = bot_token
        bot.phone = phone
        
        # Só atualiza a sessão se o usuário colou uma nova. 
        # Se deixar em branco, mantém a que já estava funcionando.
        if session_string and session_string.strip():
            bot.session_string = session_string
            
        session.add(bot)
        session.commit()
    return RedirectResponse(url="/", status_code=303)

# --- REGRAS ---

@app.get("/regras", response_class=HTMLResponse)
async def listar_regras(request: Request, session: Session = Depends(get_session)):
    regras = session.exec(select(Regra)).all()
    bots = session.exec(select(Bot)).all()
    return templates.TemplateResponse("regras.html", {"request": request, "regras": regras, "bots": bots})

@app.post("/regras/criar")
async def criar_regra(
    nome: str = Form(...), origem: str = Form(...), destino: str = Form(...), bot_id: int = Form(...),
    filtro: str = Form(None), substituto: str = Form(None), bloqueios: str = Form(None), somente_se_tiver: str = Form(None),
    session: Session = Depends(get_session)
):
    nova_regra = Regra(
        nome=nome, origem=origem, destino=destino, bot_id=bot_id,
        filtro=filtro, substituto=substituto, bloqueios=bloqueios, somente_se_tiver=somente_se_tiver, ativo=True
    )
    session.add(nova_regra)
    session.commit()
    return RedirectResponse(url="/regras", status_code=303)

@app.get("/regras/deletar/{id}")
async def deletar_regra(id: int, session: Session = Depends(get_session)):
    regra = session.get(Regra, id)
    if regra: session.delete(regra); session.commit()
    return RedirectResponse(url="/regras", status_code=303)

@app.get("/regras/editar/{id}", response_class=HTMLResponse)
async def form_editar_regra(request: Request, id: int, session: Session = Depends(get_session)):
    regra = session.get(Regra, id)
    bots = session.exec(select(Bot)).all()
    if not regra:
        return RedirectResponse(url="/regras", status_code=303)
    return templates.TemplateResponse("editar_regra.html", {"request": request, "regra": regra, "bots": bots})

@app.post("/regras/editar/{id}")
async def atualizar_regra(
    id: int,
    nome: str = Form(...),
    origem: str = Form(...),
    destino: str = Form(...),
    bot_id: int = Form(...),
    filtro: str = Form(None), 
    substituto: str = Form(None),
    bloqueios: str = Form(None), 
    somente_se_tiver: str = Form(None),
    session: Session = Depends(get_session)
):
    regra = session.get(Regra, id)
    if regra:
        regra.nome = nome
        regra.origem = origem
        regra.destino = destino
        regra.bot_id = bot_id
        regra.filtro = filtro
        regra.substituto = substituto
        regra.bloqueios = bloqueios
        regra.somente_se_tiver = somente_se_tiver
        session.add(regra)
        session.commit()
    return RedirectResponse(url="/regras", status_code=303)

# --- AGENDAMENTOS ---

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
    novo = Agendamento(
        nome=nome, origem=origem, destino=destino, msg_id_atual=msg_id_atual,
        tipo_envio=tipo_envio, horario=horario, bot_id=bot_id, ativo=True
    )
    session.add(novo); session.commit()
    return RedirectResponse(url="/agendamentos", status_code=303)

@app.get("/agendamentos/deletar/{id}")
async def deletar_agendamento(id: int, session: Session = Depends(get_session)):
    item = session.get(Agendamento, id)
    if item: session.delete(item); session.commit()
    return RedirectResponse(url="/agendamentos", status_code=303)

# --- BLOQUEIOS ---

@app.get("/bloqueios", response_class=HTMLResponse)
async def listar_bloqueios(request: Request):
    # Redireciona para regras, pois movemos os bloqueios para lá
    return RedirectResponse(url="/regras") 

# --- HTMX ---

@app.get("/htmx/logs", response_class=HTMLResponse)
async def pegar_logs_htmx(request: Request, session: Session = Depends(get_session)):
    logs = session.exec(select(LogExecucao).order_by(LogExecucao.data_hora.desc()).limit(10)).all()
    return templates.TemplateResponse("fragmento_logs.html", {"request": request, "logs": logs})