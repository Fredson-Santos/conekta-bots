from pydantic import BaseModel, ConfigDict, Field


class ConfiguracaoCreate(BaseModel):
    shopee_app_id: str | None = Field(default=None, max_length=100)
    shopee_app_secret: str | None = Field(default=None, max_length=200)


class ConfiguracaoUpdate(BaseModel):
    shopee_app_id: str | None = Field(default=None, max_length=100)
    shopee_app_secret: str | None = Field(default=None, max_length=200)


class ConfiguracaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shopee_app_id: str | None = None
    shopee_app_secret: str | None = None
    owner_id: int
