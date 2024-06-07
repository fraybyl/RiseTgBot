from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    
    bot_token: SecretStr
    admins: list[int] 
    SUPPORT: SecretStr    
    SQLALCHEMY_URL: str    
    PAYMENTS_TOKEN: str
    USE_PROXY_FROM_FILE: bool = False
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
