from sqlmodel import Session, select
from database import engine, Bot

def restaurar_dados():
    # Dados do Bot (Edite a session_string com a string REAL gerada pelo Telethon)
    bot_data = Bot(
        nome="TesteBot",
        api_id="21993165",
        api_hash="2017110c1ffe36db9adc12f808cc09bc",
        phone="5511965396092",
        bot_token=None,
        tipo="user",
        # IMPORTANTE: Esta string abaixo deve ser a sessão válida longa gerada pelo Telethon.
        # Se você usar o api_hash aqui, o worker.py vai falhar ao conectar.
        session_string="1AZWarzQBu1PL8Vloo0P6yhEYK9bTVL5h_YERjwj4vaAr0DeR1tehhHScz22jROc5AWqDU_9qclXxfiKAmR9gxL5poLVICbAvoyE9iZnoZN7IpqfH3jFno2a5gDQe97-IXA6HlH0IYGt0Xc43UG3IePFT8udJLVuUQ3n2rJZ0N8OB3CMmPc5FQGlKZQDlHWz6A19z4EYYNRBu9M6jJ3qIW6_usC03RYCeO_7YXb22BFkJTf1SWRVIgix_tSbaaalILYMGz3OmW51q4iVmgq2TIMtbom4MejJRiz6nTe1FTpH0xj41fr0NULoB098pVY2ybS5tyLi7dLRzHGlXJOcU0B70Wz3qH5c=", 
        ativo=True
    )

    with Session(engine) as session:
        # Verifica se já existe para não duplicar
        existente = session.exec(select(Bot).where(Bot.api_id == bot_data.api_id)).first()
        
        if existente:
            print(f"⚠️ O bot '{existente.nome}' já existe no banco.")
        else:
            session.add(bot_data)
            session.commit()
            print("✅ Bot 'TesteBot' inserido com sucesso!")

if __name__ == "__main__":
    restaurar_dados()