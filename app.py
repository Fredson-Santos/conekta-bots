from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import engine, Bot, Regra, LogExecucao, Agendamento
from starlette.middleware.sessions import SessionMiddleware
import secrets
import uuid
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.sessions import StringSession

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))
templates = Jinja2Templates(directory="templates")

# Armazenamento temporário de clientes em autenticação
pending_auth_clients = {}

def cleanup_expired_auth():
    """Remove sessões de autenticação expiradas (> 5 minutos)"""
    now = datetime.now()
    expired = [
        auth_id for auth_id, data in pending_auth_clients.items()
        if now - data["created_at"] > timedelta(minutes=5)
    ]
    for auth_id in expired:
        try:
            asyncio.create_task(pending_auth_clients[auth_id]["client"].disconnect())
        except:
            pass
        del pending_auth_clients[auth_id]

def get_session():
    with Session(engine) as session:
        yield session

# --- ROTAS PRINCIPAIS ---

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: Session = Depends(get_session)):
    try:
        bots = session.exec(select(Bot)).all()
        logs = session.exec(select(LogExecucao).order_by(LogExecucao.data_hora.desc()).limit(10)).all()
        
        # Pega e limpa mensagens flash
        flash_message = request.session.pop("flash_message", None)
        flash_type = request.session.pop("flash_type", "info")
        
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "bots": bots, 
            "logs": logs,
            "flash_message": flash_message,
            "flash_type": flash_type
        })
    except Exception as e:
        print(f"Erro no dashboard: {e}")
        # Retorna com listas vazias em caso de erro
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "bots": [], 
            "logs": [],
            "flash_message": None,
            "flash_type": "info"
        })

# --- GESTÃO DE BOTS (NOVO) ---

@app.get("/bots/adicionar", response_class=HTMLResponse)
async def form_adicionar_bot(request: Request):
    return templates.TemplateResponse("adicionar_bot.html", {"request": request})

