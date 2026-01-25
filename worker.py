import asyncio
import random
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from sqlmodel import Session, select
from database import engine, Regra, LogExecucao, Agendamento # Importamos Agendamento
import re

class BotWorker:
    def __init__(self, db_bot):
        self.bot_id = db_bot.id
        self.nome = db_bot.nome
        self.api_id = db_bot.api_id
        self.api_hash = db_bot.api_hash
        self.session_string = db_bot.session_string
        self.client = None
        
        # Fila de Envio (Anti-Flood)
        self.fila_envio = asyncio.Queue()
        
        self.handlers_ativos = [] 
        self.hash_regras_atual = "" 

    # --- FUNÇÕES AUXILIARES ---
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

    # --- TAREFA 1: CONSUMIDOR DA FILA (ANTI-FLOOD) ---
    async def loop_processamento_fila(self):
        print(f"   🐢 [{self.nome}] Fila de envio iniciada...")
        while True:
            item = await self.fila_envio.get()
            destino, mensagem_original, regra_nome, log_origem = item
            
            try:
                await self.client.send_message(destino, mensagem_original)
                
                msg_log = f"'{regra_nome}': Enviada (Restam {self.fila_envio.qsize()})"
                print(f"   🚀 [{self.nome}] {msg_log}")
                self.registrar_log(log_origem, destino, "Sucesso", msg_log)
                
                # Pausa estratégica (2 a 5 segundos)
                tempo_espera = random.uniform(2.0, 5.0)
                await asyncio.sleep(tempo_espera)
                
            except Exception as e:
                print(f"   ❌ Erro no envio: {e}")
                self.registrar_log(log_origem, destino, "Erro", str(e))
            finally:
                self.fila_envio.task_done()

    # --- TAREFA 2: MONITOR DE REGRAS (HOT RELOAD) ---
    async def carregar_regras(self):
        with Session(engine) as session:
            statement = select(Regra).where(Regra.bot_id == self.bot_id, Regra.ativo == True)
            regras = session.exec(statement).all()
            return [{"id": r.id, "origem": r.origem, "destino": r.destino, "nome": r.nome, 
                     "filtro": r.filtro, "substituto": r.substituto} for r in regras]

    async def aplicar_regras(self):
        regras = await self.carregar_regras()
        hash_novo = str(regras)
        
        if hash_novo == self.hash_regras_atual:
            return 
            
        print(f"🔄 [{self.nome}] Atualizando regras de repasse...")
        for handler in self.handlers_ativos:
            self.client.remove_event_handler(handler)
        self.handlers_ativos.clear()
        
        for regra in regras:
            origem = self.processar_chat_id(regra['origem'])
            destino = self.processar_chat_id(regra['destino'])
            
            async def handler(event, d=destino, o=origem, r_nome=regra['nome'], 
                            r_filtro=regra['filtro'], r_sub=regra['substituto']):
                try:
                    mensagem_final = event.message
                    if event.message.text and r_filtro and r_sub:
                        mensagem_final.text = re.sub(r_filtro, r_sub, event.message.text, flags=re.IGNORECASE)
                    
                    print(f"   📥 [{self.nome}] Recebido de {o}. Adicionando à fila...")
                    await self.fila_envio.put( (d, mensagem_final, r_nome, o) )
                except Exception as e:
                    print(f"   ❌ Erro handler: {e}")

            self.client.add_event_handler(handler, events.NewMessage(chats=origem))
            self.handlers_ativos.append(handler)

        self.hash_regras_atual = hash_novo

    async def monitorar_regras_loop(self):
        while True:
            try:
                await self.aplicar_regras()
            except Exception as e:
                print(f"❌ Erro Hot Reload: {e}")
            await asyncio.sleep(10)

    # --- TAREFA 3: AGENDADOR (NOVO!) ---
    async def verificar_agendamentos_loop(self):
        print(f"   ⏰ [{self.nome}] Agendador ativado.")
        while True:
            try:
                # Pega a hora atual (ex: "14:30")
                agora = datetime.now().strftime("%H:%M")
                segundos_para_proximo_minuto = 60 - datetime.now().second
                
                with Session(engine) as session:
                    # 1. Buscamos TODOS os agendamentos ativos deste bot
                    # (Não filtramos mais por horário no SQL, pois agora é uma lista complexa de texto)
                    agendamentos = session.exec(
                        select(Agendamento).where(
                            Agendamento.bot_id == self.bot_id,
                            Agendamento.ativo == True
                        )
                    ).all()

                    for ag in agendamentos:
                        # 2. TRUQUE DOS MÚLTIPLOS HORÁRIOS:
                        # Transformamos "12:00, 18:00" em ["12:00", "18:00"] e limpamos espaços
                        lista_horarios = [h.strip() for h in ag.horario.split(',')]
                        
                        # Se o horário de "agora" estiver na lista, executa!
                        if agora in lista_horarios:
                            
                            print(f"   ⏰ Executando agendamento múltiplo: {ag.nome} ({agora})")
                            origem_id = self.processar_chat_id(ag.origem)
                            destino_id = self.processar_chat_id(ag.destino)
                            
                            try:
                                msg = await self.client.get_messages(origem_id, ids=ag.msg_id_atual)
                                
                                if msg:
                                    await self.fila_envio.put((destino_id, msg, f"Agenda: {ag.nome}", ag.origem))
                                    
                                    if ag.tipo_envio == "sequencial":
                                        ag.msg_id_atual += 1
                                        session.add(ag)
                                        session.commit()
                                        print(f"      ➥ Próximo ID atualizado para: {ag.msg_id_atual}")
                                else:
                                    print(f"      ⚠️ Msg ID {ag.msg_id_atual} não encontrada.")
                                    self.registrar_log(ag.origem, ag.destino, "Erro", f"Agenda {ag.nome}: Msg {ag.msg_id_atual} sumiu")
                            
                            except Exception as e:
                                print(f"      ❌ Falha ao processar: {e}")

            except Exception as e:
                print(f"❌ Erro Crítico Agendador: {e}")
            
            await asyncio.sleep(segundos_para_proximo_minuto)

    # --- START PRINCIPAL ---
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

            # Inicia os 3 motores em paralelo
            asyncio.create_task(self.monitorar_regras_loop())     # Regras
            asyncio.create_task(self.loop_processamento_fila())   # Fila
            asyncio.create_task(self.verificar_agendamentos_loop()) # Agendamento (NOVO)

            await self.client.run_until_disconnected()
            
        except Exception as e:
            print(f"❌ Erro crítico em {self.nome}: {e}")

    async def stop(self):
        if self.client:
            await self.client.disconnect()