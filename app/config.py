import os
import requests
from requests.models import HTTPError
from pydantic import BaseSettings, Extra
from typing import Dict, Set, List, Any
from functools import lru_cache
from common import VaultClient

SRV_NAMESPACE = os.environ.get("APP_NAME", "service_approval")
CONFIG_CENTER_ENABLED = os.environ.get("CONFIG_CENTER_ENABLED", "false")

def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == "false":
        return {}
    else:
        return vault_factory()


def vault_factory() -> dict:
    vc = VaultClient(os.getenv("VAULT_URL"), os.getenv("VAULT_CRT"), os.getenv("VAULT_TOKEN"))
    return vc.get_from_vault(SRV_NAMESPACE)


class Settings(BaseSettings):
    env: str = os.environ.get('env')
    version: str = "0.1.0"

    port: int = 8000
    host: str = "0.0.0.0"

    NEO4J_SERVICE: str
    DATA_OPS_UTIL: str
    EMAIL_SERVICE: str
    UTILITY_SERVICE: str

    RDS_HOST: str
    RDS_PORT: str
    RDS_DBNAME: str
    RDS_USER: str
    RDS_PWD: str
    RDS_SCHEMA_DEFAULT: str

    EMAIL_SUPPORT: str = "jzhang@indocresearch.org"

    CORE_ZONE_LABEL: str
    GREENROOM_ZONE_LABEL: str

    def modify_values(self, settings):
        NEO4J_HOST = settings.NEO4J_SERVICE
        settings.NEO4J_SERVICE = NEO4J_HOST+ "/v1/neo4j/"
        settings.NEO4J_SERVICE_V2 = NEO4J_HOST + "/v2/neo4j/"
        settings.DATA_UTILITY_SERVICE = settings.DATA_OPS_UTIL + "/v1/"
        settings.EMAIL_SERVICE = settings.EMAIL_SERVICE + "/v1/email"
        settings.UTILITY_SERVICE = settings.UTILITY_SERVICE + "/v1/"
        settings.EMAIL_SUPPORT = settings.EMAIL_SUPPORT
        settings.OPS_DB_URI = f"postgresql://{settings.RDS_USER}:{settings.RDS_PWD}@{settings.RDS_HOST}/{settings.RDS_DBNAME}"
        return settings

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                load_vault_settings,
                env_settings,
                init_settings,
                file_secret_settings,
            )


@lru_cache(1)
def get_settings():
    settings = Settings()
    settings.modify_values(settings)
    return settings

ConfigClass = get_settings()