@app.post("/bots/criar")
async def criar_bot(
    request: Request,
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
    
    # Flash message
    request.session["flash_message"] = f"Bot '{nome}' criado com sucesso!"
    request.session["flash_type"] = "success"
    
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

@app.post("/bots/toggle/{id}")
async def toggle_bot(request: Request, id: int, session: Session = Depends(get_session)):
    """Toggle bot active status via HTMX"""
    bot = session.get(Bot, id)
    if bot:
        # Inverte o status
        bot.ativo = not bot.ativo
        session.add(bot)
        session.commit()
        session.refresh(bot)
        
        # Retorna a linha atualizada da tabela (HTMX vai substituir)
        return templates.TemplateResponse("bot_table_row.html", {
            "request": request,
            "bot": bot
        })
    
    return HTMLResponse("<tr><td colspan='5' class='p-4 text-red-600'>Erro ao atualizar bot</td></tr>", status_code=404)

@app.get("/bots/editar/{id}", response_class=HTMLResponse)
async def form_editar_bot(request: Request, id: int, session: Session = Depends(get_session)):
    bot = session.get(Bot, id)
    if not bot:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("editar_bot.html", {"request": request, "bot": bot})

@app.post("/bots/editar/{id}")
async def atualizar_bot(
    request: Request,
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
        
        # Flash message
        request.session["flash_message"] = f"Bot '{nome}' atualizado com sucesso!"
        request.session["flash_type"] = "success"
    
    return RedirectResponse(url="/", status_code=303)

# --- AUTENTICAÇÃO POR TELEFONE ---

@app.post("/bots/auth/start")
async def iniciar_autenticacao(
    request: Request,
    nome: str = Form(...),
    api_id: str = Form(...),
    api_hash: str = Form(...),
    phone: str = Form(...)
):
    """Inicia autenticação Telethon e envia código"""
    cleanup_expired_auth()
    
    try:
        # Criar cliente Telethon temporário
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        
        # Enviar código
        await client.send_code_request(phone)
        
        # Gerar ID único para esta autenticação
        auth_id = str(uuid.uuid4())
        
        # Armazenar temporariamente
        pending_auth_clients[auth_id] = {
            "client": client,
            "nome": nome,
            "api_id": api_id,
            "api_hash": api_hash,
            "phone": phone,
            "created_at": datetime.now()
        }
        
        # Retornar HTML com próximo passo (HTMX)
        return templates.TemplateResponse("auth_step2.html", {
            "request": request,
            "auth_id": auth_id,
            "phone": phone
        })
        
    except Exception as e:
        return HTMLResponse(
            f'<div class="text-red-600 p-4 bg-red-50 rounded">❌ Erro: {str(e)}</div>',
            status_code=400
        )

@app.post("/bots/auth/verify")
async def verificar_codigo(
    request: Request,
    auth_id: str = Form(...),
    code: str = Form(...),
    session: Session = Depends(get_session)
):
    """Verifica código e cria bot"""
    if auth_id not in pending_auth_clients:
        return HTMLResponse(
            '<div class="text-red-600 p-4 bg-red-50 rounded">❌ Sessão expirada. Tente novamente.</div>',
            status_code=400
        )
    
    auth_data = pending_auth_clients[auth_id]
    
    try:
        # Autenticar com código
        await auth_data["client"].sign_in(auth_data["phone"], code)
        
        # Obter session string
        session_string = auth_data["client"].session.save()
        
        # Criar bot no banco
        novo_bot = Bot(
            nome=auth_data["nome"],
            api_id=auth_data["api_id"],
            api_hash=auth_data["api_hash"],
            tipo="user",
            phone=auth_data["phone"],
            session_string=session_string,
            ativo=True
        )
        session.add(novo_bot)
        session.commit()
        
        # Desconectar e limpar
        await auth_data["client"].disconnect()
        del pending_auth_clients[auth_id]
        
        # Flash message
        request.session["flash_message"] = f"Bot '{novo_bot.nome}' autenticado com sucesso!"
        request.session["flash_type"] = "success"
        
        # Redirecionar para home
        return HTMLResponse(
            '<script>window.location.href="/";</script>'
        )
        
    except Exception as e:
        return HTMLResponse(
            f'<div class="text-red-600 p-4 bg-red-50 rounded">❌ Código inválido: {str(e)}</div>',
            status_code=400
        )

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

@app.post("/agendamentos/enviar/{id}")
async def enviar_agora_agendamento(request: Request, id: int, session: Session = Depends(get_session)):
    """Envia imediatamente a mensagem agendada (sem esperar horário)"""
    ag = session.get(Agendamento, id)
    
    if not ag:
        return HTMLResponse('<div class="text-red-600">Agendamento não encontrado</div>', status_code=404)
    
    # Buscar o bot associado
    bot = session.get(Bot, ag.bot_id)
    if not bot or not bot.ativo:
        return HTMLResponse('<div class="text-yellow-600">⚠️ Bot inativo ou não encontrado</div>', status_code=400)
    
    try:
        # Conectar Telethon temporariamente para enviar mensagem
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        
        client = TelegramClient(StringSession(bot.session_string), bot.api_id, bot.api_hash)
        await client.connect()
        
        # Se for bot API, autenticar com token
        if bot.tipo == "bot" and bot.bot_token:
            await client.start(bot_token=bot.bot_token)
        elif not await client.is_user_authorized():
            await client.disconnect()
            return HTMLResponse('<div class="text-red-600">❌ Bot não autorizado</div>', status_code=400)
        
        # Enviar mensagem (buscar e reenviar sem autor original)
        print(f"[DEBUG] Buscando mensagem ID {ag.msg_id_atual} de {ag.origem}")
        original_msg = await client.get_messages(ag.origem, ids=ag.msg_id_atual)
        
        print(f"[DEBUG] Mensagem encontrada: {original_msg}")
        
        if not original_msg or (not original_msg.message and not original_msg.media):
            await client.disconnect()
            return HTMLResponse('<div class="text-red-600">❌ Mensagem original não encontrada ou vazia</div>', status_code=404)
        
        # Reenviar como nova mensagem (remove o nome do autor)
        # Em Telethon, 'message' contém o texto (seja text ou caption)
        msg_text = original_msg.message or ""
        
        print(f"[DEBUG] Enviando para {ag.destino}: texto='{msg_text[:50] if msg_text else 'SEM TEXTO'}...', tem_media={bool(original_msg.media)}")
        
        await client.send_message(
            entity=ag.destino,
            message=msg_text if msg_text else None,
            file=original_msg.media if original_msg.media else None
        )
        
        print(f"[DEBUG] Mensagem enviada com sucesso!")
        
        # Se for sequencial, incrementar o ID
        if ag.tipo_envio == "sequencial":
            ag.msg_id_atual += 1
            session.add(ag)
            session.commit()
        
        await client.disconnect()
        
        # Retornar mensagem de sucesso
        return HTMLResponse(
            f'<div class="text-green-600 font-bold p-2 bg-green-50 rounded">✅ Mensagem ID {ag.msg_id_atual - 1 if ag.tipo_envio == "sequencial" else ag.msg_id_atual} enviada com sucesso!</div>'
        )
        
    except Exception as e:
        print(f"[ERRO] Exceção ao enviar mensagem: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Tratamento específico para FloodWaitError
        error_message = str(e)
        if "FloodWait" in type(e).__name__ or "wait of" in error_message.lower():
            # Extrair tempo de espera se possível
            import re
            wait_match = re.search(r'(\d+)\s*second', error_message)
            wait_time = int(wait_match.group(1)) if wait_match else 0
            wait_minutes = wait_time // 60
            
            return HTMLResponse(
                f'<div class="text-orange-600 p-2 bg-orange-50 rounded">⏳ Telegram bloqueou temporariamente (muitas requisições). Aguarde {wait_minutes} minutos e tente novamente.</div>',
                status_code=429
            )
        
        return HTMLResponse(
            f'<div class="text-red-600 p-2 bg-red-50 rounded">❌ Erro: {str(e)}</div>',
            status_code=500
        )

# --- BLOQUEIOS ---

@app.get("/bloqueios", response_class=HTMLResponse)
async def listar_bloqueios(request: Request):
    # Redireciona para regras, pois movemos os bloqueios para lá
    return RedirectResponse(url="/regras") 

# --- HTMX ---

@app.get("/htmx/logs", response_class=HTMLResponse)
async def pegar_logs_htmx(request: Request, session: Session = Depends(get_session)):
    try:
        logs = session.exec(select(LogExecucao).order_by(LogExecucao.data_hora.desc()).limit(10)).all()
        return templates.TemplateResponse("fragmento_logs.html", {"request": request, "logs": logs})
    except Exception as e:
        print(f"Erro ao buscar logs: {e}")
        return templates.TemplateResponse("fragmento_logs.html", {"request": request, "logs": []})