"""Testes unitários para BotService."""

from app.models.bot import Bot
from app.schemas.bot import BotCreate, BotUpdate
from app.services.bot_service import BotService


class TestBotService:
    def _create_bot(self, db, owner_id=1, nome="Test Bot"):
        data = BotCreate(nome=nome, api_id="12345", api_hash="abc123", tipo="user")
        return BotService.create(db, data, owner_id)

    def test_create_bot(self, db, test_user):
        bot = self._create_bot(db, test_user.id)
        assert bot.id is not None
        assert bot.nome == "Test Bot"
        assert bot.owner_id == test_user.id
        assert bot.ativo is True

    def test_get_by_id(self, db, test_user):
        bot = self._create_bot(db, test_user.id)
        found = BotService.get_by_id(db, bot.id, test_user.id)
        assert found is not None
        assert found.id == bot.id

    def test_get_by_id_wrong_owner(self, db, test_user):
        bot = self._create_bot(db, test_user.id)
        found = BotService.get_by_id(db, bot.id, 999)
        assert found is None

    def test_get_all(self, db, test_user):
        self._create_bot(db, test_user.id, "Bot 1")
        self._create_bot(db, test_user.id, "Bot 2")
        bots = BotService.get_all(db, test_user.id)
        assert len(bots) == 2

    def test_update(self, db, test_user):
        bot = self._create_bot(db, test_user.id)
        update_data = BotUpdate(nome="Updated Bot")
        updated = BotService.update(db, bot, update_data)
        assert updated.nome == "Updated Bot"

    def test_toggle_active(self, db, test_user):
        bot = self._create_bot(db, test_user.id)
        assert bot.ativo is True
        toggled = BotService.toggle_active(db, bot)
        assert toggled.ativo is False

    def test_delete(self, db, test_user):
        bot = self._create_bot(db, test_user.id)
        BotService.delete(db, bot)
        found = BotService.get_by_id(db, bot.id, test_user.id)
        assert found is None

    def test_count_by_owner(self, db, test_user):
        self._create_bot(db, test_user.id, "Bot A")
        self._create_bot(db, test_user.id, "Bot B")
        count = BotService.count_by_owner(db, test_user.id)
        assert count == 2

    def test_multi_tenancy(self, db, test_user):
        """Verifica que owner_id 1 não vê bots do owner_id 999."""
        self._create_bot(db, test_user.id, "Meu Bot")
        self._create_bot(db, 999, "Bot Alheio")
        my_bots = BotService.get_all(db, test_user.id)
        assert len(my_bots) == 1
        assert my_bots[0].nome == "Meu Bot"
