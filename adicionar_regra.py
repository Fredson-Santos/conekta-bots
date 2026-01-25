from sqlmodel import Session, select
from database import engine, Bot, Regra

def main():
    print("--- ADICIONAR NOVA REGRA DE ENCAMINHAMENTO ---")
    
    with Session(engine) as session:
        # 1. Listar Bots disponíveis para o usuário escolher
        bots = session.exec(select(Bot)).all()
        
        if not bots:
            print("❌ Nenhum bot cadastrado! Rode 'adicionar_bot.py' primeiro.")
            return

        print("\n🤖 Bots Disponíveis:")
        for bot in bots:
            print(f"[{bot.id}] {bot.nome} ({bot.tipo})")
        
        # 2. Escolher o Bot
        bot_id = int(input("\nDigite o ID do Bot que vai executar essa regra: "))
        bot_selecionado = session.get(Bot, bot_id)
        
        if not bot_selecionado:
            print("❌ Bot não encontrado.")
            return

        # 3. Definir a Regra
        print(f"\nConfigurando regra para: {bot_selecionado.nome}")
        nome_regra = input("Nome da Regra (ex: Repasse VIP): ")
        origem = input("Canal de Origem (Username ou ID): ")
        destino = input("Canal de Destino (Username ou ID): ")
        
        nova_regra = Regra(
            nome=nome_regra,
            origem=origem,
            destino=destino,
            bot_id=bot_id,
            ativo=True
        )
        
        session.add(nova_regra)
        session.commit()
        print("✅ Regra salva com sucesso!")

if __name__ == "__main__":
    main()