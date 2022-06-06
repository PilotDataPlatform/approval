# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
from functools import lru_cache
from typing import Any, Dict, Optional

from common import VaultClient
from pydantic import BaseSettings, Extra


class VaultConfig(BaseSettings):
    """Store vault related configuration."""

    APP_NAME: str = 'service_approval'
    CONFIG_CENTER_ENABLED: bool = False

    VAULT_URL: Optional[str]
    VAULT_CRT: Optional[str]
    VAULT_TOKEN: Optional[str]

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    config = VaultConfig()

    if not config.CONFIG_CENTER_ENABLED:
        return {}

    client = VaultClient(config.VAULT_URL, config.VAULT_CRT, config.VAULT_TOKEN)
    return client.get_from_vault(config.APP_NAME)


class Settings(BaseSettings):
    env: str = os.environ.get('env')
    version: str = '0.1.0'

    port: int = 8000
    host: str = '0.0.0.0'

    AUTH_SERVICE: str
    DATA_OPS_UTIL: str
    EMAIL_SERVICE: str
    METADATA_SERVICE: str
    PROJECT_SERVICE: str

    RDS_SCHEMA_DEFAULT: str
    RDS_DB_URI: str

    EMAIL_SUPPORT: str = 'jzhang@indocresearch.org'

    CORE_ZONE_LABEL: str
    GREEN_ZONE_LABEL: str

    REDIS_DB: str
    REDIS_HOST: str
    REDIS_PASSWORD: str
    REDIS_PORT: str

    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

        self.AUTH_SERVICE = self.AUTH_SERVICE + '/v1/'
        self.DATA_UTILITY_SERVICE = self.DATA_OPS_UTIL + '/v1/'
        self.EMAIL_SERVICE = self.EMAIL_SERVICE + '/v1/email/'
        self.META_SERVICE = self.METADATA_SERVICE + '/v1/'
        self.REDIS_DB_URI = (
            f'redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:'
            f'{self.REDIS_PORT}')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return env_settings, load_vault_settings, init_settings, file_secret_settings


@lru_cache(1)
def get_settings():
    settings = Settings()
    return settings


ConfigClass = get_settings()
