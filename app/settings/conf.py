import logging
import os
from uuid import UUID

from pydantic import BaseConfig

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)


class Config(BaseConfig):
    title: str = os.environ.get("TITLE")
    version: str = "1.0.0"
    description: str = os.environ.get("DESCRIPTION")
    api_prefix: str = os.environ.get("API_PREFIX")
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    debug: bool = os.environ.get("DEBUG")
    offer_ms_api_url: str = os.environ.get("OFFER_MS_URL")
    refresh_token: str = os.environ.get("OFFER_REFRESH_TOKEN")
    postgres_user: str = os.environ.get("POSTGRES_USER")
    postgres_password: str = os.environ.get("POSTGRES_PASSWORD")
    postgres_server: str = os.environ.get("POSTGRES_SERVER")
    postgres_port: int = int(os.environ.get("POSTGRES_PORT"))
    postgres_db: str = os.environ.get("POSTGRES_DB")
    postgres_db_tests: str = os.environ.get("POSTGRES_DB_TESTS")
    db_echo_log: bool = True if os.environ.get("DEBUG") == "True" else False
    access_token: UUID = os.environ.get("ACCESS_TOKEN")
    offer_job_period: int = int(os.environ.get("REFRESH_OFFER_JOB"))
    jwt_secret: str = os.environ.get("JWT_SECRET")
    jwt_algorithm: str = os.environ.get("JWT_ALGORITHM")
    jwt_expire: int = int(os.environ.get("JWT_EXPIRE"))

    @property
    def sync_database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"

    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"


settings = Config()
