from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bot import Bot
from app.schemas.bot import BotCreate, BotUpdate


class BotService:
    """Service para operações de CRUD e lógica de negócio de Bots."""

    @staticmethod
    def get_by_id(db: Session, bot_id: int, owner_id: int) -> Bot | None:
        stmt = select(Bot).where(Bot.id == bot_id, Bot.owner_id == owner_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_all(db: Session, owner_id: int) -> list[Bot]:
        stmt = select(Bot).where(Bot.owner_id == owner_id).order_by(Bot.id)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def create(db: Session, data: BotCreate, owner_id: int) -> Bot:
        bot = Bot(**data.model_dump(), owner_id=owner_id)
        db.add(bot)
        db.commit()
        db.refresh(bot)
        return bot

    @staticmethod
    def update(db: Session, bot: Bot, data: BotUpdate) -> Bot:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(bot, field, value)
        db.commit()
        db.refresh(bot)
        return bot

    @staticmethod
    def toggle_active(db: Session, bot: Bot) -> Bot:
        bot.ativo = not bot.ativo
        db.commit()
        db.refresh(bot)
        return bot

    @staticmethod
    def delete(db: Session, bot: Bot) -> None:
        db.delete(bot)
        db.commit()

    @staticmethod
    def count_by_owner(db: Session, owner_id: int) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(Bot).where(Bot.owner_id == owner_id)
        return db.execute(stmt).scalar_one()
