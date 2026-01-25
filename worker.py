import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from sqlmodel import Session, select
from database import engine, Regra, LogExecucao

class BotWorker:
    def __init__(self, db_bot):
        self.bot_id = db_bot.id
        self.nome = db_bot.nome
        self.api_id = db_bot.api_id
        self.api_hash = db_bot.api_hash
        self.session_string = db_bot.session_string
        self.client = None
        self.handlers_ativos = [] # Lista para rastrear as regras ativas
        self.hash_regras_atual = "" # Para saber se algo mudou

    async def carregar_regras(self):
        with Session(engine) as session:
            statement = select(Regra).where(Regra.bot_id == self.bot_id, Regra.ativo == True)
            regras = session.exec(statement).all()
            # Convertemos para dicionários
            return [{"id": r.id, "origem": r.origem, "destino": r.destino, "nome": r.nome} for r in regras]

    def processar_chat_id(self, chat_id):
        try:
            return int(chat_id)
        except ValueError:
            return chat_id

    def registrar_log(self, origem, destino, status, mensagem):
        try:
            with Session(engine) as session:
                novo_log = LogExecucao(
                    bot_id=self.bot_id,
                    bot_nome=self.nome,
                    origem=str(origem),
                    destino=str(destino),
                    status=status,
                    mensagem=mensagem
                )
                session.add(novo_log)
                session.commit()
        except Exception as e:
            print(f"Erro ao salvar log: {e}")

    async def aplicar_regras(self):
        """Limpa regras antigas e aplica as novas"""
        regras = await self.carregar_regras()
        
        # Cria um 'hash' simples para ver se as regras mudaram
        hash_novo = str(regras)
        if hash_novo == self.hash_regras_atual:
            return # Nada mudou, não faz nada
            
        print(f"🔄 [{self.nome}] Detectada alteração nas regras. Recarregando...")
        
        # 1. Remover handlers antigos (Limpeza)
        for handler in self.handlers_ativos:
            self.client.remove_event_handler(handler)
        self.handlers_ativos.clear()
        
        # 2. Aplicar novas regras
        if not regras:
            print(f"⚠️ [{self.nome}] Nenhuma regra ativa no momento.")
        
        for regra in regras:
            origem = self.processar_chat_id(regra['origem'])
            destino = self.processar_chat_id(regra['destino'])
            
            # Função Handler (O 'ouvido' do bot)
            async def handler(event, d=destino, o=origem, r_nome=regra['nome']):
                try:
                    await self.client.send_message(d, event.message)
                    msg = f"Regra '{r_nome}': Msg ID {event.id} repassada"
                    print(f"   🚀 [{self.nome}] {msg}")
                    self.registrar_log(o, d, "Sucesso", msg)
                except Exception as e:
                    print(f"   ❌ Erro: {e}")
                    self.registrar_log(o, d, "Erro", str(e))
            
            # Adiciona o evento ao cliente do Telegram
            # (NewMessage filtra apenas mensagens novas naquele chat)
            self.client.add_event_handler(handler, events.NewMessage(chats=origem))
            
            # Guarda o handler na lista para poder remover depois se precisar
            self.handlers_ativos.append(handler)
            print(f"   ↳ ➕ Regra Adicionada: {regra['nome']} ({origem} -> {destino})")

        self.hash_regras_atual = hash_novo
        print(f"✅ [{self.nome}] Regras atualizadas com sucesso!")

    async def monitorar_regras_loop(self):
        """Tarefa de fundo que checa o banco a cada 10 segundos"""
        while True:
            try:
                await self.aplicar_regras()
            except Exception as e:
                print(f"❌ Erro no Hot Reload: {e}")
            
            await asyncio.sleep(10) # Espera 10 segundos antes de checar de novo

    async def start(self):
        print(f"🔄 Iniciando {self.nome}...")
        try:
            self.client = TelegramClient(StringSession(self.session_string), self.api_id, self.api_hash)
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                print(f"❌ {self.nome} não autorizado!")
                return

            me = await self.client.get_me()
            print(f"✅ {self.nome} conectado (@{me.username})")

            # Inicia o monitor de regras em PARALELO
            # create_task joga isso para rodar no fundo sem travar o bot
            asyncio.create_task(self.monitorar_regras_loop())

            # Mantém o bot rodando (Bloqueia aqui)
            await self.client.run_until_disconnected()
            
        except Exception as e:
            print(f"❌ Erro crítico em {self.nome}: {e}")

    async def stop(self):
        if self.client:
            await self.client.disconnect()