import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from sqlmodel import Session, select
from database import Bot, engine

#Funcao para salvar no banco
def salvar_bot(dados_bot):
    with Session(engine) as session:
        #Verifica se o bot ja existe
        query = select(Bot)
        if dados_bot.get("phone"):
            query = query.where(Bot.phone == dados_bot["phone"])
        else:
            query = query.where(Bot.bot_token == dados_bot["bot_token"])
        
        bot_existente = session.exec(query).first()

        if bot_existente:
            print(f"⚠️ Atualizando bot existente: {bot_existente.nome}")
            for key, value in dados_bot.items():
                setattr(bot_existente, key, value)
            session.add(bot_existente)
        else:
            novo_bot = Bot(**dados_bot)
            session.add(novo_bot)

        session.commit()
        print(f"✅ {dados_bot['nome']} salvo com sucesso!")

async def main():
    print("--- ADICIONAR NOVO BOT ---")
    print("1. Userbot (Conta Pessoal - Requer Telefone)")
    print("2. Bot API (BotFather - Requer Token)")
    escolha = input("Escolha o tipo (1 ou 2): ").strip()

    nome = input("Dê um nome para este bot: ")
    api_id = input("API_ID: ")
    api_hash = input("API_HASH: ")

    client = None
    dados_para_salvar = {
        "nome": nome,
        "api_id": api_id,
        "api_hash": api_hash,
        "ativo": True
    }

    try:
        if escolha == "1":
            phone = input("Telefone (+55...): ")
            print(f"🔄 Conectando como Usuário ({phone})...")
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.start(phone)
            
            dados_para_salvar["tipo"] = "user"
            dados_para_salvar["phone"] = phone
            dados_para_salvar["session_string"] = client.session.save()

        elif escolha == "2":
            token = input("Bot Token (do BotFather): ")
            print(f"🔄 Verificando Token...")
            # Bots também precisam de sessão no Telethon para funcionar de forma persistente
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.start(bot_token=token)
            
            dados_para_salvar["tipo"] = "bot"
            dados_para_salvar["bot_token"] = token
            dados_para_salvar["session_string"] = client.session.save()

        else:
            print("❌ Opção inválida!")
            return

        print("🔓 Login realizado com sucesso!")
        salvar_bot(dados_para_salvar)

    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
    finally:
        if client:
            await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
        