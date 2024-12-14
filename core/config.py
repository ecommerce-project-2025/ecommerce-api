import logging
import logging.config
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig
from pydantic import DirectoryPath, Field, ValidationError
from pydantic_settings import BaseSettings
from uvicorn.config import LOGGING_CONFIG

load_dotenv()  

logger = logging.getLogger(__name__)

class AppSettings(BaseSettings):
    api_version: str = Field(..., env="API_VERSION")
    debug_mode: bool = Field(..., env="DEBUG_MODE")
    
    class Config:
        env_file = ".env"
        extra = "allow"

class DatabaseSettings(BaseSettings):
    
    database_url: str = Field(..., env="DATABASE_URL")
    initial_admin_email: str = Field(..., env="INITIAL_ADMIN_EMAIL")
    initial_admin_username: str = Field(..., env="INITIAL_ADMIN_USERNAME")
    initial_admin_password: str = Field(..., env="INITIAL_ADMIN_PASSWORD")
    
    class Config:
        env_file = ".env"
        extra = "allow"

class MailSettings(BaseSettings):
    mail_username: str = Field(..., env="MAIL_USERNAME")
    mail_password: str = Field(..., env="MAIL_PASSWORD")
    mail_from: str = Field(..., env="MAIL_FROM")
    mail_port: int = Field(..., env="MAIL_PORT")
    mail_server: str = Field(..., env="MAIL_SERVER")
    mail_starttls: bool = Field(..., env="MAIL_STARTTLS")
    mail_ssl_tls: bool = Field(..., env="MAIL_SSL_TLS")
    mail_template_folder: DirectoryPath = Field("./templates", env="MAIL_TEMPLATE_FOLDER")
    
    class Config:
        env_file = ".env"
        extra = "allow"

class SecuritySettings(BaseSettings):
    origin_url: str = Field(..., env="ORIGIN_URL")
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(..., env="ALGORITHM")
    access_token_expire_minutes: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    class Config:
        env_file = ".env"
        extra = "allow"

try:
    appSettings = AppSettings()
    dbSettings = DatabaseSettings()
    mailSettings = MailSettings()
    securitySettings = SecuritySettings()
except ValidationError as e:
    logger.error("Error loading settings: %s", e.json())
    raise

# Configuración de FastAPI-Mail
def getEmailConfig():
    return ConnectionConfig(
        MAIL_USERNAME=mailSettings.mail_username,
        MAIL_PASSWORD=mailSettings.mail_password,
        MAIL_PORT=mailSettings.mail_port,
        MAIL_SERVER=mailSettings.mail_server,
        MAIL_STARTTLS=mailSettings.mail_starttls,
        MAIL_SSL_TLS=mailSettings.mail_ssl_tls,
        MAIL_FROM=mailSettings.mail_from,
        MAIL_FROM_NAME="HumanSync",
        TEMPLATE_FOLDER=mailSettings.mail_template_folder,
        USE_CREDENTIALS=True,
    )

LOGGING_CONFIG["formatters"]["default"] = {
    "()": "uvicorn.logging.DefaultFormatter",
    "format": "%(levelprefix)s %(asctime)s - %(name)s - %(message)s",
}

LOGGING_CONFIG["formatters"]["access"] = LOGGING_CONFIG["formatters"]["default"]

LOGGING_CONFIG["loggers"][""] = {
    "level": "INFO",
    "handlers": ["default"],
    "propagate": True,
}

# logger.debug("Este es un mensaje DEBUG para depuración")
# logger.info("Este es un mensaje INFO para información general")
# logger.warning("Este es un mensaje WARNING para advertencias")
# logger.error("Este es un mensaje ERROR para errores")
# logger.critical("Este es un mensaje CRITICAL para errores críticos")


