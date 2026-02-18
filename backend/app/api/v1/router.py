"""Router principal da API v1 — registra todos os sub-routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import analytics, auth, bots, rules, schedules, settings

router = APIRouter()

router.include_router(auth.router)
router.include_router(bots.router)
router.include_router(rules.router)
router.include_router(schedules.router)
router.include_router(analytics.router)
router.include_router(settings.router)
